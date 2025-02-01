# actions.py

import random
from collections import defaultdict
import csv

from settings import *
from data import Action, ITEMS, ItemType, ItemFunction, BLOCKS, ResourcePath

class ActionExecutor:
    """Handles executing actions for both player and AI characters."""
    def __init__(self, game, actor):
        self.game = game
        self.actor = actor  # Define the acting character

    def execute(self, action, target):
        """Execute AI and player actions."""

        # Fetch block at the actor's location
        x, y = self.actor.location
        block = self.game.city.block(x, y)

        # System actions
        if action == Action.QUIT:
            self.game.quit_game()

        elif action == Action.PAUSE:
            self.game.pause_game()

        elif action == Action.OPTIONS:
            pass # NEED TO SET THIS UP

        elif action == Action.CLOSE_MAP:
            self.close_map()

        elif action == Action.ZOOM_IN:
            self.zoom_in()

        elif action == Action.ZOOM_OUT:
            self.zoom_out()

        # Movement
        elif action == Action.MOVE_UP:
            self.move(0, -1)
        elif action == Action.MOVE_DOWN:
            self.move(0, 1)
        elif action == Action.MOVE_LEFT:
            self.move(-1, 0)
        elif action == Action.MOVE_RIGHT:
            self.move(1, 0)
        elif action == Action.MOVE_UPLEFT:
            self.move(-1, -1)
        elif action == Action.MOVE_UPRIGHT:
            self.move(1, -1)
        elif action == Action.MOVE_DOWNLEFT:
            self.move(-1, 1)
        elif action == Action.MOVE_DOWNRIGHT:
            self.move(1, 1)       
        elif action == Action.MOVE:
            dx, dy = target.dx, target.dy
            self.move(dx, dy)
        
        # Combat
        elif action == Action.ATTACK:
            self.attack(target)            

        # Building actions
        elif action == Action.BARRICADE:
            self.barricade(block)
        elif action == Action.SEARCH:
            self.search(block)
        elif action == Action.ENTER:
            self.enter(block)
        elif action == Action.LEAVE:
            self.leave(block)

        # Inventory actions
        elif action == Action.EQUIP:
            self.equip(target.item)

        elif action == Action.UNEQUIP:
            self.unequip(target.item)

        elif action == Action.USE:
            self.use(target.item)
     
        elif action == Action.DROP:
            self.drop(target.item)

        # Update sprites after taking action
        self.game.game_ui.update()

    def attack(self, target, weapon=None):
        """Execute an attack depending on the attacker's state."""
        if self.actor.is_human:
            self._human_attack(target, weapon)
        else:
            self._zombie_attack(target, weapon)

    def _human_attack(self, target, weapon):
        if weapon:
            properties = ITEMS[weapon.type]
            if properties.item_function == ItemFunction.FIREARM and weapon.loaded_ammo == 0:
                    return False

            roll = random.randint(1, 20)
            attack_success = (roll + properties.attack) >= ATTACK_DIFFICULTY

            if attack_success:
                self._deplete_weapon(weapon, properties)
                target.take_damage(properties.damage)

        else: # If no weapon equipped, punch the enemy.
            roll = random.randint(1, 20)
            attack_success = roll >= ATTACK_DIFFICULTY

            if attack_success:
                target.take_damage(1)

    def _zombie_attack(self, target, weapon):
        roll = random.randint(1, 20)
        attack_success = (roll + weapon.attack) >= ATTACK_DIFFICULTY

        if attack_success:
            target.take_damage(weapon.damage)

    def _deplete_weapon(self, weapon, properties):
        """Reduce loaded ammo or durability, depending on weapon type."""
        if properties.item_function == ItemFunction.FIREARM:
            weapon.loaded_ammo -= 1
        elif properties.item_function == ItemFunction.MELEE:
            weapon.durability -= 1
            if weapon.durability <= 0:
                self.actor.inventory.remove(weapon)
                self.actor.weapon = None        

    def reload(self):
        weapon = self.actor.weapon
        if weapon.type == ItemType.PISTOL:
            weapon.loaded_ammo = weapon.max_ammo
        elif weapon.type == ItemType.SHOTGUN:
            weapon.loaded_ammo += 1
 
    def move(self, dx, dy):
        """Moves the actor to a new location."""
        x, y = self.actor.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < 100 and 0 <= new_y < 100:
            # If a player moves, they are no longer inside.
            if self.actor.inside:
                self.actor.inside = False
            self.actor.location = (new_x, new_y)

    def wander(self):
        """Randomly moves the actor to an adjacent block."""
        x, y = self.actor.location[0], self.actor.location[1]
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        new_x, new_y = x + dx, y + dy
        current_block = self.game.city.block(x, y)

        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:  # Ensure within city bounds
            new_block = self.game.city.block(new_x, new_y)
            self.action_points -= 2
            self.action_points_lost += 2
            current_block.current_zombies -= 1
            new_block.current_zombies += 1
            self.actor.location = (new_x, new_y)
            self.actor.inside = False
            return True
        return False

    def barricade(self, building):
        properties = BLOCKS[building.type]
        success_chances = [1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2]
        if properties.is_building and self.actor.inside:
            success_chance = success_chances[building.barricade.level]
            success = random.random() < success_chance
            if success:
                building.barricade.adjust_barricade_sublevel(1)

    def repair_building(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building and self.actor.inside:
            building.ransack_level = 0

    def enter(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building and not self.actor.inside:
            if self.actor.is_human:
                if building.barricade.level <= 4:
                    self.actor.inside = True
            else:
                if building.barricade.level == 0:
                    self.actor.inside = True             

    def leave(self, building):
        properties = BLOCKS[building.type]
        if properties.is_building and self.actor.inside:
            if self.actor.is_human:
                if building.barricade.level <= 4:
                    self.actor.inside = False
            else:
                if building.barricade.level == 0:
                    self.actor.inside = False                

    def search(self, building):
        search_path = ResourcePath('data/search.csv').path
        search_chances = self._load_search_chances(search_path)
        items_held = len(self.actor.inventory)
        building_properties = BLOCKS[building.type]
        if building_properties.is_building:
            if self.actor.inside:
                if building.lights_on:
                    multiplier = LIGHTSON_MULTIPLIER
                elif building.ransack_level > 0:
                    multiplier = RANSACKED_MULTIPLIER
                else:
                    multiplier = SEARCH_MULTIPLIER
                items = list(search_chances.keys())
                random.shuffle(items)

                for item_type in items:
                    search_chance = search_chances[item_type].get(building.type.name, 0.0) # Default to 0.0 if item not found
                    roll = random.random()
                    if roll < search_chance * multiplier:
                        item = self.actor.create_item(item_type)
                        if item is not None:
                            if items_held >= MAX_ITEMS:
                                return
                            elif item_type == ItemType.PORTABLE_GENERATOR:
                                for item in self.actor.inventory:
                                    if hasattr(item, 'type') and item.type == ItemType.PORTABLE_GENERATOR:
                                        return False
                            self.actor.inventory.append(item)

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
        if properties.item_function == ItemFunction.MELEE or properties.item_function == ItemFunction.FIREARM:
            self.actor.weapon = item

    def unequip(self, item):
        properties = ITEMS[item.type]
        self.actor.weapon = None

    def use(self, item):
        if item.type == ItemType.FIRST_AID_KIT:
            if self.actor.hp < self.actor.max_hp:
                self.actor.heal(20)
                self.actor.inventory.remove(item)
    
        elif item.type == ItemType.PORTABLE_GENERATOR:
            if self.actor.inside:
                item_used = self.actor.install_generator()
                if item_used:
                    self.actor.inventory.remove(item)
    
        elif item.type == ItemType.FUEL_CAN:
            if self.actor.inside:
                item_used = self.actor.fuel_generator()
                if item_used:
                    self.actor.inventory.remove(item)

        elif item.type == ItemType.TOOLBOX:
            if self.actor.inside:
                self.repair_building()

        elif item.type == ItemType.MAP:
            self.game.reading_map = True
        
        elif item.type == ItemType.PISTOL_CLIP:
            weapon = self.actor.weapon
            if weapon.type == ItemType.PISTOL:
                if weapon.loaded_ammo < weapon.max_ammo:
                    self.reload(weapon)
                    self.actor.inventory.remove(item)

        elif item.type == ItemType.SHOTGUN_SHELL:
            weapon = self.actor.weapon.sprite
            if weapon.type == ItemType.SHOTGUN:
                if weapon.loaded_ammo < weapon.max_ammo:
                    self.actor.reload(weapon)
                    self.actor.inventory.remove(item)          

    def drop(self, item):
        self.actor.inventory.remove(item)

    def install_generator(self):
        x, y = self.actor.location
        building = self.game.city.block(x, y)
        if building.generator_installed:
            return False
        else:
            building.generator_installed = True
            return True
        
    def fuel_generator(self):
        x, y = self.actor.location
        building = self.city.block(x, y)
        building.fuel_expiration = self.game.ticker + FUEL_DURATION
        building.lights_on = True
        return True
        
    def repair_building(self):
        x, y = self.actor.location
        building = self.city.block(x, y)
        building.ransack_level = 0
        building.ruined = False       

    def stand(self):
        """Actor stands up at full health after collecting enough action points."""
        self.is_dead = False
        self.hp = 50
        self.actor.action_points -= STAND_AP

    def close_map(self):
        self.game.reading_map = False
    
    def zoom_in(self):
        self.game.game_ui.map.zoom_in = True

    def zoom_out(self):
        self.game.game_ui.map.zoom_in = False


