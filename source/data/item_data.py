# item_data.py

from enum import Enum, auto
from collections import namedtuple

from data.path import ResourcePath


class ItemType(Enum):
    FIRST_AID_KIT = auto()
    PORTABLE_GENERATOR = auto()
    FUEL_CAN = auto()
    MAP = auto()
    TOOLBOX = auto()
    BINOCULARS = auto()
    DNA_EXTRACTOR = auto()
    SYRINGE = auto()
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
    ITEM = auto()
    AMMO = auto()
    MELEE = auto()
    FIREARM = auto()


ItemProperties = namedtuple(
    'ItemProperties', [
        'item_type', 'description', 'item_function', 'image_file', 'attack', 'damage', 'durability', 'max_ammo'
    ]
)

ITEMS = {
    ItemType.FIRST_AID_KIT: ItemProperties('First Aid Kit', 'a first aid kit', ItemFunction.ITEM, ResourcePath('assets/first_aid_kit.png').path, None, None, None, None),
    ItemType.PORTABLE_GENERATOR: ItemProperties('Portable Generator', 'a portable generator', ItemFunction.ITEM, ResourcePath('assets/portable_generator.png').path, None, None, None, None),
    ItemType.FUEL_CAN: ItemProperties('Fuel Can', 'a fuel can', ItemFunction.ITEM, ResourcePath('assets/fuel_can.png').path, None, None, None, None),
    ItemType.MAP: ItemProperties('Map', 'a map', ItemFunction.ITEM, ResourcePath('assets/map.png').path, None, None, None, None),
    ItemType.TOOLBOX: ItemProperties('Toolbox', 'a toolbox', ItemFunction.ITEM, ResourcePath('assets/toolbox.png').path, None, None, None, None),
    ItemType.BINOCULARS: ItemProperties('Binoculars', 'a pair of binoculars', ItemFunction.ITEM, ResourcePath('assets/binoculars.png').path, None, None, None, None),
    ItemType.DNA_EXTRACTOR: ItemProperties('DNA Extractor', 'a DNA extractor', ItemFunction.ITEM, ResourcePath('assets/dna_extractor.png').path, None, None, None, None),
    ItemType.SYRINGE: ItemProperties('NecroTech Syringe', 'a NecroTech revivification syringe', ItemFunction.ITEM, ResourcePath('assets/syringe.png').path, None, None, None, None),
    ItemType.SHOTGUN_SHELL: ItemProperties('Shotgun Shell', 'a shotgun shell', ItemFunction.AMMO, ResourcePath('assets/shotgun_shell.png').path, None, None, None, None),
    ItemType.PISTOL_CLIP: ItemProperties('Pistol Clip', 'a pistol clip', ItemFunction.AMMO, ResourcePath('assets/pistol_clip.png').path, None, None, None, None),
    ItemType.KNIFE: ItemProperties('Knife', 'a knife', ItemFunction.MELEE, ResourcePath('assets/knife.png').path, 20, 2, 75, None),
    ItemType.CROWBAR: ItemProperties('Crowbar', 'a crowbar', ItemFunction.MELEE, ResourcePath('assets/crowbar.png').path, 5, 2, 30, None),
    ItemType.FIRE_AXE: ItemProperties('Fire Axe', 'a fire axe', ItemFunction.MELEE, ResourcePath('assets/fire_axe.png').path, 10, 3, 20, None),
    ItemType.SHOVEL: ItemProperties('Shovel', 'a shovel', ItemFunction.MELEE, ResourcePath('assets/shovel.png').path, 10, 2, 20, None),
    ItemType.BASEBALL_BAT: ItemProperties('Baseball Bat', 'a baseball bat', ItemFunction.MELEE, ResourcePath('assets/baseball_bat.png').path, 10, 2, 20, None),
    ItemType.GOLF_CLUB: ItemProperties('Golf Club', 'a golf club', ItemFunction.MELEE, ResourcePath('assets/golf_club.png').path, 10, 2, 20, None),
    ItemType.HOCKEY_STICK: ItemProperties('Hockey Stick', 'a hockey stick', ItemFunction.MELEE, ResourcePath('assets/hockey_stick.png').path, 10, 3, 20, None),
    ItemType.TENNIS_RACKET: ItemProperties('Tennis Racket', 'a tennis racket', ItemFunction.MELEE, ResourcePath('assets/tennis_racket.png').path, 10, 2, 20, None),
    ItemType.SHOTGUN: ItemProperties('Shotgun', 'a shotgun', ItemFunction.FIREARM, ResourcePath('assets/shotgun.png').path, 5, 10, None, 2),
    ItemType.PISTOL: ItemProperties('Pistol', 'a pistol', ItemFunction.FIREARM, ResourcePath('assets/pistol.png').path, 5, 5, None, 6),
}