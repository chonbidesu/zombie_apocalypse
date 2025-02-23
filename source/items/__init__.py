# items.py

from enum import Enum, auto

from .ammo import ShotgunShell, PistolClip
from .firearm import Shotgun, Pistol
from .melee import Knife, Crowbar, FireAxe, Shovel, BaseballBat, GolfClub, HockeyStick, TennisRacket
from .misc import PortableGenerator, FuelCan, Toolbox, Consumable, Map, Binoculars, Book, PoetryBook, Crucifix, GPSUnit, Newspaper
from .science import DNAExtractor, Syringe, FirstAidKit
from .base_classes import ItemFunction