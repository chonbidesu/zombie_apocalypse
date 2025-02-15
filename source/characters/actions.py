# actions.py

import random
from collections import defaultdict
import csv
from dataclasses import dataclass

from settings import *
from data import Action, ITEMS, ItemType, ItemFunction, BLOCKS, BlockType, ResourcePath, SKILLS, SkillType


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    witness: str = ""
    attacked: str = ""


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

    def execute(self, action, target=None):
        """Execute AI and player actions."""
        # Fetch block at the actor's location
        x, y = self.actor.location
        block = self.game.state.city.block(x, y)

        weapon = self.actor.weapon
        player = self.game.state.player 
        screen_transition = self.game.game_ui.screen_transition
        action_progress = self.game.game_ui.action_progress

        # System actions
        if action == Action.QUIT:
            return self.game.quit_game()

        elif action == Action.NEW_GAME:
            self.game.start_new_game = True

        elif action == Action.SAVE_MENU:
            self.game.save_menu = True

        elif action == Action.LOAD_MENU:
            self.game.load_menu = True

        elif action == Action.SKILLS_MENU:
            self.game.skills_menu = True

        elif action == Action.BACK:
            self.game.save_menu = False
            self.game.load_menu = False
            self.game.skills_menu = False

        elif action == Action.PAUSE:
            return self.game.pause_game()

        elif action == Action.OPTIONS:
            pass # NEED TO SET THIS UP

        elif action == Action.CLOSE_MAP:
            return self.close_map()

        elif action == Action.ZOOM_IN:
            return self.zoom_in()

        elif action == Action.ZOOM_OUT:
            return self.zoom_out()

        # Stand up
        elif action == Action.STAND:
            if self.actor == player:
                action_progress.start("Standing", self.stand, duration=10000)
            else:
                return self.stand()

        # Movement
        elif action == Action.MOVE_UP:
            return self.move(0, -1)
        elif action == Action.MOVE_DOWN:
            return self.move(0, 1)
        elif action == Action.MOVE_LEFT:
            return self.move(-1, 0)
        elif action == Action.MOVE_RIGHT:
            return self.move(1, 0)
        elif action == Action.MOVE_UPLEFT:
            return self.move(-1, -1)
        elif action == Action.MOVE_UPRIGHT:
            return self.move(1, -1)
        elif action == Action.MOVE_DOWNLEFT:
            return self.move(-1, 1)
        elif action == Action.MOVE_DOWNRIGHT:
            return self.move(1, 1)       
        elif action == Action.MOVE:
            dx, dy = target.dx, target.dy
            return self.move(dx, dy)
        elif action == Action.WANDER:
            return self.wander()
        
        # Combat
        elif action == Action.ATTACK:
            return self.attack(target, weapon)            

        # Building actions
        elif action == Action.CLOSE_DOORS:
            if self.actor == player:
                action_progress.start("Closing doors", self.close_doors, block)
            else:
                return self.close_doors(block)
            
        elif action == Action.OPEN_DOORS:
            if self.actor == player:
                action_progress.start("Opening doors", self.open_doors, block)
            else:
                return self.open_doors(block)

        elif action == Action.BARRICADE:
            if self.actor == player:
                action_progress.start("Barricading", self.barricade, block)
            else:
                return self.barricade(block)
        elif action == Action.SEARCH:
            if self.actor == player:
                action_progress.start("Searching", self.search, block)
            else:
                return self.search(block)
        elif action == Action.ENTER:
            if self.actor == player and block.barricade.can_pass(self.actor):
                action_result = screen_transition.circle_wipe(self.enter, self.game.chat_history, block)
            else:
                action_result = self.enter(block)
            return action_result
        elif action == Action.LEAVE:
            if self.actor == player and block.barricade.can_pass(self.actor):
                action_result = screen_transition.circle_wipe(self.leave, self.game.chat_history, block)
            else:
                action_result = self.leave(block)
            return action_result
        elif action == Action.REPAIR_BUILDING:
            if self.actor == player:
                action_progress.start("Repairing", self.repair_building, block)
            else:
                return self.repair_building(block)
        elif action == Action.DECADE:
            if self.actor == player:
                action_progress.start("Smashing", self.break_barricades, block)
            else:
                return self.break_barricades(block)

        # Inventory actions
        elif action == Action.EQUIP:
            return self.equip(target.item)

        elif action == Action.UNEQUIP:
            return self.unequip(target.item)

        elif action == Action.USE:
            return self.use(target.item)
     
        elif action == Action.DROP:
            return self.drop(target.item)

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

    def _deplete_weapon(self, weapon, properties):
        """Reduce loaded ammo or durability, depending on weapon type."""
        if properties.item_function == ItemFunction.FIREARM:
            weapon.loaded_ammo -= 1
        elif properties.item_function == ItemFunction.MELEE:
            weapon.durability -= 1
            if weapon.durability <= 0:
                self.actor.inventory.remove(weapon)
                self.actor.weapon = None        

    def reload(self, weapon):
        if not weapon:
            return ActionResult(False, "You need to equip a firearm to reload.")

        properties = ITEMS[weapon.type]
        if properties.item_function == ItemFunction.MELEE:
            return ActionResult(False, "You need to equip a firearm to reload.")

        if weapon.type == ItemType.PISTOL:
            self.actor.ap -= 1
            return ActionResult(True, "You slap a new pistol clip into your gun.")
        elif weapon.type == ItemType.SHOTGUN:
            self.actor.ap -= 1
            return ActionResult(True, "You load a shell into your shotgun.")
 
    def move(self, dx, dy):
        """Moves the actor to a new location."""
        city = self.game.state.city
        x, y = self.actor.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 < new_x < CITY_SIZE and 0 < new_y < CITY_SIZE:
            new_block = city.block(new_x, new_y)
            block_properties = BLOCKS[new_block.type]
            is_human = self.actor.is_human

            # If a player moves, they are no longer inside unless they have Free Running.
            if is_human:
                if SkillType.FREE_RUNNING not in self.actor.human_skills:
                    self.actor.inside = False
                elif block_properties.is_building:
                    if new_block.ruined:
                        self.actor.inside = False
                        self.actor.fall()
                self.actor.ap -= 1
            else:
                self.actor.inside = False
                if SkillType.LURCHING_GAIT in self.actor.zombie_skills:
                    self.actor.ap -= 1
                else:
                    self.actor.ap -= 2
            self.actor.location = (new_x, new_y)
        
        else:
            return False

    def wander(self):
        """Randomly moves the actor to an adjacent block."""
        x, y = self.actor.location[0], self.actor.location[1]
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        new_x, new_y = x + dx, y + dy
        is_human = self.actor.is_human

        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:  # Ensure within city bounds
            if is_human:
                self.actor.ap -= 1
            else:
                self.actor.ap -= 2
            self.actor.location = (new_x, new_y)
            self.actor.inside = False
            return ActionResult(True)
        return ActionResult(False)

    def close_doors(self, building):
        building.doors_closed = True
        return ActionResult(True, "You close the doors of the building.")
    
    def open_doors(self, building):
        building.doors_closed = False
        return ActionResult(True, "You open the doors of the building.")

    def barricade(self, building):
        properties = BLOCKS[building.type]
        x, y = building.x, building.y
        block_npcs = self.actor.state.filter_characters_at_location(x, y, inside=True)

        success_chances = [1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2]
        if len(block_npcs.living_zombies) > 1:
            modifier = 0.5
        else:
            modifier = 1
        
        if properties.is_building and self.actor.inside:
            if building.ransack_level > 0:
                return ActionResult(False, "You have to repair the building before you can add barricades.")
            elif building.barricade.level >= 7 and building.barricade.sublevel >= 4:
                return ActionResult(False, "You can't add more barricades.")
            
            success_chance = success_chances[building.barricade.level]
            success = random.random() < success_chance * modifier
            if success:
                add_barricade = building.barricade.adjust_barricade_sublevel(1)
                if not add_barricade:
                    return ActionResult(False, "You can't add more barricades.")
                elif building.barricade.level == 4 and building.barricade.sublevel == 2:
                    self.actor.ap -= 1
                    return ActionResult(True, "You reinforce the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in.")
                elif building.barricade.sublevel == 0:
                    barricade_description = building.barricade.get_barricade_description()
                    self.actor.ap -= 1            
                    return ActionResult(True, f"You reinforce the barricade. The building is now {barricade_description}.")
                elif building.barricade.sublevel > 0:
                    self.actor.ap -= 1
                    return ActionResult(True, "You reinforce the barricade.")
            else:
                return ActionResult(False, "You can't find anything to reinforce the barricade.")
        else:
            return ActionResult(False, "You have to be inside a building to barricade.")

    def break_barricades(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building:
            if building.barricade.level > 0:
                building.barricade.register_hit()
                self.actor.ap -= 1
                if building.barricade.level == 0:
                    message = "You smash at the barricades. The last piece of it falls away."
                    witness = "Something smashes through the last of the barricades."
                else:
                    message = "You smash at the barricades."
                    witness = "Something smashes at the barricades."
                return ActionResult(True, message, witness)
            else:
                return ActionResult(False, "There are no barricades to break.")                
        else:
            return ActionResult(False, "Only buildings have barricades.")

    def ransack(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building:
            if self.actor.inside:
                if not building.ruined:
                    building.ransack_level += 1
                    if building.ransack_level == 6:
                        building.ruined = True
                        return ActionResult(True, "You ransack further rooms of the buildling. The building is now ruined.")
                    else:
                        if building.ransack_level == 1:
                            return ActionResult(True, "You ransack the building.")
                        else:
                            return ActionResult(True, "You ransack further rooms of the building.")
                else:
                    return ActionResult(False, "This building is already ruined.")
            else:
                return ActionResult(False, "You have to be inside to ransack.")
        else:
            return ActionResult(False, "Only buildings can be ransacked.")

    def enter(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building:
            if not self.actor.inside:
                if self.actor.is_human:
                    if building.barricade.level == 0:
                        self.actor.inside = True
                        self.actor.ap -= 1
                        return ActionResult(True, "You entered the building.")
                    elif building.barricade.level <= 4:
                        self.actor.inside = True
                        self.actor.ap -= 1
                        return ActionResult(True, "You climb through the barricades and are now inside.")
                    else:
                        return ActionResult(False, "You can't find a way through the barricades.")
                else:
                    if building.barricade.level == 0:
                        self.actor.inside = True   
                    else:
                        return ActionResult(False, "You have to break through the barricades first.")
            else:
                return ActionResult(False, "You are already inside.")
        else:
            return ActionResult(False, "This is not a building.")

    def leave(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building and self.actor.inside:
            if self.actor.is_human:
                if building.barricade.level == 0:
                    self.actor.inside = False
                    self.actor.ap -= 1
                    return ActionResult(True, "You left the building.")
                if building.barricade.level <= 4:
                    self.actor.inside = False
                    self.actor.ap -= 1
                    return ActionResult(True, "You climb through the barricades and are now outside.")
                else:
                    return ActionResult(False, "The building has been so heavily barricaded that you cannot leave through the main doors.")
            else:
                if building.barricade.level == 0:
                    self.actor.inside = False
                    self.actor.ap -= 1
                    return ActionResult(True, "You left the building.")
                else:
                    return ActionResult(False, "You have to break through the barricades first.")
        else:
            return ActionResult(False, "You can't leave this place.")

    def search(self, building):
        """Search a building for items."""
        search_path = ResourcePath('data/search.csv').path
        search_chances = self._load_search_chances(search_path)
        items_held = len(self.actor.inventory)
        building_properties = BLOCKS[building.type]

        if building_properties.is_building and self.actor.inside:
            if building.lights_on:
                multiplier = SEARCH_MULTIPLIER + LIGHTSON_MULTIPLIER
            elif building.ransack_level > 0:
                multiplier = RANSACKED_MULTIPLIER // building.ransack_level
            else:
                multiplier = SEARCH_MULTIPLIER
            items = list(search_chances.keys())
            random.shuffle(items)

            for item_type in items:
                search_chance = search_chances[item_type].get(building.type.name, 0.0) # Default to 0.0 if item not found
                roll = random.random()
                if roll < search_chance * multiplier:
                    item = self.actor.create_item(item_type)
                    item_properties = ITEMS[item.type]
                    if item is not None:
                        if items_held >= MAX_ITEMS:
                            self.actor.ap -= 1
                            return ActionResult(False, f"You found {item_properties.description}, but you are carrying too much!")
                        elif item.type == ItemType.PORTABLE_GENERATOR:
                            for inventory_item in self.actor.inventory:
                                if hasattr(inventory_item, 'type') and inventory_item.type == ItemType.PORTABLE_GENERATOR:
                                    self.actor.ap -= 1
                                    return ActionResult(False, "You found a portable generator, but you can only carry one at a time.")
                        self.actor.inventory.append(item)
                        self.actor.ap -= 1
                        return ActionResult(True, f"You found {item_properties.description}!")
            return ActionResult(False, "You didn't find anything.")
        else:
            return ActionResult(False, "You have to be inside a building to search.")

    def _load_search_chances(self, file_path):
        """Load search chances from a CSV file."""
        search_chances = defaultdict(dict)
        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item = row['Item']
                for building_type, chance in row.items():
                    if building_type != 'Item':  # Skip the 'Item' column
                        search_chances[item][building_type] = float(chance)
        return search_chances

    def equip(self, item):        
        properties = ITEMS[item.type]
        self.actor.weapon = item
        return ActionResult(True, f"You equip {properties.description}.")


    def unequip(self, item):
        properties = ITEMS[item.type]
        self.actor.weapon = None
        return ActionResult(True, f"You unequip {properties.description}.")

    def use(self, item):
        x, y = self.actor.location
        block = self.game.state.city.block(x, y)
        block_properties = BLOCKS[block.type]
        weapon = self.actor.weapon

        if item.type == ItemType.FIRST_AID_KIT:
            if SkillType.FIRST_AID in self.actor.human_skills:
                heal_bonus = 5
                if SkillType.SURGERY in self.actor.human_skills and block_properties.type == BlockType.HOSPITAL and block.lights_on:
                    heal_bonus += 5
            else:
                heal_bonus = 0
            if self.actor.hp < self.actor.max_hp:
                self.actor.heal(5 + heal_bonus)
                self.actor.inventory.remove(item)
                self.actor.ap -= 1
                return ActionResult(True, "You use a first aid kit, and feel a bit better.")
            else:
                return ActionResult(False, "You already feel healthy.")
    
        elif item.type == ItemType.PORTABLE_GENERATOR:
            
            result = self.install_generator(block)
            if result.success:
                self.actor.ap -= 1
                block.generator_installed = True
                self.actor.inventory.remove(item)
            return result
    
        elif item.type == ItemType.FUEL_CAN:
            result = self.fuel_generator(block)
            if result.success:
                self.actor.ap -= 1
                block.fuel_expiration = self.game.ticker + FUEL_DURATION
                block.lights_on = True
                self.actor.inventory.remove(item)
            return result

        elif item.type == ItemType.TOOLBOX:
            result = self.repair_building(block)
            if result.success:
                self.actor.ap -= 1
                block.ransack_level = 0
                block.ruined = False
            return result

        elif item.type == ItemType.MAP:
            self.game.reading_map = True
        
        elif item.type == ItemType.PISTOL_CLIP:
            result = self.reload(weapon)
            if result.success:
                self.actor.ap -= 1
                weapon.loaded_ammo = weapon.max_ammo
                self.actor.inventory.remove(item)
            return result

        elif item.type == ItemType.SHOTGUN_SHELL:
            result = self.reload(weapon)
            if result.sucess:       
                self.actor.ap -= 1
                weapon.loaded_ammo += 1                
                self.actor.inventory.remove(item)          
            return result

    def drop(self, item):
        properties = ITEMS[item.type]
        self.actor.inventory.remove(item)
        return ActionResult(True, f"You drop {properties.description}.")

    def install_generator(self, block):
        properties = BLOCKS[block.type]

        if not self.actor.inside:
            return ActionResult(False, "Generators need to be installed inside buildings.")

        if properties.is_building:
            building = block
            if building.generator_installed:
                return ActionResult(False, "A generator is already installed.")
            else:
                return ActionResult(True, "You install a generator. It needs fuel to operate.")
        
    def fuel_generator(self, block):
        properties = BLOCKS[block.type]

        if not self.actor.inside:
            return ActionResult(False, "You have to be inside a building to use this.")

        if properties.is_building:
            building = block
            if building.lights_on:
                return ActionResult(False, "Generator already has fuel.")
            elif not building.generator_installed:
                return ActionResult(False, "You need to install a generator first.")
            else:
                return ActionResult(True, "You fuel the generator. The lights are now on.")
        
    def repair_building(self, block):
        properties = BLOCKS[block.type]

        if not self.actor.inside:
            return ActionResult(False, "You have to be inside a building to use this.")
        
        if properties.is_building:
            building = block
            if building.ransack_level == 0:
                return ActionResult(False, "This building does not need repairs.")
            elif building.ruined:
                if not building.lights_on:
                    return ActionResult(False, "Ruined buildings need to be powered in order to be repaired.")
                elif not SkillType.CONSTRUCTION in self.actor.human_skills:
                    return ActionResult(False, "You need the Construction skill to repair ruins.")
            else:
                return ActionResult(True, "You repaired the interior of the building and cleaned up the mess.")

    def stand(self):
        """Actor stands up at full health."""
        if not self.actor.permadeath:
            self.actor.is_dead = False
            self.actor.hp = self.actor.max_hp
            if SkillType.ANKLE_GRAB in self.actor.zombie_skills:
                self.actor.ap -= 1
            else:
                self.actor.ap -= STAND_AP

    def close_map(self):
        self.game.reading_map = False
    
    def zoom_in(self):
        self.game.game_ui.map.zoom_in = True

    def zoom_out(self):
        self.game.game_ui.map.zoom_in = False       


