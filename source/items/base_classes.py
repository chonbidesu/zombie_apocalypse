# base_classes.py

from enum import Enum, auto
from data import ItemType

class ItemFunction(Enum):
    MISC = auto()
    AMMO = auto()
    MELEE = auto()
    FIREARM = auto()
    SCIENCE = auto()

class Item:
    """Base class for all items."""
    def __init__(self, character, type, name, description, item_function, image_file):
        self.character = character
        self.type = type
        self.name = name
        self.description = description
        self.item_function = item_function
        self.image_file = image_file

    def use(self):
        """Default use method—only for instant-use items."""
        raise NotImplementedError("This item must be equipped before use.")
    
    def drop(self):
        """Drop the item."""
        self.character.drop(self)
        return True, f"You drop {self.description}."

    def _can_reload(self, equipped):
        if not equipped:
            return False, "You need to equip a firearm to reload."

        if equipped.item_function in [ItemFunction.MELEE, ItemFunction.SCIENCE]:
            return False, "You need to equip a firearm to reload."
        
        if equipped.loaded_ammo >= equipped.max_ammo:
            return False, "Your weapon is already fully loaded."    
        
        if (self.type == ItemType.SHOTGUN_SHELL and equipped.type == ItemType.PISTOL) or (self.type == ItemType.PISTOL_CLIP and equipped.type == ItemType.SHOTGUN):
            return False, "This is the wrong type of ammo for this weapon."
        
        return True, ""      
    
    def get_block(self):
        x, y = self.character.location
        city = self.character.game.state.city
        block = city.block(x, y)
        return block    

    def get_attributes(self):
        """Returns item-specific attributes for saving."""
        return {}  # Default: No special attributes     


class Weapon(Item):
    """Base class for all weapons."""
    def __init__(self, character, type, name, description, image_file, attack, damage, durability=None, max_ammo=None):
        super().__init__(character, type, name, description, "Weapon", image_file)
        self.attack = attack
        self.damage = damage

    def use(self):
        if self.character.equipped != self:
            self.character.equip(self)
            return True, f"You equipped {self.description}."
        else:
            self.character.unequip()
            return True, f"You unequipped {self.description}."


class Firearm(Weapon):
    """Base class for all weapons."""
    def __init__(self, character, type, name, description, image_file, attack, damage, max_ammo):
        super().__init__(character, type, name, description, image_file, attack, damage, durability=None, max_ammo=max_ammo)
        self.item_function = ItemFunction.FIREARM
        self.loaded_ammo = max_ammo
        self.max_ammo = max_ammo

    def reload(self, amount):
        if amount:
            self.loaded_ammo = (min(self.loaded_ammo + amount, self.max_ammo))
        else:
            self.loaded_ammo = self.max_ammo

    def get_attributes(self):
        """Returns firearm-specific attributes, including ammo count."""
        return {"loaded_ammo": self.loaded_ammo}

class Melee(Weapon):
    """Base class for all weapons."""
    def __init__(self, character, type, name, description, image_file, attack, damage, durability):
        super().__init__(character, type, name, description, image_file, attack, damage, durability, max_ammo=None)
        self.item_function = ItemFunction.MELEE
        self.durability = durability

    def get_attributes(self):
        """Returns weapon-specific attributes."""
        return {"durability": self.durability}        