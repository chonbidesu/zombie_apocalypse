# state.py

from dataclasses import dataclass
import random

from data import ItemType, SKILLS, SkillType, SkillCategory, OCCUPATIONS, OccupationCategory
from core.settings import *
from items import (FirstAidKit, PortableGenerator, FuelCan, Map, Toolbox, Binoculars, DNAExtractor, Syringe, Consumable, Book, PoetryBook, Crucifix, GPSUnit, Newspaper, 
                    ShotgunShell, PistolClip, Shotgun, Pistol, Knife, Crowbar, FireAxe, Shovel, BaseballBat, GolfClub, HockeyStick, TennisRacket
)


@dataclass
class CharacterName:
    first_name: str
    last_name: str
    zombie_adjective: str


@dataclass
class BlockNPCs:
    x: int
    y: int
    inside: bool
    living_humans: list
    living_zombies: list
    dead_bodies: list
    dead_zombies: list
    revivifying_bodies: list


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


class CharacterHelper:
    """Helper for the CharacterClass."""
    def __init__(self, character):
        self.game = character.game
        self.character = character # Reference the parent character
   
    def filter_characters_at_location(self, x, y, inside=False, include_player=True):
        """Retrieve all characters at a given location and categorize them."""
        player = self.game.state.player
        characters_here = [
            npc for npc in self.game.state.npcs.list
            if npc.location == (x, y) and npc.inside == inside
        ]

        if include_player:
            # Add the player to the list if they are at location
            if player.location == (x, y) and player.inside == inside:
                characters_here.append(player)

        zombies_here = [character for character in characters_here if not character.is_human]
        humans_here = [character for character in characters_here if character.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [c for c in characters_here if c.is_dead]
        dead_zombies = [z for z in zombies_here if z.is_dead]
        revivifying_bodies = [h for h in humans_here if h.is_dead]

        return BlockNPCs(x, y, inside, living_humans, living_zombies, dead_bodies, dead_zombies, revivifying_bodies)                      
    
    def get_adjacent_locations(self):
        """Returns a list of (x, y) coordinates for the 8 adjacent blocks."""
        x, y = self.character.location
        adjacent_locations = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), # Top row
            (x - 1, y),                 (x + 1, y),     # Middle row
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)  # Bottom row
        ]
        valid_locations = []

        # Filter only valid locations in bounds
        for location in adjacent_locations:
            x, y = location
            if 0 < x < CITY_SIZE - 1 and 0 < y < CITY_SIZE - 1:
                valid_locations.append(location)
        return valid_locations
      
    def select_skill(self):
        """Selects a skill to learn."""
        occupation_category = OCCUPATIONS[self.character.occupation].occupation_category

        if self.character.is_human:
            skills = [
                skill for skill, properties in SKILLS.items() 
                if properties.skill_category != SkillCategory.ZOMBIE and
                (properties.skill_category != SkillCategory.ZOMBIE_HUNTER or self.character.level >= 10)
            ]
        else:
            skills = [skill for skill, properties in SKILLS.items() 
                      if properties.skill_category == SkillCategory.ZOMBIE]           

        acquired_skills = set(self.character.human_skills) if self.character.is_human else set(self.character.zombie_skills)

        # Filter skills where prerequisites are met
        skills_with_prereqs_met = [
            skill for skill in skills 
            if all(prerequisite in acquired_skills for prerequisite in SKILLS[skill].prerequisite_skills)
        ]

        occupation_skills = [skill for skill, properties in SKILLS.items() if skill in skills_with_prereqs_met and properties.skill_category == occupation_category]

        # Prioritize occupational skills
        if occupation_skills:
                return random.choice(occupation_skills) if random.random() < 0.75 else random.choice(skills_with_prereqs_met)
                
        # If no occupation skills are available, pick any valid skill
        if skills_with_prereqs_met:
            return random.choice(skills_with_prereqs_met)
            
        return None

    def get_skill_xp_cost(self, skill):
        """Calculate the XP cost for the given skill based on the player's occupation."""
        skill_category = SKILLS[skill].skill_category
        occupation_category = OCCUPATIONS[self.character.occupation].occupation_category

        if skill_category == SkillCategory.CIVILIAN:
            return 100 # Fixed cost for civilian skills
        
        elif skill_category == SkillCategory.MILITARY:
            if occupation_category == OccupationCategory.MILITARY:
                return 75
            elif occupation_category == OccupationCategory.CIVILIAN:
                return 100
            else: # Science occupation
                return 150
            
        elif skill_category == SkillCategory.SCIENCE:
            if occupation_category == OccupationCategory.SCIENCE:
                return 75
            elif occupation_category == OccupationCategory.CIVILIAN:
                return 100
            else: # Military occupation
                return 150
            
        elif skill_category == SkillCategory.ZOMBIE_HUNTER:
            return 100
            
        elif skill_category == SkillCategory.ZOMBIE:
            return 100 # Fixed cost for zombie skills            

    def add_starting_skill(self):
        """Adds a starting skill depending on player's occupation."""
        occupation_properties = OCCUPATIONS[self.character.occupation]
        starting_skill = occupation_properties.starting_skill
        self.add_skill(starting_skill)

    def add_starting_items(self):
        """Adds starting items depending on player's occupation."""
        occupation_properties = OCCUPATIONS[self.character.occupation]
        starting_items = occupation_properties.starting_items
        for item_type in starting_items:
            item = self.create_item(item_type)
            self.character.inventory.append(item)

    def add_skill(self, skill):
        """Add a skill to the character's skill set."""
        if skill in SKILLS:
            skill_category = SKILLS[skill].skill_category

            if skill_category == SkillCategory.ZOMBIE:
                self.character.zombie_skills.add(skill)
            else:
                self.character.human_skills.add(skill)

            self.character.gain_level()

    def has_skill(self, skill):
        """Check if a character has a particular skill."""
        return skill in self.character.human_skills or skill in self.character.zombie_skills

    def create_item(self, type):
        """Create an item based on its type."""
        item_classes = {
            ItemType.FIRST_AID_KIT: FirstAidKit,
            ItemType.PORTABLE_GENERATOR: PortableGenerator,
            ItemType.FUEL_CAN: FuelCan,
            ItemType.MAP: Map,
            ItemType.TOOLBOX: Toolbox,
            ItemType.BINOCULARS: Binoculars,
            ItemType.DNA_EXTRACTOR: DNAExtractor,
            ItemType.SYRINGE: Syringe,
            ItemType.BEER: Consumable,
            ItemType.WINE: Consumable,
            ItemType.BOOK: Book,
            ItemType.POETRY_BOOK: PoetryBook,
            ItemType.CANDY: Consumable,
            ItemType.CRUCIFIX: Crucifix,
            ItemType.GPS_UNIT: GPSUnit,
            ItemType.NEWSPAPER: Newspaper,
            ItemType.SHOTGUN_SHELL: ShotgunShell,
            ItemType.PISTOL_CLIP: PistolClip,
            ItemType.KNIFE: Knife,
            ItemType.CROWBAR: Crowbar,
            ItemType.FIRE_AXE: FireAxe,
            ItemType.SHOVEL: Shovel,
            ItemType.BASEBALL_BAT: BaseballBat,
            ItemType.GOLF_CLUB: GolfClub,
            ItemType.HOCKEY_STICK: HockeyStick,
            ItemType.TENNIS_RACKET: TennisRacket,
            ItemType.SHOTGUN: Shotgun,
            ItemType.PISTOL: Pistol,
        }

        # Check if the item is a weapon
        item_type = getattr(ItemType, type)
        if item_type in [ItemType.BEER, ItemType.WINE, ItemType.CANDY]:
            item = item_classes[item_type](self.character, item_type)
        else:
            item = item_classes[item_type](self.character)

        return item            






