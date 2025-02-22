# __init__.py

from dataclasses import dataclass

from settings import *
from data import ITEMS, ItemType, ItemFunction, SKILLS, SkillType, SkillCategory, OCCUPATIONS
from items import Item, Weapon
from characters.human_state import Human
from characters.zombie_state import Zombie, ZombieWeapon


@dataclass
class CharacterName:
    first_name: str
    last_name: str
    zombie_adjective: str


class Character:
    """Base class for Player and NPC Characters."""
    def __init__(self, game, name, occupation, x, y, is_human, inside=False):
        self.game = game
        self.name = name
        self.occupation = occupation
        self.location = (x, y)
        self.max_hp = MAX_HP
        self.hp = self.max_hp
        self.ap = 0
        self.xp = 0
        self.level = 0
        self.is_dead = False
        self.permadeath = False
        self.is_human = is_human
        self.inside = inside
        self.inventory = []
        self.equipped = None
        self.human_skills = set()
        self.zombie_skills = set()
        self.safehouse = None
        self.current_goal = None

        self.get_state()
        self.add_starting_skill()
        self.add_starting_items()


    def get_state(self):
        """Set state based on is_human."""
        if self.is_human:
            self.state = Human(self)
        else:
            self.state = Zombie(self)
        self.state.update_name()

    def add_starting_skill(self):
        """Adds a starting skill depending on player's occupation."""
        occupation_properties = OCCUPATIONS[self.occupation]
        starting_skill = occupation_properties.starting_skill
        self.add_skill(starting_skill)

    def add_starting_items(self):
        """Adds starting items depending on player's occupation."""
        occupation_properties = OCCUPATIONS[self.occupation]
        starting_items = occupation_properties.starting_items
        for item_type in starting_items:
            item = self.create_item(item_type)
            self.inventory.append(item)

    def add_skill(self, skill):
        """Add a skill to the character's skill set."""
        if skill in SKILLS:
            skill_category = SKILLS[skill].skill_category

            if skill_category == SkillCategory.ZOMBIE:
                self.zombie_skills.add(skill)
            else:
                self.human_skills.add(skill)

            self.apply_skill_effect(skill)
            self.level += 1

    def has_skill(self, skill):
        """Check if a character has a particular skill."""
        return skill in self.human_skills or skill in self.zombie_skills

    def apply_skill_effect(self, skill, remove=False):
        """Apply or remove the passive effects of a skill."""
        if remove:
            modifier = -1
        else:
            modifier = 1

        if skill == SkillType.BODY_BUILDING:
            self.max_hp += 10 * modifier
        elif skill == SkillType.FLESH_ROT:
            self.max_hp += 10 * modifier

    def take_damage(self, amount, fatal=True):
        """Reduces the character's health by the given amount."""
        self.hp -= amount
        if self.hp <= 0:
            if fatal:
                self.hp = 0
                self.state.die()
            else:
                self.hp = 1
        elif self == self.game.state.player:  # Trigger red flicker effect for the player only
            self.game.game_ui.screen_transition.flicker_red()                

    def heal(self, amount):
        """Heals the character by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def revive(self):
        """Revives the character to human state."""
        self.is_dead = True
        self.is_human = True
        self.get_state()

        for skill in self.zombie_skills:
            self.apply_skill_effect(skill, remove=True)
        for skill in self.human_skills:
            self.apply_skill_effect(skill)    

    def gain_ap(self, ap):
        """Gain a certain amount of action points."""
        self.ap += ap

    def lose_ap(self, ap):
        """Lose a certain amount of action points."""
        self.ap -= ap        

    def gain_xp(self, xp):
        """Gain a certain amount of experience points."""
        self.xp += xp

    def status(self):
        """Returns the character's current status."""
        status = {
            "Name": self.current_name,
            "Occupation": self.occupation.name.title(),
            "HP": f"{self.hp} / {self.max_hp}",
            "XP": self.xp
        }
        return status
    
    def create_item(self, type):
        """Create an item based on its type."""
        # Check if the item is a weapon
        item_type = getattr(ItemType, type)
        if item_type in [ItemType.BEER, ItemType.WINE, ItemType.CANDY]:
            item = ITEMS[item_type](self, item_type)
        else:
            item = ITEMS[item_type](self)

        return item

    def equip(self, item):
        self.equipped = item

    def deplete_weapon(self):
        """Reduce loaded ammo or durability, depending on weapon type."""
        properties = ITEMS[self.weapon.type]
        if properties.item_function == ItemFunction.FIREARM:
            self.weapon.loaded_ammo -= 1
        elif properties.item_function == ItemFunction.MELEE:
            self.weapon.durability -= 1
            if self.weapon.durability <= 0:
                self.inventory.remove(self.weapon)
                self.weapon = None  

    def enter(self):
        self.inside = True

    def leave(self):
        self.inside = False

    def move(self, x, y):
        self.location = (x, y)

    def fall(self):
        """Character falls from a building, taking damage."""
        self.take_damage(5, fatal=False)
        if self == self.game.state.player:
            self.game.chat_history.append("You fall from the crumbling building, injuring yourself.")             

    def stand(self):
        self.is_dead = False

    def die(self):
        """Handles the character's death."""
        zombified = self.is_human
        self.is_dead = True
        self.is_human = False

        if zombified:
            self.get_state()

            # Reassign passive skill effects
            for skill in self.human_skills:
                self.apply_skill_effect(skill, remove=True)
            for skill in self.zombie_skills:
                self.apply_skill_effect(skill)                