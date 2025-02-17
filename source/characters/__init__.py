# __init__.py

from dataclasses import dataclass

from settings import *
from data import ITEMS, ItemType, ItemFunction, SKILLS, SkillType, SkillCategory, OCCUPATIONS
from characters.items import Item, Weapon
from characters.human_state import Human
from characters.zombie_state import Zombie
from characters.actions import ActionExecutor


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
        self.weapon = None
        self.state = self.get_state()
        self.human_skills = set()
        self.zombie_skills = set()
        self.action = ActionExecutor(game, self)

        self.add_starting_skill()
        self.add_starting_items()

    def update_name(self):
        """Updates the character's name based on their current state."""
        if self.is_human:
            self.current_name = f"{self.name.first_name} {self.name.last_name}"
        else:
            self.current_name = f"{self.name.zombie_adjective} {self.name.first_name}"

    def get_state(self):
        """Set state based on is_human."""
        if self.is_human:
            state = Human(self.game, self)
            self.update_name()
        else:
            state = Zombie(self.game, self)
            self.update_name()
        return state

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
                self.die()
            else:
                self.hp = 1
        elif self == self.game.state.player:  # Trigger red flicker effect for the player only
            self.game.game_ui.screen_transition.flicker_red()                

    def fall(self):
        """Character falls from a building, taking damage."""
        self.take_damage(5, fatal=False)
        self.game.chat_history.append("You fall from the crumbling building, injuring yourself.")

    def heal(self, amount):
        """Heals the character by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def die(self):
        """Handles the character's death."""
        if self.is_human:
            zombified = True
        else:
            zombified = False

        self.is_dead = True
        self.is_human = False
        self.state = Zombie(self.game, self)
        self.update_name()

        # Reassign passive skill effects
        if zombified:
            for skill in self.human_skills:
                self.apply_skill_effect(skill, remove=True)
            for skill in self.zombie_skills:
                self.apply_skill_effect(skill)

    def revivify(self):
        """Revives the character to human state."""
        self.is_dead = True
        self.is_human = True
        self.state = Human(self.game, self)
        self.update_name()
        for skill in self.zombie_skills:
            self.apply_skill_effect(skill, remove=True)
        for skill in self.human_skills:
            self.apply_skill_effect(skill)    

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
    