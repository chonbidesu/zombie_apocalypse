# __init__.py

from settings import *
from data import ITEMS, ItemType, ItemFunction
from items import Item, Weapon
from characters.human_state import Human
from characters.zombie_state import Zombie
from characters.actions import ActionExecutor

class Character:
    """Base class for Player and NPC Characters."""
    def __init__(self, game, occupation, x, y, is_human, inside=False):
        self.game = game
        self.occupation = occupation
        self.location = (x, y)
        self.max_hp = MAX_HP
        self.hp = self.max_hp
        self.ap = 0
        self.is_dead = False
        self.is_human = is_human
        self.inside = inside
        self.inventory = []
        self.weapon = None
        self.state = self.get_state()
        self.human_skills = set()
        self.zombie_skills = set()
        self.action = ActionExecutor(game, self)

    # Set initial state
    def get_state(self):
        if self.is_human:
            state = Human(self.game, self)
        else:
            state = Zombie(self.game, self)
        return state

    def take_damage(self, amount):
        """Reduces the character's health by the given amount."""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def heal(self, amount):
        """Heals the character by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def die(self):
        """Handles the character's death."""
        self.is_dead = True
        self.is_human = False
        self.state = Zombie(self.game, self)

    def revivify(self):
        """Revives the character to human state."""
        self.is_dead = True
        self.is_human = True
        self.state = Human(self.game, self)

    def status(self):
        """Returns the character's current status."""
        status = {
            "Occupation": self.occupation,
            "Location": self.location,
            "HP": f"{self.hp} / {self.max_hp}",
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
    
