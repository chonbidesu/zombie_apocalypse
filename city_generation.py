# city_generation.py
import csv
import random
from collections import defaultdict
from pathlib import Path
from blocks import CityBlock, BuildingBlock
from settings import *

# Load descriptive phrases of city blocks from CSV file for assembly
def load_descriptions_from_csv(file_path):
    descriptions = defaultdict(lambda: {"inside": defaultdict(list), "outside": defaultdict(list)})
    with open(file_path, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            block_type = row["BlockType"]
            description_type = row["DescriptionType"]
            position = row["SentencePosition"]
            phrase = row["Phrase"]
            descriptions[block_type][description_type][position].append(phrase)
    return descriptions

# Load block names from files
block_name_pool = {}

# Load descriptions
descriptions = load_descriptions_from_csv("assets/descriptions.csv")

def _load_block_names():
    """Load block names from text files into a dictionary."""
    for block_type, filename in BLOCKNAME_FILES.items():
        filepath = Path(f"{BLOCKNAME_LISTS_FOLDER}/{filename}")
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                contents = f.read()
            names = contents.splitlines()
            block_name_pool[block_type] = names
        else:
            print(f"Warning: {filepath} does not exist!")


def _get_unique_block_name(block_type):
    """Retrieve a block name for the given type."""
    block_type = block_type
    if block_name_pool[block_type]:
        name = random.choice(block_name_pool[block_type])
        return name
    else:
        return f"{block_type} (Generic)"  # Fallback if no names are left

def _generate_neighbourhood(neighbourhood_name):
    """Generate a 10x10 neighbourhood grid with a mix of block types."""
    grid = []

    building_types = ['FireStation', 'PoliceDepartment', 'Hospital', 'Library', 'Church', 
                      'Warehouse', 'AutoRepair', 'Factory', 'School', 'NecroTechLab', 
                      'Junkyard', 'Museum', 'Nightclub', 'Pub']
    outdoor_types = ['Street', 'Park', 'Cemetery', 'Monument', 'Carpark']

    # Create a pool of random blocks, ensuring malls have a smaller chance of appearing
    block_pool = []
    for _ in range(50):  # Creating 50 random buildings
        block_type = random.choice(['Mall'] + (building_types * 4))
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        building_block = BuildingBlock(block_type)
        building_block.block_name = block_name
        building_block.block_desc = block_desc
        building_block.generate_descriptions(descriptions)
        block_pool.append(building_block)

    for _ in range(50):  # Creating 50 random outdoor spaces
        block_type = random.choice(['Street'] * 12 + outdoor_types)
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        city_block = CityBlock(block_type)
        city_block.block_name = block_name
        city_block.block_desc = block_desc
        city_block.generate_descriptions(descriptions)
        block_pool.append(city_block)

    random.shuffle(block_pool)

    # Now, randomly place blocks into a 10x10 grid
    for y in range(10):
        row = []
        for x in range(10):
            block = block_pool.pop()
            row.append(block)
        grid.append(row)

    # Implement mall spreading logic
    for y in range(10):
        for x in range(10):
            block = grid[y][x]
            if block.block_type == 'Mall':
                # Try to expand the mall to adjacent blocks
                if x + 1 < 10 and y + 1 < 10 and grid[y][x + 1].block_type == 'Street' and grid[y + 1][x].block_type == 'Street':
                    grid[y][x + 1].block_type = block.block_type
                    grid[y + 1][x].block_type = block.block_type
                    grid[y][x + 1].block_name = block.block_name
                    grid[y + 1][x].block_name = block.block_name
                    grid[y][x + 1].block_desc = block.block_desc
                    grid[y + 1][x].block_desc = block.block_desc
                elif x + 1 < 10 and grid[y][x + 1].block_type == 'Street':
                    grid[y][x + 1].block_type = block.block_type
                    grid[y][x + 1].block_name = block.block_name
                    grid[y][x + 1].block_desc = block.block_desc
                elif y + 1 < 10 and grid[y + 1][x].block_type == 'Street':
                    grid[y + 1][x].block_type = block.block_type
                    grid[y + 1][x].block_name = block.block_name
                    grid[y + 1][x].block_desc = block.block_desc
    return grid


def generate_city():
    """Generate the entire 100x100 city as a grid of neighbourhoods."""
    _load_block_names()

    city = [[None for _ in range(100)] for _ in range(100)]

    for neighbourhood_index, neighbourhood_name in NEIGHBOURHOODS.items():
        top_left_x = ((neighbourhood_index - 1) % 10) * 10
        top_left_y = ((neighbourhood_index - 1) // 10) * 10

        neighbourhood_grid = _generate_neighbourhood(neighbourhood_name)
        for y in range(10):
            for x in range(10):
                city[top_left_y + y][top_left_x + x] = neighbourhood_grid[y][x]

    return city

# Store zoom coordinates for street blocks to give streets variety
def initialize_zoom_coordinates(city):
    for row in city:
        for block in row:
            if block.block_type == "Street":
                image_width, image_height = 200, 200
                zoom_factor = 2
                zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor
                
                # Precompute random zoom position
                block.zoom_x = random.randint(0, image_width - zoom_width)
                block.zoom_y = random.randint(0, image_height - zoom_height)