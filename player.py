# player.py
import random
import csv
from collections import defaultdict
import pygame
import sys
from enum import Enum, auto

from settings import *
from items import Item, Weapon

class Skill(Enum):
    BODY_BUILDING = auto()
    FREE_RUNNING = auto()
    CONSTRUCTION = auto()
    FIRST_AID = auto()
    FIREARMS_TRAINING = auto()

SkillProperties = namedtuple(
    'SkillProperties', [
        'description', 'effect'
    ]
)

SKILLS = {
    Skill.BODY_BUILDING: SkillProperties('Increases player max HP by 10.', ''),
    Skill.FREE_RUNNING: SkillProperties('Allows moving between adjacent buildings without going outside.', ''),
    Skill.CONSTRUCTION: SkillProperties('Player can repair ransacked buildings.', ''),
    Skill.FIRST_AID: SkillProperties('First Aid Kit heals an additional 10 HP.', ''),
    Skill.FIREARMS_TRAINING: SkillProperties('Trained with firearms.', '')
}


class Player:
    """Represents the player's character."""
    def __init__(self, city, name, occupation, x, y, inside=False):
        self.name = name
        self.occupation = occupation
        self.inventory = pygame.sprite.Group()  # Items carried by the player
        self.weapon = pygame.sprite.GroupSingle()  # The currently equipped weapon
        self.max_hp = 50  # Maximum hit points
        self.hp = self.max_hp  # Current hit points
        self.skills = set()
        self.location = (x, y)  # Initial location in the 100x100 grid
        self.inside = inside
        self.is_dead = False  # Status of the player
        self.search_chances = self.load_search_chances("assets/search.csv")
        self.ticker = 0  # Tracks the number of actions taken
        self.city = city

        self.assign_starting_trait(self.occupation)

    
    def assign_starting_trait(self, occupation):
        """Assigns a starting trait based on the player's occupation."""
        traits = {
            "Doctor": Skill.FIRST_AID,
            "Soldier": Skill.FIREARMS_TRAINING,
            "Engineer": Skill.CONSTRUCTION,
            "Athlete": Skill.BODY_BUILDING,
            "Plumber": Skill.FREE_RUNNING,
        }
        self.skills.add(traits[occupation])
    
    def gain_skill(self, choice):
        """Gain a skill if it's not already learned and enough XP is available."""
        SKILL_COST = 150  # cost to acquire a skill

        if choice in self.skills:
            print(f"{choice.name} already learned.")
            return False

        if self.xp >= SKILL_COST:
            self.xp -= SKILL_COST
            self.skills.add(choice)
            self.SKILL_EFFECTS[choice]["effect"](self)
            print(f"Learned skill: {self.SKILL_EFFECTS[choice]['description']}")
            return True

        print("Not enough XP to learn this skill.")
        return False

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

    def status(self):
        """Returns the player's current status."""
        status = {
            "Name": self.name,
            "Occupation": self.occupation,
            "Location": self.location,
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

    def create_item(self, type):
        """Create an item or weapon based on its name."""
        # Check if the item is a weapon
        item_type = getattr(ItemType, type)
        properties = ITEMS[item_type]
        if properties.item_function == ItemFunction.MELEE:
            # Create a melee weapon
            weapon = Weapon(type=item_type)
            return weapon
        elif properties.item_function == ItemFunction.FIREARM:
            # Create a firearm
            weapon = Weapon(type=item_type)
            return weapon
        elif properties.item_function == ItemFunction.ITEM or properties.item_function == ItemFunction.AMMO:
            # Create a regular item
            item = Item(type=item_type)
            return item


    # Start of player actions
    def attack(self, target):
        if self.weapon:
            weapon = self.weapon.sprite
            properties = ITEMS[weapon.type]
            if properties.item_function == ItemFunction.FIREARM:
                if weapon.loaded_ammo == 0:
                    return "Your weapon is out of ammo."

            roll = random.randint(1, 20)
            attack_roll = (roll + properties.attack) >= ATTACK_DIFFICULTY

            if attack_roll:
                if properties.item_function == ItemFunction.FIREARM:
                    weapon.loaded_ammo -= 1
                elif properties.item_function == ItemFunction.MELEE:
                    weapon.durability -= 1
                    if weapon.durability <= 0:
                        weapon.kill()
                        return target.zombie.take_damage(properties.damage) + " Your weapon breaks!"
                return target.zombie.take_damage(properties.damage)
            else:
                return "Your attack misses."
        else:
            roll = random.randint(1, 20)
            attack_roll = roll >= ATTACK_DIFFICULTY

            if attack_roll:
                return "You punch the zombie. " + target.zombie.take_damage(1)
            else:
                return "You try punching the zombie, but miss."


    def reload(self):
        weapon = self.weapon.sprite
        if weapon.type == ItemType.PISTOL:
            weapon.loaded_ammo = weapon.max_ammo
            return "You slap a new pistol clip into your gun."
        elif weapon.type == ItemType.SHOTGUN:
            weapon.loaded_ammo += 1
            return "You load a shell into your shotgun."

    def move(self, dx, dy):
        """Moves the player to a new location on the grid."""
        x, y = self.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < 100 and 0 <= new_y < 100:
            # If a player moves, they are no longer inside.
            if self.inside:
                self.inside = False
            self.location = (new_x, new_y)
            return True
        return False

    def barricade(self, modifier=1):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building and self.inside:
            success_chance = BARRICADE_CHANCE * modifier
            success_chance = max(0, min(success_chance, 1))  # Ensure the chance is between 0 and 1
            success = random.random() < success_chance
            if success:
                add_barricade = current_block.barricade.adjust_barricade_level(1)
                if not add_barricade:
                    return "You can't add more barricades."
                if current_block.barricade.level == 4:
                    return f"The building is now very strongly barricaded. If you add any more barricades, you cannot re-enter the building."
                return f"You managed to add to the barricade. The building is now {current_block.barricade.get_barricade_description()}."
            else:
                return "You could not find anything to add to the barricade."
        else:
            return "You can't barricade here."

    def repair_building(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building and self.inside:
            if current_block.is_ransacked:
                current_block.is_ransacked = False
                return "You repaired the interior of the building and cleaned up the mess."
            else:
                return "There's nothing to repair here."

    def enter(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building:
            if not self.inside:
                if current_block.barricade.level == 0:
                    self.inside = True
                    return "You entered the building."
                if current_block.barricade.level <= 4:
                    self.inside = True
                    return "You climb through the barricades."
                else:
                    return "You can't find a way through the barricades."
            return "You are already inside."
        return "This is not a building."

    def leave(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building:
            if self.inside:
                self.inside = False
                return "You left the building."
            return "You are already outside."
        return "You can't leave this place."

    def search(self):
        items_held = len(self.inventory.sprites())
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        block_properties = BLOCKS[current_block.type]
        if block_properties.is_building:
            if self.inside:
                if current_block.lights_on:
                    multiplier = LIGHTSON_MULTIPLIER
                elif current_block.is_ransacked:
                    multiplier = RANSACKED_MULTIPLIER
                else:
                    multiplier = SEARCH_MULTIPLIER
                items = list(self.search_chances.keys())
                random.shuffle(items)

                for item_type in items:
                    search_chance = self.search_chances[item_type].get(current_block.type.name, 0.0) # Default to 0.0 if item not found
                    roll = random.random()
                    if roll < search_chance * multiplier:
                        item = self.create_item(item_type)
                        item_properties = ITEMS[item.type]
                        if item is not None:
                            if items_held >= MAX_ITEMS:
                                return f"You found {item_properties.description}, but you are carrying too much and it falls under a pile of debris!"
                            elif item_type == 'PORTABLE_GENERATOR':
                                for sprite in self.inventory:
                                    if hasattr(sprite, 'type') and sprite.type == ItemType.PORTABLE_GENERATOR:
                                        return 'You found Portable Generator, but you can only carry one at a time.'
                            self.inventory.add(item)
                            return f"You found {item_properties.description}!"
                        else:
                            return f"Tried to add {item_properties.description} to inventory!"
                return f"You found nothing."
            
            else:
                return "You search around the building but there is nothing to be found."
        else:
            return "You search but there is nothing to be found."
        
    def install_generator(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        if current_block.generator_installed:
            return "Generator is already installed.", False
        else:
            current_block.generator_installed = True
            return "You install a generator. It needs fuel to operate.", True
        
    def fuel_generator(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        if current_block.lights_on:
            return "Generator already has fuel.", False
        elif not current_block.generator_installed:
            return "You need to install a generator first.", False
        else:
            current_block.fuel_expiration = self.ticker + FUEL_DURATION
            current_block.lights_on = True
            return "You fuel the generator. The lights are now on.", True
        

    # Handle player death
    def show_death_screen(self, screen):
        """Display a death screen with restart options."""
        # Create a semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)  # Transparency level (0 = transparent, 255 = opaque)
        overlay.fill(BLACK)

        # Render "YOU DIED" and "RESTART? Y / N"
        text_you_died = font_xxl.render("YOU DIED", True, (255, 0, 0))
        text_restart = font_xl.render("RESTART? Y / N", True, WHITE)

        # Get text positions
        you_died_rect = text_you_died.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        restart_rect = text_restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # Blit overlay and text onto the screen
        screen.blit(overlay, (0, 0))
        screen.blit(text_you_died, you_died_rect)
        screen.blit(text_restart, restart_rect)

        pygame.display.flip()  # Update display

        # Handle restart or quit actions
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:  # Restart game logic
                        return "restart"
                    elif event.key == pygame.K_n:  # Quit game
                        pygame.quit()
                        sys.exit()


