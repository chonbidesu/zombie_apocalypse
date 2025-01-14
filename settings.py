# settings.py
import pygame
from enum import Enum, auto
from collections import namedtuple

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
BARRICADE_CHANCE = 0.5
FUEL_DURATION = 200
MAX_ITEMS = 10
ATTACK_DIFFICULTY = 15
ZOMBIE_MAX_HP = 50
ZOMBIE_CAPACITY = 6 # Limit of zombies per block
ZOMBIE_DAMAGE = 4
STAND_UP_AP = 50
SEARCH_MULTIPLIER = 1.0
LIGHTSON_MULTIPLIER = 2.5
RANSACKED_MULTIPLIER = 0.3

# Fonts
pygame.init()
font_xs = pygame.font.SysFont(None, 12)
font_small = pygame.font.SysFont(None, 16)
font_large = pygame.font.SysFont(None, 26)
font_xl = pygame.font.SysFont(None, 56)
font_xxl = pygame.font.SysFont(None, 102)
font_chat = pygame.font.SysFont(None, 21)

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
    ItemType.FIRST_AID_KIT: ItemProperties('First Aid Kit', 'a first aid kit', ItemFunction.ITEM, 'assets/first_aid_kit.png', None, None, None, None),
    ItemType.PORTABLE_GENERATOR: ItemProperties('Portable Generator', 'a portable generator', ItemFunction.ITEM, 'assets/portable_generator.png', None, None, None, None),
    ItemType.FUEL_CAN: ItemProperties('Fuel Can', 'a fuel can', ItemFunction.ITEM, 'assets/fuel_can.png', None, None, None, None),
    ItemType.MAP: ItemProperties('Map', 'a map', ItemFunction.ITEM, 'assets/map.png', None, None, None, None),
    ItemType.TOOLBOX: ItemProperties('Toolbox', 'a toolbox', ItemFunction.ITEM, 'assets/toolbox.png', None, None, None, None),
    ItemType.SHOTGUN_SHELL: ItemProperties('Shotgun Shell', 'a shotgun shell', ItemFunction.AMMO, 'assets/shotgun_shell.png', None, None, None, None),
    ItemType.PISTOL_CLIP: ItemProperties('Pistol Clip', 'a pistol clip', ItemFunction.AMMO, 'assets/pistol_clip.png', None, None, None, None),
    ItemType.CROWBAR: ItemProperties('Crowbar', 'a crowbar', ItemFunction.MELEE, 'assets/crowbar.png', 5, 3, 30, None),
    ItemType.FIRE_AXE: ItemProperties('Fire Axe', 'a fire axe', ItemFunction.MELEE, 'assets/fire_axe.png', 5, 4, 20, None),
    ItemType.SHOVEL: ItemProperties('Shovel', 'a shovel', ItemFunction.MELEE, 'assets/shovel.png', 5, 2, 20, None),
    ItemType.SHOTGUN: ItemProperties('Shotgun', 'a shotgun', ItemFunction.FIREARM, 'assets/shotgun.png', 4, 20, None, 2),
    ItemType.PISTOL: ItemProperties('Pistol', 'a pistol', ItemFunction.FIREARM, 'assets/pistol.png', 2, 8, None, 7),
}


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
    BlockType.FIRE_STATION: BlockProperties("a fire station", True, "assets/fire_station.bmp"),
    BlockType.POLICE_DEPARTMENT: BlockProperties("a police department", True, "assets/police_department.bmp"),
    BlockType.HOSPITAL: BlockProperties("a hospital", True, "assets/hospital.bmp"),
    BlockType.LIBRARY: BlockProperties("a library", True, "assets/library.bmp"),
    BlockType.CHURCH: BlockProperties("a church", True, "assets/church.bmp"),
    BlockType.WAREHOUSE: BlockProperties("a warehouse", True, "assets/warehouse.bmp"),
    BlockType.AUTO_REPAIR: BlockProperties("an auto repair shop", True, "assets/auto_repair.bmp"),
    BlockType.FACTORY: BlockProperties("a factory", True, "assets/factory.bmp"),
    BlockType.SCHOOL: BlockProperties("a school", True, "assets/school.bmp"),
    BlockType.NECROTECH_LAB: BlockProperties("a NecroTech lab", True, "assets/necrotech_lab.bmp"),
    BlockType.JUNKYARD: BlockProperties("a junkyard", True, "assets/junkyard.bmp"),
    BlockType.MUSEUM: BlockProperties("a museum", True, "assets/museum.bmp"),
    BlockType.NIGHTCLUB: BlockProperties("a nightclub", True, "assets/nightclub.bmp"),
    BlockType.PUB: BlockProperties("a pub", True, "assets/pub.bmp"),
    BlockType.MALL: BlockProperties("a mall", True, "assets/mall.bmp"),

    BlockType.STREET: BlockProperties("a street", False, "assets/streets.bmp"),
    BlockType.PARK: BlockProperties("a park", False, "assets/park.bmp"),
    BlockType.CEMETERY: BlockProperties("a cemetery", False, "assets/cemetery.bmp"),
    BlockType.MONUMENT: BlockProperties("a monument", False, "assets/monument.bmp"),
    BlockType.CARPARK: BlockProperties("a carpark", False, "assets/carpark.bmp"),
}


# Barricade states
class BarricadeState(Enum):
    NOT_BARRICADED = auto()
    LOOSELY_BARRICADED = auto()
    LIGHTLY_BARRICADED = auto()
    STRONGLY_BARRICADED = auto()
    VERY_STRONGLY_BARRICADED = auto()
    HEAVILY_BARRICADED = auto()
    VERY_HEAVILY_BARRICADED = auto()
    EXTREMELY_HEAVILY_BARRICADED = auto()


BARRICADE_DESCRIPTIONS = {
    BarricadeState.NOT_BARRICADED: "not barricaded",
    BarricadeState.LOOSELY_BARRICADED: "loosely barricaded",
    BarricadeState.LIGHTLY_BARRICADED: "lightly barricaded",
    BarricadeState.STRONGLY_BARRICADED: "strongly barricaded",
    BarricadeState.VERY_STRONGLY_BARRICADED: "very strongly barricaded",
    BarricadeState.HEAVILY_BARRICADED: "heavily barricaded",
    BarricadeState.VERY_HEAVILY_BARRICADED: "very heavily barricaded",
    BarricadeState.EXTREMELY_HEAVILY_BARRICADED: "extremely heavily barricaded"
}

# List of neighbourhoods
NEIGHBOURHOODS = {
    1: "Dakerstown",
    2: "Jensentown",
    3: "Quarlesbank",
    4: "West Boundwood",
    5: "East Boundwood",
    6: "Lamport Hills",
    7: "Chancelwood",
    8: "Earletown",
    9: "Rhodenbank",
    10: "Dulston",
    11: "Roywood",
    12: "Judgewood",
    13: "Gatcombeton",
    14: "Shuttlebank",
    15: "Yagoton",
    16: "Millen Hills",
    17: "Raines Hills",
    18: "Pashenton",
    19: "Rolt Heights",
    20: "Pescodside",
    21: "Peddlesden Village",
    22: "Chudleyton",
    23: "Darvall Heights",
    24: "Eastonwood",
    25: "Brooke Hills",
    26: "Shearbank",
    27: "Huntley Heights",
    28: "Santlerville",
    29: "Gibsonton",
    30: "Dunningwood",
    31: "Dunell Hills",
    32: "West Becktown",
    33: "East Becktown",
    34: "Richmond Hills",
    35: "Ketchelbank",
    36: "Roachtown",
    37: "Randallbank",
    38: "Heytown",
    39: "Spracklingbank",
    40: "Paynterton",
    41: "Owsleybank",
    42: "Molebank",
    43: "Lukinswood",
    44: "Havercroft",
    45: "Barrville",
    46: "Ridleybank",
    47: "Pimbank",
    48: "Peppardville",
    49: "Pitneybank",
    50: "Starlingtown",
    51: "Grigg Heights",
    52: "Reganbank",
    53: "Lerwill Heights",
    54: "Shore Hills",
    55: "Galbraith Hills",
    56: "Stanbury Village",
    57: "Roftwood",
    58: "Edgecombe",
    59: "Pegton",
    60: "Dentonside",
    61: "Crooketon",
    62: "Mornington",
    63: "North Blythville",
    64: "Brooksville",
    65: "Mockridge Heights",
    66: "Shackleville",
    67: "Tollyton",
    68: "Crowbank",
    69: "Vinetown",
    70: "Houldenbank",
    71: "Nixbank",
    72: "Wykewood",
    73: "South Blythville",
    74: "Greentown",
    75: "Tapton",
    76: "Kempsterbank",
    77: "Wray Heights",
    78: "Gulsonside",
    79: "Osmondville",
    80: "Penny Heights",
    81: "Foulkes Village",
    82: "Ruddlebank",
    83: "Lockettside",
    84: "Dartside",
    85: "Kinch Heights",
    86: "West Grayside",
    87: "East Grayside",
    88: "Scarletwood",
    89: "Pennville",
    90: "Fryerbank",
    91: "New Arkham",
    92: "Old Arkham",
    93: "Spicer Hills",
    94: "Williamsville",
    95: "Buttonville",
    96: "Wyke Hills",
    97: "Hollomstown",
    98: "Danversbank",
    99: "Whittenside",
    100: "Miltown"
}

# Human Skills
HUMAN_SKILLS = [
    "Firearms Training",
    "Hand-to-Hand Combat",
    "First Aid",
    "Construction",
    "Body Building",
    "Scavenging",
    "Diplomacy",
]

# Zombie Skills
ZOMBIE_SKILLS = [
    "Scent Enhancement",
    "Infectious Bite",
    "Vigour Mortis",
    "Death Grip",
    "Ransack",
    "Lurching Gait",
    "Feeding Frenzy",
]