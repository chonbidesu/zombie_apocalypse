# player.py
import random
import csv
from collections import defaultdict
import pygame

from settings import *
from items import Item, Weapon

class Player:
    """Represents the player's character."""
    def __init__(self, name, occupation, x, y):
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

    def get_current_observations(self, current_block, building_group, lights_on, generator_installed):
        current_observations = ""
        if self.inside:
            current_observations += f'You are standing inside {current_block.block_name}. '
            if not current_block in lights_on:
                current_observations += 'With the lights out, you can hardly see anything. '
            current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "
            
            # Check if the building has a running generator.
            if current_block in generator_installed:
                current_observations += "A portable generator has been set up here. "
                if current_block in lights_on:
                    current_observations += "It is running. "
                else:
                    current_observations += "It is out of fuel. "
        else:
            if current_block in building_group:
                current_observations += f'You are standing outside {current_block.block_desc}. A sign reads "{current_block.block_name}". '
                current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "
                if current_block in lights_on:
                    current_observations += "Lights are on inside. "
            else:
                current_observations += f'You are standing in {current_block.block_desc}.'
        return current_observations

    def update_observations(self, current_block, building_group, lights_on, generator_installed):
        """Update the observations list based on the player's current state."""
        current_block.observations.clear()  # Clear existing observations
        if self.inside:
            current_block.observations.append(self.get_current_observations(current_block, building_group, lights_on, generator_installed))
            current_block.observations.append(current_block.block_inside_desc)
        else:
            current_block.observations.append(self.get_current_observations(current_block, building_group, lights_on, generator_installed))
            current_block.observations.append(current_block.block_outside_desc)

    def description(self, current_block, building_group, lights_on, generator_installed):
        """Return the current list of observations as a list."""
        self.update_observations(current_block, building_group, lights_on, generator_installed)  # Ensure observations are current
        return current_block.observations
    
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
                return Weapon(
                    name=item_name,
                    image_file=attributes['image_file'],
                    damage=attributes['damage'],
                    durability=attributes['durability']
                )
            elif item_name in FIREARMS:
                # Create a firearm
                return Weapon(
                    name=item_name,
                    image_file=attributes['image_file'],
                    damage=attributes['damage'],
                    loaded_ammo=attributes['loaded_ammo'],
                    max_ammo=attributes['max_ammo']
                )
        elif item_name in ITEMS:
            # Create a regular item
            attributes = ITEMS[item_name]
            return Item(
                name=item_name,
                image_file=attributes['image_file']
            )

    def increment_ticker(self, building_group, lights_on):
        """Increments the ticker to track player actions."""
        self.ticker += 1
        for building in building_group:
            if building.fuel_expiration < self.ticker:
                if building in lights_on:
                    lights_on.remove(building)

    # Start of player actions

    def use_item(self, item_name, building_group, lights_on):
        """Uses an item from the inventory if available."""
        for item in self.inventory:
            if item.name == item_name:
                result = item.use()
                self.increment_ticker(building_group, lights_on)
                if item.consumable:
                    self.remove_item(item)
                return result
        return f"You don't have a {item_name}."

    def move(self, dx, dy, building_group, lights_on):
        """Moves the player to a new location on the grid."""
        x, y = self.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < 100 and 0 <= new_y < 100:
            # If a player moves, they are no longer inside.
            self.inside = False
            self.increment_ticker(building_group, lights_on)
            self.location = (new_x, new_y)
            return True
        return False

    def barricade(self, current_block, building_group, lights_on, modifier=1):
        if current_block in building_group and self.inside:
            self.increment_ticker(building_group, lights_on)
            success_chance = BARRICADE_CHANCE * modifier
            success_chance = max(0, min(success_chance, 1))  # Ensure the chance is between 0 and 1
            success = random.random() < success_chance
            if success:
                add_barricade = current_block.barricade.adjust_barricade(1)
                if not add_barricade:
                    return "You can't add more barricades."
                return f"You managed to add to the barricade. The building is now {current_block.barricade.get_barricade_description()}."
            else:
                return "You could not find anything to add to the barricade."
        else:
            return "You can't barricade here."

    def where(self, current_block):
        if self.inside:
            return f"You are standing inside {current_block.block_desc} called {current_block.block_name}."
        else:
            return f"You are standing in front of {current_block.block_desc} called {current_block.block_name}."

    def enter(self, current_block, building_group, lights_on, generator_installed):
        if current_block in building_group:
            if not self.inside:
                self.increment_ticker(building_group, lights_on)
                self.inside = True
                self.update_observations(current_block, building_group, lights_on, generator_installed)
                return "You entered the building."
            return "You are already inside."
        return "This is not a building."

    def leave(self, current_block, building_group, lights_on, generator_installed):
        if current_block in building_group:
            if self.inside:
                self.increment_ticker(building_group, lights_on)
                self.inside = False
                self.update_observations(current_block, building_group, lights_on, generator_installed)
                return "You left the building."
            return "You are already outside."
        return "You can't leave this place."

    def search(self, current_block, building_group, lights_on, building_type_groups):
        self.increment_ticker(building_group, lights_on)
        if current_block in building_group:
            for group_type, group in building_type_groups.items():
                if current_block in group:
                    block_type = group_type
            if self.inside:
                if current_block in lights_on:
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
        
    def install_generator(self, current_block, building_group, lights_on, generator_installed):
        if current_block in generator_installed:
            return "Generator is already installed."
        else:
            self.increment_ticker(building_group, lights_on)
            generator_installed.add(current_block)
            return "You install a generator. It needs fuel to operate."
        
    def fuel_generator(self, current_block, building_group, lights_on, generator_installed):
        if current_block in lights_on:
            return "Generator already has fuel."
        elif current_block not in generator_installed:
            return "You need to install a generator first."
        else:
            self.increment_ticker(building_group, lights_on)
            current_block.fuel_expiration = self.ticker + FUEL_DURATION
            lights_on.add(current_block)
            return "You fuel the generator. The lights are now on."