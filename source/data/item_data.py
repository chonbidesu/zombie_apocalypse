# item_data.py

from enum import Enum, auto

from data.path import ResourcePath
from items import (FirstAidKit, PortableGenerator, FuelCan, Map, Toolbox, Binoculars, DNAExtractor, Syringe, Consumable, Book, PoetryBook, Crucifix, GPSUnit, Newspaper, 
                    ShotgunShell, PistolClip, Shotgun, Pistol, Knife, Crowbar, FireAxe, Shovel, BaseballBat, GolfClub, HockeyStick, TennisRacket, 
)


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


ITEMS = {
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