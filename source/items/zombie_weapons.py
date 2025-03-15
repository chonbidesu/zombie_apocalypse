# zombie_weapons.py

from items.base_classes import ZombieWeapon
from data import ZombieWeaponType, ResourcePath

class Claws(ZombieWeapon):
    """The claws of a zombie."""
    def __init__(self, character):
        super().__init__(character, ZombieWeaponType.ZOMBIE_CLAWS, "Claws", "sharp claws", ResourcePath('cursor/zombie_claws.png').path, attack=25, damage=2)


class Teeth(ZombieWeapon):
    """The claws of a zombie."""
    def __init__(self, character):
        super().__init__(character, ZombieWeaponType.ZOMBIE_TEETH, "Teeth", "rotten teeth", ResourcePath('cursor/zombie_teeth.png').path, attack=10, damage=4)        