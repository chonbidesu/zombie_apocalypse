# settings.py
import pygame

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
FUEL_DURATION = 50
ZOMBIE_START_HP = 50

# Fonts
pygame.init()
font_small = pygame.font.SysFont(None, 16)
font_large = pygame.font.SysFont(None, 26)
font_chat = pygame.font.SysFont(None, 21)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (34, 51, 34)
ORANGE = (236, 88, 0)

ITEMS = {
    'First Aid Kit': {'image_file': 'assets/first_aid_kit.bmp'},
    'Portable Generator': {'image_file': 'assets/portable_generator.bmp'},
    'Fuel Can': {'image_file': 'assets/fuel_can.bmp'},
    'Map': {'image_file': 'assets/map.bmp'},
    'Shotgun Shell': {'image_file': 'assets/shotgun_shell.bmp'},
    'Pistol Clip': {'image_file': 'assets/pistol_clip.bmp'},
}

WEAPONS = {
    'Crowbar': {'image_file': 'assets/crowbar.bmp', 'damage': 8, 'durability': 100},
    'Fire Axe': {'image_file': 'assets/fire_axe.bmp', 'damage': 15, 'durability': 80},
    'Shovel': {'image_file': 'assets/shovel.bmp', 'damage': 10, 'durability': 90},
    'Shotgun': {'image_file': 'assets/shotgun.bmp', 'damage': 50, 'loaded_ammo': 2, 'max_ammo': 2},
    'Pistol': {'image_file': 'assets/pistol.bmp', 'damage': 20, 'loaded_ammo': 7, 'max_ammo': 7},
}

# Categorization for weapons
MELEE_WEAPONS = ['Crowbar', 'Fire Axe', 'Shovel']
FIREARMS = ['Shotgun', 'Pistol']

# Images for block sprites
BLOCK_IMAGES = {
    "FireStation": "assets/fire_station.bmp",
    "PoliceDepartment": "assets/police_department.bmp",
    "Street": "assets/streets.bmp",
    "Park": "assets/park.bmp",
    "Carpark": "assets/carpark.bmp",
    "Cemetery": "assets/cemetery.bmp",
    "Monument": "assets/monument.bmp",
    "Hospital": "assets/hospital.bmp",
    "Mall": "assets/mall.bmp",
    "Church": "assets/church.bmp",
    "Warehouse": "assets/warehouse.bmp",
    "Factory": "assets/factory.bmp",
    "School": "assets/school.bmp",
    "NecroTechLab": "assets/necrotech_lab.bmp",
    "Junkyard": "assets/junkyard.bmp",
    "Museum": "assets/museum.bmp",
    "Nightclub": "assets/nightclub.bmp",
    "Pub": "assets/pub.bmp",
    "Library": "assets/library.bmp",
    "AutoRepair": "assets/auto_repair.bmp",
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

BUILDING_TYPES = ['FireStation', 'PoliceDepartment', 'Hospital', 'Library', 'Church', 
                'Warehouse', 'AutoRepair', 'Factory', 'School', 'NecroTechLab', 
                'Junkyard', 'Museum', 'Nightclub', 'Pub', 'Mall']
OUTDOOR_TYPES = ['Street', 'Park', 'Cemetery', 'Monument', 'Carpark']

# Paths to block name files
BLOCKNAME_LISTS_FOLDER = "blockname_lists"
BLOCKNAME_FILES = {
    'Park': 'parks.txt',
    'Cemetery': 'cemeteries.txt',
    'Street': 'streets.txt',
    'Monument': 'monuments.txt',
    'Carpark': 'carparks.txt',
    'PoliceDepartment': 'police_departments.txt',
    'FireStation': 'fire_stations.txt',
    'Hospital': 'hospitals.txt',
    'Library': 'libraries.txt',
    'Mall': 'malls.txt',
    'Church': 'churches.txt',
    'Warehouse': 'warehouses.txt',
    'AutoRepair': 'auto_repairs.txt',
    'Factory': 'factories.txt',
    'School': 'schools.txt',
    'NecroTechLab': 'necrotech_labs.txt',
    'Junkyard': 'junkyards.txt',
    'Museum': 'museums.txt',
    'Nightclub': 'nightclubs.txt',
    'Pub': 'pubs.txt'
}

BLOCKNAME_DESC = {
    'Park': 'a park',
    'Cemetery': 'a cemetery',
    'Street': 'a street',
    'Monument': 'a monument',
    'Carpark': 'a carpark',
    'PoliceDepartment': 'a police department',
    'FireStation': 'a fire station',
    'Hospital': 'a hospital',
    'Library': 'a library',
    'Mall': 'a mall',
    'Church': 'a church',
    'Warehouse': 'a warehouse',
    'AutoRepair': 'an auto repair shop',
    'Factory': 'a factory',
    'School': 'a school',
    'NecroTechLab': 'a NecroTech lab',
    'Junkyard': 'a junkyard',
    'Museum': 'a museum',
    'Nightclub': 'a nightclub',
    'Pub': 'a pub'
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