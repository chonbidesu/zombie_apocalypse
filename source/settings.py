# settings.py

import pygame
from data import DataPath

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
FPS = 60
FONT_SIZE = 16
CHAT_HEIGHT = SCREEN_HEIGHT * 1 // 4
CHAT_LINES = 10
ACTION_INTERVAL = 1500 # Time between actions in milliseconds

# Gameplay
FUEL_DURATION = 200
MAX_ITEMS = 10
ATTACK_DIFFICULTY = 10
MAX_HP = 50
BLOCK_CAPACITY = 8 # Limit of characters per block
STAND_AP = 50
SEARCH_MULTIPLIER = 1.0
LIGHTSON_MULTIPLIER = 2.5
RANSACKED_MULTIPLIER = 0.3
MAX_ITEMS = 10  # Define the maximum number of items in inventory
MAX_ITEMS_PER_ROW = 5

# Zombie attacks
ZOMBIE_ATTACKS = {
    'hands': {'attack': 25, 'damage': 2},
    'teeth': {'attack': 10, 'damage': 4}
}

# Fonts
pygame.init()
font_xs = pygame.font.Font(DataPath('fonts/PixelifySans.ttf').path, 10)
font_small = pygame.font.Font(DataPath('fonts/PixelifySans.ttf').path, 12)
font_large = pygame.font.Font(DataPath('fonts/PixelifySans.ttf').path, 18)
font_xl = pygame.font.Font(DataPath('fonts/PixelifySans.ttf').path, 56)
font_xxl = pygame.font.Font(DataPath('fonts/PixelifySans.ttf').path, 102)
font_chat = pygame.font.Font(DataPath('fonts/PixelifySans.ttf').path, 16)
font_skills = pygame.font.SysFont("Courier New", 16)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
LIGHT_GRAY = (175, 175, 175)
MED_GRAY = (125, 125, 125)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (34, 51, 34)
ORANGE = (236, 88, 0)
TRANS_YELLOW = (251, 232, 2, 64)
PALE_YELLOW = (255, 255, 150)
RED = (255, 0, 0)