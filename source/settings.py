# settings.py
import pygame
from enum import Enum, auto
from collections import namedtuple
import os
import sys

# Define resource path function
def resource_path(relative_path):
    """Get the absolute path to a resource, working for both dev & PyInstaller."""
    if hasattr(sys, '_MEIPASS'):  # PyInstaller extracts files here in --onefile mode
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# Saved game file
SAVE_FILE = "savegame.pkl"

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

# Grid and tile settings
VIEWPORT_SIZE = 3  # 3x3 viewport
CITY_SIZE = 100  # 100x100 city grid
NEIGHBOURHOOD_SIZE = 10  # 10x10 neighbourhoods
BLOCK_SIZE = SCREEN_HEIGHT * 7 // 54

# Game settings
FPS = 30
FONT_SIZE = 16
CHAT_HEIGHT = SCREEN_HEIGHT * 1 // 4
CHAT_LINES = 10

# Gameplay
FUEL_DURATION = 200
MAX_ITEMS = 10
ATTACK_DIFFICULTY = 15
MAX_HP = 50
ZOMBIE_CAPACITY = 6 # Limit of zombies per block
HUMAN_CAPACITY = 2 # Limit of humans per block
ZOMBIE_DAMAGE = 4
STAND_AP = 50
SEARCH_MULTIPLIER = 1.0
LIGHTSON_MULTIPLIER = 2.5
RANSACKED_MULTIPLIER = 0.3
MAX_ITEMS = 10  # Define the maximum number of items in inventory
MAX_ITEMS_PER_ROW = 5

# Fonts
pygame.init()
font_xs = pygame.font.Font(resource_path('data/PixelifySans.ttf'), 10)
font_small = pygame.font.Font(resource_path('data/PixelifySans.ttf'), 12)
font_large = pygame.font.Font(resource_path('data/PixelifySans.ttf'), 18)
font_xl = pygame.font.Font(resource_path('data/PixelifySans.ttf'), 56)
font_xxl = pygame.font.Font(resource_path('data/PixelifySans.ttf'), 102)
font_chat = pygame.font.Font(resource_path('data/PixelifySans.ttf'), 16)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (34, 51, 34)
ORANGE = (236, 88, 0)
TRANS_YELLOW = (251, 232, 2, 64)
PALE_YELLOW = (255, 255, 150)

# Item Settings
class ItemType(Enum):
    FIRST_AID_KIT = auto()
    PORTABLE_GENERATOR = auto()
    FUEL_CAN = auto()
    MAP = auto()
    TOOLBOX = auto()
    SHOTGUN_SHELL = auto()
    PISTOL_CLIP = auto()
    CROWBAR = auto()
    FIRE_AXE = auto()
    SHOVEL = auto()
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
    ItemType.FIRST_AID_KIT: ItemProperties('First Aid Kit', 'a first aid kit', ItemFunction.ITEM, resource_path('assets/first_aid_kit.png'), None, None, None, None),
    ItemType.PORTABLE_GENERATOR: ItemProperties('Portable Generator', 'a portable generator', ItemFunction.ITEM, resource_path('assets/portable_generator.png'), None, None, None, None),
    ItemType.FUEL_CAN: ItemProperties('Fuel Can', 'a fuel can', ItemFunction.ITEM, resource_path('assets/fuel_can.png'), None, None, None, None),
    ItemType.MAP: ItemProperties('Map', 'a map', ItemFunction.ITEM, resource_path('assets/map.png'), None, None, None, None),
    ItemType.TOOLBOX: ItemProperties('Toolbox', 'a toolbox', ItemFunction.ITEM, resource_path('assets/toolbox.png'), None, None, None, None),
    ItemType.SHOTGUN_SHELL: ItemProperties('Shotgun Shell', 'a shotgun shell', ItemFunction.AMMO, resource_path('assets/shotgun_shell.png'), None, None, None, None),
    ItemType.PISTOL_CLIP: ItemProperties('Pistol Clip', 'a pistol clip', ItemFunction.AMMO, resource_path('assets/pistol_clip.png'), None, None, None, None),
    ItemType.CROWBAR: ItemProperties('Crowbar', 'a crowbar', ItemFunction.MELEE, resource_path('assets/crowbar.png'), 5, 3, 30, None),
    ItemType.FIRE_AXE: ItemProperties('Fire Axe', 'a fire axe', ItemFunction.MELEE, resource_path('assets/fire_axe.png'), 5, 4, 20, None),
    ItemType.SHOVEL: ItemProperties('Shovel', 'a shovel', ItemFunction.MELEE, resource_path('assets/shovel.png'), 5, 2, 20, None),
    ItemType.SHOTGUN: ItemProperties('Shotgun', 'a shotgun', ItemFunction.FIREARM, resource_path('assets/shotgun.png'), 4, 20, None, 2),
    ItemType.PISTOL: ItemProperties('Pistol', 'a pistol', ItemFunction.FIREARM, resource_path('assets/pistol.png'), 2, 8, None, 7),
}

# NPC types
class NPCType(Enum):
    SURVIVOR = auto()
    PREPPER = auto()
    SCIENTIST = auto()
    PKER = auto()

# City block settings
class BlockType(Enum):
    FIRE_STATION = auto()
    POLICE_DEPARTMENT = auto()
    HOSPITAL = auto()
    LIBRARY = auto()
    CHURCH = auto()
    WAREHOUSE = auto()
    AUTO_REPAIR = auto()
    FACTORY = auto()
    SCHOOL = auto()
    NECROTECH_LAB = auto() 
    JUNKYARD = auto()
    MUSEUM = auto()
    NIGHTCLUB = auto()
    PUB = auto()
    MALL = auto()

    STREET = auto()
    PARK = auto()
    CEMETERY = auto()
    MONUMENT = auto()
    CARPARK = auto()


BlockProperties = namedtuple(
    'BlockProperties', ['description', 'is_building', 'image_file']
)

BLOCKS = {
    BlockType.FIRE_STATION: BlockProperties("a fire station", True, resource_path("assets/fire_station.bmp")),
    BlockType.POLICE_DEPARTMENT: BlockProperties("a police department", True, resource_path("assets/police_department.bmp")),
    BlockType.HOSPITAL: BlockProperties("a hospital", True, resource_path("assets/hospital.bmp")),
    BlockType.LIBRARY: BlockProperties("a library", True, resource_path("assets/library.bmp")),
    BlockType.CHURCH: BlockProperties("a church", True, resource_path("assets/church.bmp")),
    BlockType.WAREHOUSE: BlockProperties("a warehouse", True, resource_path("assets/warehouse.bmp")),
    BlockType.AUTO_REPAIR: BlockProperties("an auto repair shop", True, resource_path("assets/auto_repair.bmp")),
    BlockType.FACTORY: BlockProperties("a factory", True, resource_path("assets/factory.bmp")),
    BlockType.SCHOOL: BlockProperties("a school", True, resource_path("assets/school.bmp")),
    BlockType.NECROTECH_LAB: BlockProperties("a NecroTech lab", True, resource_path("assets/necrotech_lab.bmp")),
    BlockType.JUNKYARD: BlockProperties("a junkyard", True, resource_path("assets/junkyard.bmp")),
    BlockType.MUSEUM: BlockProperties("a museum", True, resource_path("assets/museum.bmp")),
    BlockType.NIGHTCLUB: BlockProperties("a nightclub", True, resource_path("assets/nightclub.bmp")),
    BlockType.PUB: BlockProperties("a pub", True, resource_path("assets/pub.bmp")),
    BlockType.MALL: BlockProperties("a mall", True, resource_path("assets/mall.bmp")),

    BlockType.STREET: BlockProperties("a street", False, resource_path("assets/streets.bmp")),
    BlockType.PARK: BlockProperties("a park", False, resource_path("assets/park.bmp")),
    BlockType.CEMETERY: BlockProperties("a cemetery", False, resource_path("assets/cemetery.bmp")),
    BlockType.MONUMENT: BlockProperties("a monument", False, resource_path("assets/monument.bmp")),
    BlockType.CARPARK: BlockProperties("a carpark", False, resource_path("assets/carpark.bmp")),
}


# Barricade states
class BarricadeState(Enum):
    NOT_BARRICADED = auto()
    LOOSELY_BARRICADED = auto()
    LIGHTLY_BARRICADED = auto()
    QUITE_STRONGLY_BARRICADED = auto()
    VERY_STRONGLY_BARRICADED = auto()
    HEAVILY_BARRICADED = auto()
    VERY_HEAVILY_BARRICADED = auto()
    EXTREMELY_HEAVILY_BARRICADED = auto()


BARRICADE_DESCRIPTIONS = {
    BarricadeState.NOT_BARRICADED: "not barricaded",
    BarricadeState.LOOSELY_BARRICADED: "loosely barricaded",
    BarricadeState.LIGHTLY_BARRICADED: "lightly barricaded",
    BarricadeState.QUITE_STRONGLY_BARRICADED: " quite strongly barricaded",
    BarricadeState.VERY_STRONGLY_BARRICADED: "very strongly barricaded",
    BarricadeState.HEAVILY_BARRICADED: "heavily barricaded",
    BarricadeState.VERY_HEAVILY_BARRICADED: "very heavily barricaded",
    BarricadeState.EXTREMELY_HEAVILY_BARRICADED: "extremely heavily barricaded"
}

# List of neighbourhoods
NEIGHBOURHOODS = [
    "Dakerstown", "Jensentown", "Quarlesbank", "West Boundwood", "East Boundwood",
    "Lamport Hills", "Chancelwood", "Earletown", "Rhodenbank", "Dulston",
    "Roywood", "Judgewood", "Gatcombeton", "Shuttlebank", "Yagoton",
    "Millen Hills", "Raines Hills", "Pashenton", "Rolt Heights", "Pescodside",
    "Peddlesden Village", "Chudleyton", "Darvall Heights", "Eastonwood", "Brooke Hills",
    "Shearbank", "Huntley Heights", "Santlerville", "Gibsonton", "Dunningwood",
    "Dunell Hills", "West Becktown", "East Becktown", "Richmond Hills", "Ketchelbank",
    "Roachtown", "Randallbank", "Heytown", "Spracklingbank", "Paynterton",
    "Owsleybank", "Molebank", "Lukinswood", "Havercroft", "Barrville",
    "Ridleybank", "Pimbank", "Peppardville", "Pitneybank", "Starlingtown",
    "Grigg Heights", "Reganbank", "Lerwill Heights", "Shore Hills", "Galbraith Hills",
    "Stanbury Village", "Roftwood", "Edgecombe", "Pegton", "Dentonside",
    "Crooketon", "Mornington", "North Blythville", "Brooksville", "Mockridge Heights",
    "Shackleville", "Tollyton", "Crowbank", "Vinetown", "Houldenbank",
    "Nixbank", "Wykewood", "South Blythville", "Greentown", "Tapton",
    "Kempsterbank", "Wray Heights", "Gulsonside", "Osmondville", "Penny Heights",
    "Foulkes Village", "Ruddlebank", "Lockettside", "Dartside", "Kinch Heights",
    "West Grayside", "East Grayside", "Scarletwood", "Pennville", "Fryerbank",
    "New Arkham", "Old Arkham", "Spicer Hills", "Williamsville", "Buttonville",
    "Wyke Hills", "Hollomstown", "Danversbank", "Whittenside", "Miltown"
]

