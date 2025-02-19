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
    ITEM = auto()
    AMMO = auto()
    MELEE = auto()
    FIREARM = auto()
    SCIENCE = auto()


ItemProperties = namedtuple(
    'ItemProperties', [
        'item_type', 'description', 'item_function', 'image_file', 'attack', 'damage', 'durability', 'max_ammo'
    ]
)

ITEMS = {
    ItemType.FIRST_AID_KIT: ItemProperties('First Aid Kit', 'a first aid kit', ItemFunction.SCIENCE, ResourcePath('items/first_aid_kit.png').path, None, None, None, None),
    ItemType.PORTABLE_GENERATOR: ItemProperties('Portable Generator', 'a portable generator', ItemFunction.ITEM, ResourcePath('items/portable_generator.png').path, None, None, None, None),
    ItemType.FUEL_CAN: ItemProperties('Fuel Can', 'a fuel can', ItemFunction.ITEM, ResourcePath('items/fuel_can.png').path, None, None, None, None),
    ItemType.MAP: ItemProperties('Map', 'a map', ItemFunction.ITEM, ResourcePath('items/map.png').path, None, None, None, None),
    ItemType.TOOLBOX: ItemProperties('Toolbox', 'a toolbox', ItemFunction.ITEM, ResourcePath('items/toolbox.png').path, None, None, None, None),
    ItemType.BINOCULARS: ItemProperties('Binoculars', 'a pair of binoculars', ItemFunction.ITEM, ResourcePath('items/binoculars.png').path, None, None, None, None),
    ItemType.DNA_EXTRACTOR: ItemProperties('DNA Extractor', 'a DNA extractor', ItemFunction.SCIENCE, ResourcePath('items/dna_extractor.png').path, None, None, None, None),
    ItemType.SYRINGE: ItemProperties('NecroTech Syringe', 'a NecroTech revivification syringe', ItemFunction.SCIENCE, ResourcePath('items/syringe.png').path, None, None, None, None),
    ItemType.BEER: ItemProperties('Beer', 'a can of beer', ItemFunction.ITEM, ResourcePath('items/beer.png').path, None, None, None, None),
    ItemType.WINE: ItemProperties('Wine', 'a bottle of wine', ItemFunction.ITEM, ResourcePath('items/wine.png').path, None, None, None, None),
    ItemType.BOOK: ItemProperties('Book', 'a book', ItemFunction.ITEM, ResourcePath('items/book.png').path, None, None, None, None),
    ItemType.POETRY_BOOK: ItemProperties('Poetry Book', 'a book of poetry', ItemFunction.ITEM, ResourcePath('items/poetry_book.png').path, None, None, None, None),
    ItemType.CANDY: ItemProperties('Candy', 'a stale piece of candy', ItemFunction.ITEM, ResourcePath('items/candy.png').path, None, None, None, None),
    ItemType.CRUCIFIX: ItemProperties('Crucifix', 'a crucifix', ItemFunction.ITEM, ResourcePath('items/crucifix.png').path, None, None, None, None),
    ItemType.GPS_UNIT: ItemProperties('GPS Unit', 'a GPS unit', ItemFunction.ITEM, ResourcePath('items/gps_unit.png').path, None, None, None, None),
    ItemType.NEWSPAPER: ItemProperties('Newspaper', 'a newspaper', ItemFunction.ITEM, ResourcePath('items/newspaper.png').path, None, None, None, None),
    ItemType.SHOTGUN_SHELL: ItemProperties('Shotgun Shell', 'a shotgun shell', ItemFunction.AMMO, ResourcePath('items/shotgun_shell.png').path, None, None, None, None),
    ItemType.PISTOL_CLIP: ItemProperties('Pistol Clip', 'a pistol clip', ItemFunction.AMMO, ResourcePath('items/pistol_clip.png').path, None, None, None, None),
    ItemType.KNIFE: ItemProperties('Knife', 'a knife', ItemFunction.MELEE, ResourcePath('items/knife.png').path, 20, 2, 75, None),
    ItemType.CROWBAR: ItemProperties('Crowbar', 'a crowbar', ItemFunction.MELEE, ResourcePath('items/crowbar.png').path, 5, 2, 30, None),
    ItemType.FIRE_AXE: ItemProperties('Fire Axe', 'a fire axe', ItemFunction.MELEE, ResourcePath('items/fire_axe.png').path, 10, 3, 20, None),
    ItemType.SHOVEL: ItemProperties('Shovel', 'a shovel', ItemFunction.MELEE, ResourcePath('items/shovel.png').path, 10, 2, 20, None),
    ItemType.BASEBALL_BAT: ItemProperties('Baseball Bat', 'a baseball bat', ItemFunction.MELEE, ResourcePath('items/baseball_bat.png').path, 10, 2, 20, None),
    ItemType.GOLF_CLUB: ItemProperties('Golf Club', 'a golf club', ItemFunction.MELEE, ResourcePath('items/golf_club.png').path, 10, 2, 20, None),
    ItemType.HOCKEY_STICK: ItemProperties('Hockey Stick', 'a hockey stick', ItemFunction.MELEE, ResourcePath('items/hockey_stick.png').path, 10, 3, 20, None),
    ItemType.TENNIS_RACKET: ItemProperties('Tennis Racket', 'a tennis racket', ItemFunction.MELEE, ResourcePath('items/tennis_racket.png').path, 10, 2, 20, None),
    ItemType.SHOTGUN: ItemProperties('Shotgun', 'a shotgun', ItemFunction.FIREARM, ResourcePath('items/shotgun.png').path, 5, 10, None, 2),
    ItemType.PISTOL: ItemProperties('Pistol', 'a pistol', ItemFunction.FIREARM, ResourcePath('items/pistol.png').path, 5, 5, None, 6),
}