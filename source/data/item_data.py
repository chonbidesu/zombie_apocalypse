# item_data.py

from enum import Enum, auto


class ItemType(Enum):
    FIRST_AID_KIT = auto()
    PORTABLE_GENERATOR = auto()
    FUEL_CAN = auto()
    MAP = auto()
    TOOLBOX = auto()
    BINOCULARS = auto()
    DNA_EXTRACTOR = auto()
    SYRINGE = auto()
    BEER = auto()
    WINE = auto()
    BOOK = auto()
    POETRY_BOOK = auto()
    CANDY = auto()
    CRUCIFIX = auto()
    GPS_UNIT = auto()
    NEWSPAPER = auto()
    SHOTGUN_SHELL = auto()
    PISTOL_CLIP = auto()
    KNIFE = auto()
    CROWBAR = auto()
    FIRE_AXE = auto()
    SHOVEL = auto()
    BASEBALL_BAT = auto()
    GOLF_CLUB = auto()
    HOCKEY_STICK = auto()
    TENNIS_RACKET = auto()
    SHOTGUN = auto()
    PISTOL = auto()


class ItemFunction(Enum):
    MISC = auto()
    AMMO = auto()
    MELEE = auto()
    FIREARM = auto()
    SCIENCE = auto()