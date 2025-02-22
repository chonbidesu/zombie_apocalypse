# combat.py

import random

from actions import ActionCommand
from data import ItemType, ItemFunction, SkillType, BLOCKS, BlockType
from characters import ZombieWeapon


class Attack(ActionCommand):
    """Handles attacking enemies."""
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        if self.character.is_human:
            return self._human_attack(target)
        else:
            return self._zombie_attack(target)

    def _human_attack(self, target):
        weapon = self.character.equipped

        if weapon:           
            if weapon.item_function == ItemFunction.FIREARM and weapon.loaded_ammo == 0:
                self.message = "Your firearm is out of ammo."
                return
            elif weapon.item_function == ItemFunction.SCIENCE:
                self._science_attack(target, weapon)
                return

            # Base attack success rate
            attack_chance = weapon.attack

            # Apply skill bonuses
            if weapon.item_function == ItemFunction.FIREARM:
                if self.character.has_skill(SkillType.BASIC_FIREARMS_TRAINING):
                    attack_chance += 25
                if weapon.type == ItemType.PISTOL:
                    if self.character.has_skill(SkillType.PISTOL_TRAINING):
                        attack_chance += 25
                    if self.character.has_skill(SkillType.ADV_PISTOL_TRAINING):
                        attack_chance += 10
                if weapon.type == ItemType.SHOTGUN:
                    if self.character.has_skill(SkillType.SHOTGUN_TRAINING):
                        attack_chance += 25
                    if self.character.has_skill(SkillType.ADV_SHOTGUN_TRAINING):
                        attack_chance += 10
            if weapon.item_function == ItemFunction.MELEE:
                if self.character.has_skill(SkillType.HAND_TO_HAND):
                    attack_chance += 15
                if weapon.type == ItemType.KNIFE and self.character.has_skill(SkillType.KNIFE_COMBAT):
                        attack_chance += 15
                if weapon.type == ItemType.FIRE_AXE and self.character.has_skill(SkillType.AXE_PROFICIENCY):
                        attack_chance += 15
            
            roll = random.randint(1, 100)
            attack_success = roll <= attack_chance
            self.character.lose_ap(1)

            if attack_success:
                # Resolve action result
                self.character.deplete_weapon()
                target.take_damage(weapon.damage)
                self.character.gain_xp(weapon.damage)
                if target.is_dead:
                    self.character.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.character.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)


                if target.is_dead and self.character.has_skill(SkillType.HEADSHOT):
                    target.permadeath = True
                    if self.character.weapon:
                        self.message = f"You deal a headshot for {weapon.damage} damage."
                        self.witness = f"{self.character.current_name} deals a headshot against {target.current_name} with {weapon.description}."
                        self.success = True
                    else:
                        self.message = f"You deal a headshot for {weapon.damage} damage. Your weapon breaks!"
                        self.witness = f"{self.character.current_name} deals a headshot against {target.current_name} with {weapon.description}."
                        self.success = True
                else:
                    if self.character.weapon:
                        self.message = f"Your attack hits for {weapon.damage} damage."
                        self.witness = f"{self.character.current_name} attacks {target.current_name} with {weapon.description}."
                        self.success = True
                    else:
                        self.message = f"Your attack hits for {weapon.damage} damage. Your weapon breaks!"
                        self.witness = f"{self.character.current_name} attacks {target.current_name} with {weapon.description}."
                        self.success = True
            else:
                self.message = "Your attack misses."

        else: # If no weapon equipped, punch the enemy.
            attack_chance = 10

            if self.character.has_skill(SkillType.HAND_TO_HAND):
                attack_chance += 15

            roll = random.randint(1, 100)
            attack_success = roll <= attack_chance            

            self.character.lose_ap(1)

            if attack_success:
                target.take_damage(1)
                self.character.gain_xp(1)
                if target.is_dead:
                    self.character.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)

                self.success = True
                self.message = "You punch the enemy for 1 damage."
                self.witness = f"{self.character.current_name} punches {target.current_name}."

            else:
                self.message = "Your attack misses."
            

    def _zombie_attack(self, target):
        weapon = ZombieWeapon.choose()  # Get attack choice

        # Base attack success rate
        attack_chance = weapon.attack
        bonus_damage = 0

        # Apply skill bonuses
        if self.character.has_skill(SkillType.VIGOUR_MORTIS):
            attack_chance += 10
        if weapon.name == 'hands' and self.character.has_skill(SkillType.DEATH_GRIP):
            attack_chance += 15
            if self.character.has_skill(SkillType.REND_FLESH):
                bonus_damage = 1
        if weapon.name == 'teeth' and self.character.has_skill(SkillType.NECK_LURCH):
            attack_chance += 10

        roll = random.randint(1, 100)
        attack_success = roll <= attack_chance
        self.character.lose_ap(1)

        if attack_success:
            target.take_damage(weapon.damage + bonus_damage)
            self.character.gain_xp(weapon.damage + bonus_damage)
            if target.is_dead:
                self.character.gain_xp(10)

            # Trigger NPC sprite animation if visible
            sprites = list(self.game.game_ui.description_panel.human_sprite_group)
            for sprite in sprites:
                if target == sprite.npc:
                    if target.is_dead:
                        sprite.set_action(2)
                    else:
                        sprite.set_action(3)

            self.message = f"You attack {target.current_name} with {weapon.name} for {weapon.damage + bonus_damage} damage."
            self.witness = f"{self.character.current_name} attacks {target.current_name} with {weapon.name}."
            self.attacked = f"{self.character.current_name} attacks you with {weapon.name} for {weapon.damage + bonus_damage} damage!"
            self.success = True
        else:
            self.message = "Your attack misses."


class Heal(ActionCommand):
    """Handles healing the character and allies."""
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        block = self.get_block()

        block_properties = BLOCKS[block.type]
        if self.character.has_skill(SkillType.FIRST_AID):
            heal_bonus = 5
            if self.character.has_skill(SkillType.SURGERY) and block_properties.type == BlockType.HOSPITAL and block.lights_on:
                heal_bonus += 5
        else:
            heal_bonus = 0
        if target.hp < target.max_hp:
            target.heal(5 + heal_bonus)
            self.character.inventory.remove(self.character.equipped)
            self.character.equipped = None
            self.character.lose_ap(1)
            if target == self.character:
                self.message = "You use a first aid kit on yourself, and feel a bit better."
                self.success = True
            else:
                self.message = f"You use a first aid kit on {target.current_name}, and they gain some health."
                self.success = True
        else:
            if target == self.character:
                self.message = "You already feel healthy."
            else:
                self.message = f"{target.current_name} already feels healthy."

class Inject(ActionCommand):
    """Handles attacking enemies."""
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        if target.is_human:
            message = "You cannot inject humans."

        else:
            block = self.get_block()

            if self.character.inside:
                if block.lights_on:
                    self._inject_success(target)
                else:
                    success = random.randint(0, 1) == 1
                    if success:
                        self._inject_success(target)
                    else:
                        self.message = "While priming the needle, you happen to lose track of the zombie in the dark."
            else:
                self._inject_success(target)

    def _inject_success(self, target):
        target.revivify()
        self.character.lose_ap(10)

        # Trigger NPC sprite animation if visible
        sprites = list(self.character.game.game_ui.description_panel.human_sprite_group)
        for sprite in sprites:
            if target == sprite.npc:
                sprite.set_action(2)

        self.success = True
        self.message = "Following standard procedures, you press the syringe into the back of the zombie's neck and pump the glittering serum into its brain and spinal cord."
            