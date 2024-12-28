# items.py

class Item:
    """Base class for all items."""
    def __init__(self, name, type, description):
        self.name = name
        self.type = type
        self.description = description


# Weapons
class Weapon(Item):
    """Base class for all weapons."""
    def __init__(self, name, type, description, damage, ammo_type=None, max_ammo=None):
        super().__init__(name, type, description)
        self.damage = damage
        self.ammo_type = ammo_type  # Type of ammo this firearm uses
        self.loaded_ammo = 0  # Amount of ammo currently loaded
        self.max_ammo = max_ammo  # Maximum ammo the firearm can hold