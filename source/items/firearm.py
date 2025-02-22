# firearm.py

from data import ResourcePath, ItemType
from items import Firearm


class Shotgun(Firearm):
    """A shotgun that holds 2 shells at a time."""
    def __init__(self, character):
        super().__init__(character, ItemType.SHOTGUN, "Shotgun", "a shotgun", ResourcePath('items/shotgun.png').path, attack=5, damage=10, max_ammo=2)


class Pistol(Firearm):
    """A pistol that holds 6 bullet magazines."""
    def __init__(self, character):
        super().__init__(character, ItemType.PISTOL, "Pistol", "a pistol", ResourcePath('items/pistol.png').path, attack=5, damage=5, max_ammo=6)