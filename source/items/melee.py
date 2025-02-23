# melee.py

from data import ResourcePath, ItemType
from items.base_classes import Melee


class Knife(Melee):
    """A sharp hunting knife."""
    def __init__(self, character):
        super().__init__(character, ItemType.KNIFE, "Knife", "a knife", ResourcePath('items/knife.png').path, attack=20, damage=2, durability=75)


class Crowbar(Melee):
    """A steel crowbar."""
    def __init__(self, character):
        super().__init__(character, ItemType.CROWBAR, "Crowbar", "a crowbar", ResourcePath('items/crowbar.png').path, attack=5, damage=2, durability=30)


class FireAxe(Melee):
    """A sharp, red fire axe."""
    def __init__(self, character):
        super().__init__(character, ItemType.FIRE_AXE, "Fire Axe", "a fire axe", ResourcePath('items/fire_axe.png').path, attack=10, damage=3, durability=20)       


class Shovel(Melee):
    """A pointed shovel with a long handle."""
    def __init__(self, character):
        super().__init__(character, ItemType.SHOVEL, "Shovel", "a shovel", ResourcePath('items/shovel.png').path, attack=10, damage=2, durability=20)      


class BaseballBat(Melee):
    """A blunt, wooden baseball bat."""
    def __init__(self, character):
        super().__init__(character, ItemType.BASEBALL_BAT, "Baseball Bat", "a baseball bat", ResourcePath('items/baseball_bat.png').path, attack=10, damage=2, durability=20)

                        
class GolfClub(Melee):
    """A 7-iron golf club."""
    def __init__(self, character):
        super().__init__(character, ItemType.GOLF_CLUB, "Golf Club", "a golf club", ResourcePath('items/golf_club.png').path, attack=10, damage=2, durability=20)


class HockeyStick(Melee):
    """A wooden hockey stick."""
    def __init__(self, character):
        super().__init__(character, ItemType.HOCKEY_STICK, "Hockey Stick", "a hockey stick", ResourcePath('items/hockey_stick.png').path, attack=10, damage=3, durability=20)


class TennisRacket(Melee):
    """A sporty tennis racket."""
    def __init__(self, character):
        super().__init__(character, ItemType.TENNIS_RACKET, "Tennis Racket", "a tennis racket", ResourcePath('items/tennis_racket.png').path, attack=5, damage=2, durability=20)                
    
