# player.py
import random
import csv
from collections import defaultdict
import pygame

from settings import *
from items import Item, Weapon

class Player:
    """Represents the player's character."""
    def __init__(self, x_groups, y_groups,
                 button_group, update_observations, get_block_at_player,
                 name, occupation, x, y):
        self.name = name
        self.occupation = occupation
        self.skills = []  # Skills active when human
        self.inventory = pygame.sprite.Group()  # Items carried by the player
        self.weapon = pygame.sprite.GroupSingle()  # The currently equipped weapon
        self.max_hp = 100  # Maximum hit points
        self.hp = self.max_hp  # Current hit points
        self.location = (x, y)  # Initial location in the 100x100 grid
        self.inside = False
        self.starting_trait = self.assign_starting_trait(occupation)
        self.is_dead = False  # Status of the player
        self.search_chances = self.load_search_chances("assets/search.csv")
        self.ticker = 0  # Tracks the number of actions taken
        self.x_groups = x_groups
        self.y_groups = y_groups
        self.button_group = button_group
        self.update_observations = update_observations
        self.get_block_at_player = get_block_at_player
        self.lights_on = pygame.sprite.Group()
        self.generator_installed = pygame.sprite.Group()
        self.weapon_group = pygame.sprite.Group()
        self.firearm_group = pygame.sprite.Group()

        for sprite in self.button_group:
            if sprite.name == 'enter':
                self.enter_button = sprite
            elif sprite.name == 'leave':
                self.leave_button = sprite
        self.button_group.remove(self.leave_button)

    def assign_starting_trait(self, occupation):
        """Assigns a starting trait based on the player's occupation."""
        traits = {
            "Doctor": "First Aid Training",
            "Soldier": "Firearms Training",
            "Engineer": "Construction Skills",
            "Athlete": "Body Building",
            "Teacher": "Educational Resources",
            "Scientist": "Experimental Knowledge",
            "Police Officer": "Combat Training",
        }
        return traits.get(occupation, "Survivor Instinct")


    
    def gain_skill(self, skill):
        """Adds a skill to the player's skill list depending on their state."""
        self.skills.append(skill)

    def list_inventory(self):
        """Returns a string representation of the inventory."""
        if not self.inventory:
            return "Inventory is empty."
        return ", ".join(item.name for item in self.inventory)

    def take_damage(self, amount):
        """Reduces the player's health by the given amount."""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def heal(self, amount):
        """Heals the player by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def die(self):
        """Handles the player's death."""
        self.is_dead = True
        return "The player has died."

#    def revive(self):
#        """Revives the player, switching them back to human form."""
#        if self.is_dead:
#            self.is_human = True
#            self.is_dead = False
#            self.hp = self.max_hp
#            return "The player has been revived and is now human again."
#        return "The player is not dead and cannot be revived."

    def status(self):
        """Returns the player's current status."""
        status = {
            "Name": self.name,
            "Occupation": self.occupation,
            "Location": self.location,
            "HP": f"{self.hp} / {self.max_hp}",
            "Actions taken": self.ticker,
        }
        return status

    def load_search_chances(self, file_path):
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

    def create_item(self, item_name):
        """Create an item or weapon based on its name."""
        # Check if the item is a weapon
        if item_name in WEAPONS:
            attributes = WEAPONS[item_name]
            if item_name in MELEE_WEAPONS:
                # Create a melee weapon
                weapon = Weapon(
                    name=item_name,
                    image_file=attributes['image_file'],
                    damage=attributes['damage'],
                    durability=attributes['durability']
                )
                self.weapon_group.add(weapon)
                return weapon
            elif item_name in FIREARMS:
                # Create a firearm
                weapon = Weapon(
                    name=item_name,
                    image_file=attributes['image_file'],
                    damage=attributes['damage'],
                    loaded_ammo=attributes['loaded_ammo'],
                    max_ammo=attributes['max_ammo']
                )
                self.weapon_group.add(weapon)
                self.firearm_group.add(weapon)
                return weapon
        elif item_name in ITEMS:
            # Create a regular item
            attributes = ITEMS[item_name]
            item = Item(
                name=item_name,
                image_file=attributes['image_file']
            )
            return item

    def increment_ticker(self, city):
        """Increments the ticker to track player actions."""
        self.ticker += 1
        for building in city.building_group:
            if hasattr(building, 'fuel_expiration') and building.fuel_expiration < self.ticker:
                if building in self.lights_on:
                    self.lights_on.remove(building)

    # Start of player actions

    def use_item(self, item_name, city):
        """Uses an item from the inventory if available."""
        for item in self.inventory:
            if item.name == item_name:
                result = item.use()
                self.increment_ticker(city)
                if item.consumable:
                    self.remove_item(item)
                return result
        return f"You don't have a {item_name}."

    def move(self, dx, dy, city):
        """Moves the player to a new location on the grid."""
        x, y = self.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < 100 and 0 <= new_y < 100:
            # If a player moves, they are no longer inside.
            if self.inside:
                self.inside = False
                self.button_group.remove(self.leave_button)
                self.button_group.add(self.enter_button)
            self.increment_ticker(city)
            self.location = (new_x, new_y)
            return True
        return False

    def barricade(self, city, modifier=1):
        current_block = self.get_block_at_player(self, city)
        if current_block in city.building_group and self.inside:
            self.increment_ticker(city)
            success_chance = BARRICADE_CHANCE * modifier
            success_chance = max(0, min(success_chance, 1))  # Ensure the chance is between 0 and 1
            success = random.random() < success_chance
            if success:
                add_barricade = current_block.barricade.adjust_barricade(1)
                if not add_barricade:
                    return "You can't add more barricades."
                if current_block.barricade.level == 4:
                    return f"The building is now very strongly barricaded. If you add any more barricades, you cannot re-enter the building."
                return f"You managed to add to the barricade. The building is now {current_block.barricade.get_barricade_description()}."
            else:
                return "You could not find anything to add to the barricade."
        else:
            return "You can't barricade here."

    def where(self, city):
        current_block = self.get_block_at_player(self, city)
        if self.inside:
            return f"You are standing inside {current_block.block_desc} called {current_block.block_name}."
        else:
            return f"You are standing in front of {current_block.block_desc} called {current_block.block_name}."

    def enter(self, city):
        current_block = self.get_block_at_player(self, city)
        if current_block in city.building_group:
            if not self.inside:
                if current_block.barricade.level <= 4:
                    self.increment_ticker(city)
                    self.inside = True
                    self.update_observations(self, city)
                    for button in self.button_group:
                        if button.name == 'enter':
                            self.button_group.remove(button)
                    self.button_group.add(self.leave_button)
                    return "You entered the building."
                else:
                    return "You can't find a way through the barricades."
            return "You are already inside."
        return "This is not a building."

    def leave(self, city):
        current_block = self.get_block_at_player(self, city)
        if current_block in city.building_group:
            if self.inside:
                self.increment_ticker(city)
                self.inside = False
                self.update_observations(self, city)
                for button in self.button_group:
                    if button.name == 'leave':
                        self.button_group.remove(button)
                self.button_group.add(self.enter_button)
                return "You left the building."
            return "You are already outside."
        return "You can't leave this place."

    def search(self, city):
        current_block = self.get_block_at_player(self, city)
        self.increment_ticker(city)
        if current_block in city.building_group:
            for group_type, group in city.building_type_groups.items():
                if current_block in group:
                    block_type = group_type
            if self.inside:
                if current_block in self.lights_on:
                    multiplier = 1.5
                else:
                    multiplier = 1.0
                items = list(self.search_chances.keys())
                random.shuffle(items)

                for item_name in items:
                    search_chance = self.search_chances[item_name].get(block_type, 0.0) # Default to 0.0 if item not found
                    if random.random() < search_chance * multiplier:
                        item = self.create_item(item_name)
                        if item is not None:
                            if item_name == 'Portable Generator':
                                for sprite in self.inventory:
                                    if hasattr(sprite, 'name') and sprite.name == "Portable Generator":
                                        return 'You found Portable Generator, but you can only carry one at a time.'
                            self.inventory.add(item)
                            return f"You found {item_name}!"
                        else:
                            return f"Tried to add {item_name} to inventory!"
                return f"You found nothing."
            
            else:
                return "You search around the building but there is nothing to be found."
        else:
            return "You search but there is nothing to be found."
        
    def install_generator(self, city):
        current_block = self.get_block_at_player(self, city)
        if current_block in self.generator_installed:
            return "Generator is already installed."
        else:
            self.increment_ticker(city)
            self.generator_installed.add(current_block)
            return "You install a generator. It needs fuel to operate."
        
    def fuel_generator(self, city):
        current_block = self.get_block_at_player(self, city)
        if current_block in self.lights_on:
            return "Generator already has fuel."
        elif current_block not in self.generator_installed:
            return "You need to install a generator first."
        else:
            self.increment_ticker(city)
            current_block.fuel_expiration = self.ticker + FUEL_DURATION
            self.lights_on.add(current_block)
            return "You fuel the generator. The lights are now on."