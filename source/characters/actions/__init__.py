# actions.py

import random
from collections import defaultdict
import csv
from dataclasses import dataclass
from system import SystemHandler
from movement import MovementHandler
from combat import CombatHandler
from item import ItemHandler
from environment import EnvironmentHandler

from settings import *
from data import Action, ActionResult, ITEMS, ItemType, ItemFunction, BLOCKS, BlockType, SkillType


@dataclass
class ZombieWeapon:
    name: str
    attack: int
    damage: int

    @classmethod
    def choose(cls):
        """Randomly select hands or teeth and return a ZombieWeapon instance."""
        attack_type, stats = random.choice(list(ZOMBIE_ATTACKS.items()))
        return cls(name=attack_type, attack=stats["attack"], damage=stats["damage"])


class ActionExecutor:
    """Handles executing actions for both player and AI characters."""
    def __init__(self, game, actor):
        self.game = game
        self.actor = actor  # Define the acting character
        self.handlers = {
            Action.QUIT: SystemHandler.quit,
            Action.PAUSE: SystemHandler.pause,
            Action.OPTIONS: SystemHandler.options,
            Action.NEW_GAME: SystemHandler.new_game,
            Action.NEWGAME_MENU: SystemHandler.newgame_menu,
            Action.SAVE: SystemHandler.save,
            Action.SAVE_MENU: SystemHandler.save_menu,
            Action.LOAD: SystemHandler.load,
            Action.LOAD_MENU: SystemHandler.load_menu,
            Action.SKILLS_MENU: SystemHandler.skills_menu,
            Action.BACK: SystemHandler.back,
            Action.ZOOM_IN: SystemHandler.zoom_in,
            Action.ZOOM_OUT: SystemHandler.zoom_out,

            Action.ENTER: MovementHandler.enter,
            Action.LEAVE: MovementHandler.leave,
            Action.MOVE: MovementHandler.move,
            Action.MOVE_UP: MovementHandler.move_up,
            Action.MOVE_DOWN: MovementHandler.move_down,
            Action.MOVE_LEFT: MovementHandler.move_left,
            Action.MOVE_RIGHT: MovementHandler.move_right,
            Action.MOVE_UPLEFT: MovementHandler.move_upleft,
            Action.MOVE_UPRIGHT: MovementHandler.move_upright,
            Action.MOVE_DOWNLEFT: MovementHandler.move_downleft,
            Action.MOVE_DOWNRIGHT: MovementHandler.move_downright,
            Action.STAND: MovementHandler.stand,
            Action.WANDER: MovementHandler.wander,
            Action.PURSUE: MovementHandler.pursue,

            Action.ATTACK: CombatHandler.attack,
            Action.HEAL: CombatHandler.heal,
            Action.SPEAK: CombatHandler.speak,
            Action.EXTRACT_DNA: CombatHandler.extract_dna,
            Action.REVIVIFY: CombatHandler.revivify,

            Action.USE: ItemHandler.use,
            Action.DROP: ItemHandler.drop,
            Action.EQUIP: ItemHandler.equip,
            Action.DROP: ItemHandler.drop,

            Action.BARRICADE: EnvironmentHandler.barricade,
            Action.DECADE: EnvironmentHandler.decade,
            Action.OPEN_DOORS: EnvironmentHandler.open_doors,
            Action.CLOSE_DOORS: EnvironmentHandler.close_doors,
            Action.SEARCH: EnvironmentHandler.search,
            Action.REPAIR_BUILDING: EnvironmentHandler.repair_building,
            Action.RANSACK: EnvironmentHandler.ransack,
            Action.DUMP: CombatHandler.dump,
        }

    def execute(self, action, target=None):
        """Execute AI and player actions."""
        # Fetch block at the actor's location
        self.x, self.y = self.actor.location
        self.block = self.game.state.city.block(x, y)

        self.weapon = self.actor.weapon
        self.player = self.game.state.player 
        self.screen_transition = self.game.game_ui.screen_transition
        self.action_progress = self.game.game_ui.action_progress

        if self.actor == self.player:
            self.is_player = True
        else:
            self.is_player = False

        if action in self.handlers:
            return self.handlers[action](self, target)
        print(f"Unknown action: {action}  Target: {target}")




        # Inventory actions
        elif action == Action.EQUIP:
            return self.equip(target)

        elif action == Action.UNEQUIP:
            return self.unequip(target)

        elif action == Action.USE:
            return self.use(target)
     
        elif action == Action.DROP:
            return self.drop(target)

        else:
            return ActionResult(False, "No action available.")

    def attack(self, target, weapon=None):
        """Execute an attack depending on the attacker's state."""
        if self.actor.is_human:
            return self._human_attack(target, weapon)
        else:
            return self._zombie_attack(target)

    def _human_attack(self, target, weapon):
        if weapon:
            properties = ITEMS[weapon.type]

            
            if properties.item_function == ItemFunction.FIREARM and weapon.loaded_ammo == 0:
                return ActionResult(False, "Your firearm is out of ammo.")
            elif properties.item_function == ItemFunction.SCIENCE:
                result = self._science_attack(target, weapon)
                return result

            # Base attack success rate
            attack_chance = properties.attack

            # Apply skill bonuses
            if properties.item_function == ItemFunction.FIREARM:
                if SkillType.BASIC_FIREARMS_TRAINING in self.actor.human_skills:
                    attack_chance += 25
                if weapon.type == ItemType.PISTOL:
                    if SkillType.PISTOL_TRAINING in self.actor.human_skills:
                        attack_chance += 25
                    if SkillType.ADV_PISTOL_TRAINING in self.actor.human_skills:
                        attack_chance += 10
                if weapon.type == ItemType.SHOTGUN:
                    if SkillType.SHOTGUN_TRAINING in self.actor.human_skills:
                        attack_chance += 25
                    if SkillType.ADV_SHOTGUN_TRAINING in self.actor.human_skills:
                        attack_chance += 10
            if properties.item_function == ItemFunction.MELEE:
                if SkillType.HAND_TO_HAND in self.actor.human_skills:
                    attack_chance += 15
                if weapon.type == ItemType.KNIFE and SkillType.KNIFE_COMBAT in self.actor.human_skills:
                        attack_chance += 15
                if weapon.type == ItemType.FIRE_AXE and SkillType.AXE_PROFICIENCY in self.actor.human_skills:
                        attack_chance += 15
            
            roll = random.randint(1, 100)
            attack_success = roll <= attack_chance
            self.actor.ap -= 1

            if attack_success:
                # Resolve action result
                self._deplete_weapon(weapon, properties)
                target.take_damage(properties.damage)
                self.actor.gain_xp(properties.damage)
                if target.is_dead:
                    self.actor.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)


                if target.is_dead and SkillType.HEADSHOT in self.actor.human_skills:
                    target.permadeath = True
                    if self.actor.weapon:
                        message = f"You deal a headshot for {properties.damage} damage."
                        witness = f"{self.actor.current_name} deals a headshot against {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                    else:
                        message = f"You deal a headshot for {properties.damage} damage. Your weapon breaks!"
                        witness = f"{self.actor.current_name} deals a headshot against {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                else:
                    if self.actor.weapon:
                        message = f"Your attack hits for {properties.damage} damage."
                        witness = f"{self.actor.current_name} attacks {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                    else:
                        message = f"Your attack hits for {properties.damage} damage. Your weapon breaks!"
                        witness = f"{self.actor.current_name} attacks {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)                    
            else:
                return ActionResult(False, "Your attack misses.")

        else: # If no weapon equipped, punch the enemy.
            roll = random.randint(1, 20)
            attack_success = roll >= ATTACK_DIFFICULTY

            self.actor.ap -= 1

            if attack_success:
                target.take_damage(1)
                self.actor.gain_xp(1)
                if target.is_dead:
                    self.actor.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)

                return ActionResult(True, "You punch the enemy for 1 damage.", f"{self.actor.current_name} punches {target.current_name}.")
            else:
                return ActionResult(False, "Your attack misses.")

    def _zombie_attack(self, target):
        weapon = ZombieWeapon.choose()  # Get attack choice

        # Base attack success rate
        attack_chance = weapon.attack
        bonus_damage = 0

        # Apply skill bonuses
        if SkillType.VIGOUR_MORTIS in self.actor.zombie_skills:
            attack_chance += 10
        if weapon.name == 'hands' and SkillType.DEATH_GRIP in self.actor.zombie_skills:
            attack_chance += 15
            if SkillType.REND_FLESH in self.actor.zombie_skills:
                bonus_damage = 1
        if weapon.name == 'teeth' and SkillType.NECK_LURCH in self.actor.zombie_skills:
            attack_chance += 10

        roll = random.randint(1, 100)
        attack_success = roll <= attack_chance
        self.actor.ap -= 1

        if attack_success:
            target.take_damage(weapon.damage + bonus_damage)
            self.actor.gain_xp(weapon.damage + bonus_damage)
            if target.is_dead:
                self.actor.gain_xp(10)

            # Trigger NPC sprite animation if visible
            sprites = list(self.game.game_ui.description_panel.human_sprite_group)
            for sprite in sprites:
                if target == sprite.npc:
                    if target.is_dead:
                        sprite.set_action(2)
                    else:
                        sprite.set_action(3)

            message = f"You attack {target.current_name} with {weapon.name} for {weapon.damage + bonus_damage} damage."
            witness = f"{self.actor.current_name} attacks {target.current_name} with {weapon.name}."
            attacked = f"{self.actor.current_name} attacks you with {weapon.name} for {weapon.damage + bonus_damage} damage!"
            return ActionResult(True, message, witness, attacked)
        else:
            message = "Your attack misses."
            return ActionResult(False, message)

    def _science_attack(self, target, weapon):
        """Execute a science attack (extract DNA or inject syringe)."""
        if weapon.type == ItemType.DNA_EXTRACTOR:
            result = self._extract_DNA(target)
            return result
        elif weapon.type == ItemType.SYRINGE:
            result = self._inject_syringe(target)
            return result

    def _extract_DNA(self, target):
        return ActionResult(True, "You extract DNA from the zombie.")
    
    def _inject_syringe(self, target):
        if target.is_human:
            return ActionResult(False, "You cannot inject humans.")
        else:
            location = self.actor.location
            city = self.game.state.city
            block = city.block(location)

            if self.actor.inside:
                if block.lights_on:
                    return self._inject_success(target)
                else:
                    success = random.randint(0, 1) == 1
                    if success:
                        return self._inject_success(target)
                    else:
                        return ActionResult(False, "While priming the needle, you happen to lose track of the zombie in the dark.")
            else:
                return self._inject_success(target)

    def _inject_success(self, target):
        target.revivify()
        self.actor.ap -= 1

        # Trigger NPC sprite animation if visible
        sprites = list(self.game.game_ui.description_panel.human_sprite_group)
        for sprite in sprites:
            if target == sprite.npc:
                sprite.set_action(2)

        return ActionResult(True, "Following standard procedures, you press the syringe into the back of the zombie's neck and pump the glittering serum into its brain and spinal cord.")



    
    


