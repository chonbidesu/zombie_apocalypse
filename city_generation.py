# city_generation.py
import csv
import random
import pygame
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

# Create groups to manage block types
building_types = ['FireStation', 'PoliceDepartment', 'Hospital', 'Library', 'Church', 
                      'Warehouse', 'AutoRepair', 'Factory', 'School', 'NecroTechLab', 
                      'Junkyard', 'Museum', 'Nightclub', 'Pub', 'Mall']
building_type_groups = {block_type: pygame.sprite.Group() for block_type in building_types}
building_group = pygame.sprite.Group()
outdoor_types = ['Street', 'Park', 'Cemetery', 'Monument', 'Carpark']
outdoor_type_groups = {block_type: pygame.sprite.Group() for block_type in outdoor_types}
outdoor_group = pygame.sprite.Group()

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

def generate_city(x_groups, y_groups):
    """Generate a 100x100 grid of block sprites"""
    _load_block_names()
    block_pool = []

    # Generate 500 building blocks
    for _ in range(500):
        building_block = BuildingBlock()
        building_group.add(building_block)
        block_type = random.choice(building_types)
        building_type_groups[block_type].add(building_block)
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        building_block.block_name = block_name
        building_block.block_desc = block_desc
        building_block.generate_descriptions(descriptions)
        block_pool.append(building_block)

    # Generate 500 outdoor blocks
    for _ in range(500):
        outdoor_block = CityBlock()
        outdoor_group.add(outdoor_block)
        block_type = random.choice(outdoor_types)
        outdoor_type_groups[block_type].add(outdoor_block)
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        outdoor_block.block_name = block_name
        outdoor_block.block_desc = block_desc
        outdoor_block.generate_descriptions(descriptions)
        block_pool.append(outdoor_block)

    random.shuffle(block_pool)

    # Now, randomly place blocks into a 100x100 grid
    for y in range(100):
        for x in range(100):
            block = block_pool.pop()
            x_groups[x].add(block)
            y_groups[y].add(block)

    # Implement mall spreading logic
    for y, row in y_groups.items():
        for x, block in x_groups.items():
            if block in building_type_groups['Mall']:
                # Try to expand the mall to adjacent blocks
                # Right neighbour
                if x + 1 in x_groups and y in y_groups and \
                        x_groups[x + 1] in outdoor_type_groups['Street']:
                    right_block = x_groups[x + 1]
                    outdoor_type_groups['Street'].remove(right_block)
                    outdoor_group.remove(right_block)
                    building_type_groups['Mall'].add(right_block)
                    building_group.add(right_block)
                    # Update block attributes to match original mall
                    right_block.block_name = block.block_name
                    right_block.block_desc = block.block_desc

                # Bottom neighbor
                if y + 1 in y_groups and x in x_groups and \
                        y_groups[y + 1] in outdoor_type_groups['Street']:
                    bottom_block = y_groups[y + 1]
                    outdoor_type_groups['Street'].remove(bottom_block)
                    outdoor_group.remove(bottom_block)
                    building_type_groups['Mall'].add(bottom_block)
                    building_group.add(bottom_block)
                    # Update block attributes
                    bottom_block.block_name = block.block_name
                    bottom_block.block_desc = block.block_desc

######################def generate_neighbourhoods:

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