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
cityblock_group = pygame.sprite.Group()
neighbourhood_groups = {}

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
    """Generate a pool of 10,000 block sprites"""
    _load_block_names()
    block_pool = []

    # Generate 5000 building blocks
    for _ in range(CITY_SIZE * 50):
        building_block = BuildingBlock()
        building_group.add(building_block)
        cityblock_group.add(building_block)
        block_type = random.choice(building_types)
        image_filename = BLOCK_IMAGES[block_type]
        image = pygame.image.load(image_filename)
        image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
        building_block.image = image
        building_type_groups[block_type].add(building_block)
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        building_block.block_name = block_name
        building_block.block_desc = block_desc
        building_block.generate_descriptions(descriptions, block_type)
        block_pool.append(building_block)

    # Generate 2500 outdoor blocks
    for _ in range(CITY_SIZE * 25):
        outdoor_block = CityBlock()
        outdoor_group.add(outdoor_block)
        cityblock_group.add(outdoor_block)
        block_type = random.choice(outdoor_types)
        image_filename = BLOCK_IMAGES[block_type]
        image = pygame.image.load(image_filename)
        image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
        outdoor_block.image = image
        outdoor_type_groups[block_type].add(outdoor_block)
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        outdoor_block.block_name = block_name
        outdoor_block.block_desc = block_desc
        outdoor_block.generate_descriptions(descriptions, block_type)
        block_pool.append(outdoor_block)

    # Generate 2500 street blocks
    for _ in range(CITY_SIZE * 25):
        street_block = CityBlock()
        outdoor_group.add(street_block)
        cityblock_group.add(street_block)
        block_type = 'Street'
        image_filename = BLOCK_IMAGES[block_type]
        image = pygame.image.load(image_filename)
        image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
        street_block.image = image
        outdoor_type_groups[block_type].add(street_block)
        block_name = _get_unique_block_name(block_type)
        block_desc = BLOCKNAME_DESC[block_type]
        street_block.block_name = block_name
        street_block.block_desc = block_desc
        street_block.generate_descriptions(descriptions, block_type)
        block_pool.append(street_block)

    random.shuffle(block_pool)

    # Now, randomly place blocks into a 100x100 grid
    for y in range(CITY_SIZE):
        for x in range(CITY_SIZE):
            block = block_pool.pop()
            x_groups[x].add(block)
            y_groups[y].add(block)

    # Implement mall spreading logic
    mall_sizes = {}  # Track the size of each mall (keyed by block_name)

    for y, blocks_in_row in y_groups.items():
        for x, block_set in x_groups.items():
            for block in set(block_set) & set(blocks_in_row):  # Get intersection of x_groups and y_groups
                if block in building_type_groups['Mall']:
                    # Get or initialize the mall size
                    mall_name = block.block_name
                    if mall_name not in mall_sizes:
                        mall_sizes[mall_name] = 1  # Start with the original block

                    # Skip if the mall has reached its maximum size
                    if mall_sizes[mall_name] >= 4:
                        continue

                    # Try to expand the mall to adjacent blocks
                    right_spread = False
                    below_spread = False

                    # Right neighbor
                    if x + 1 in x_groups and y in y_groups:
                        adjacent_blocks = set(x_groups[x + 1]) & set(blocks_in_row)
                        for right_block in adjacent_blocks:
                            if right_block in outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                                # Replace the block
                                new_block = BuildingBlock()
                                new_block.block_name = block.block_name
                                new_block.block_desc = block.block_desc
                                new_block.image = block.image
                                new_block.generate_descriptions(descriptions, 'Mall')

                                # Update group memberships
                                outdoor_type_groups['Street'].remove(right_block)
                                outdoor_group.remove(right_block)
                                cityblock_group.remove(right_block)

                                building_type_groups['Mall'].add(new_block)
                                building_group.add(new_block)
                                # print(f"Added to building_group: {new_block} of type {new_block.__class__.__name__}")
                                cityblock_group.add(new_block)

                                x_groups[x + 1].remove(right_block)
                                y_groups[y].remove(right_block)
                                x_groups[x + 1].add(new_block)
                                y_groups[y].add(new_block)

                                mall_sizes[mall_name] += 1
                                right_spread = True

                    # Bottom neighbor
                    if y + 1 in y_groups and x in x_groups:
                        adjacent_blocks = set(y_groups[y + 1]) & set(block_set)
                        for bottom_block in adjacent_blocks:
                            if bottom_block in outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                                # Replace the block
                                new_block = BuildingBlock()
                                new_block.block_name = block.block_name
                                new_block.block_desc = block.block_desc
                                new_block.image = block.image
                                new_block.generate_descriptions(descriptions, 'Mall')

                                # Update group memberships
                                outdoor_type_groups['Street'].remove(bottom_block)
                                outdoor_group.remove(bottom_block)
                                cityblock_group.remove(bottom_block)

                                building_type_groups['Mall'].add(new_block)
                                building_group.add(new_block)
                                # print(f"Added to building_group: {new_block} of type {new_block.__class__.__name__}")
                                cityblock_group.add(new_block)

                                x_groups[x].remove(bottom_block)
                                y_groups[y + 1].remove(bottom_block)
                                x_groups[x].add(new_block)
                                y_groups[y + 1].add(new_block)

                                mall_sizes[mall_name] += 1
                                below_spread = True

                    # Diagonal neighbor (only if right or below spread occurred)
                    if (right_spread or below_spread) and x + 1 in x_groups and y + 1 in y_groups:
                        diagonal_blocks = set(x_groups[x + 1]) & set(y_groups[y + 1])
                        for diagonal_block in diagonal_blocks:
                            if diagonal_block in outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                                # Replace the block
                                new_block = BuildingBlock()
                                new_block.block_name = block.block_name
                                new_block.block_desc = block.block_desc
                                new_block.image = block.image
                                new_block.generate_descriptions(descriptions, 'Mall')

                                # Update group memberships
                                outdoor_type_groups['Street'].remove(diagonal_block)
                                outdoor_group.remove(diagonal_block)
                                cityblock_group.remove(diagonal_block)

                                building_type_groups['Mall'].add(new_block)
                                building_group.add(new_block)
                                # print(f"Added to building_group: {new_block} of type {new_block.__class__.__name__}")
                                cityblock_group.add(new_block)

                                x_groups[x + 1].remove(diagonal_block)
                                y_groups[y + 1].remove(diagonal_block)
                                x_groups[x + 1].add(new_block)
                                y_groups[y + 1].add(new_block)

                                mall_sizes[mall_name] += 1

def generate_neighbourhoods(x_groups, y_groups):
    neighbourhood_index = 0

    for y_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over rows in steps of 10
        for x_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over columns in steps of 10
            neighbourhood_name = list(NEIGHBOURHOODS.values())[neighbourhood_index]
            neighbourhood_group = pygame.sprite.Group()
            neighbourhood_index += 1

            # Collect blocks and add to neighbourhood group
            for y in range(y_start, y_start + NEIGHBOURHOOD_SIZE):
                for x in range(x_start, x_start + NEIGHBOURHOOD_SIZE):
                    block = set(x_groups[x]) & set(y_groups[y]) & set(cityblock_group)
                    neighbourhood_group.add(block)

            # Store the neighbourhood group
            neighbourhood_groups[neighbourhood_name] = neighbourhood_group

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