# city.py
import csv
import random
import pygame
from collections import defaultdict
from pathlib import Path
from blocks import CityBlock, BuildingBlock
from settings import *

class City:
    def __init__(self, x_groups, y_groups):
        self.x_groups, self.y_groups = x_groups, y_groups
        self.descriptions = self.load_descriptions_from_csv("assets/descriptions.csv")
        self.block_name_pool = {}
        self.building_types = ['FireStation', 'PoliceDepartment', 'Hospital', 'Library', 'Church', 
                      'Warehouse', 'AutoRepair', 'Factory', 'School', 'NecroTechLab', 
                      'Junkyard', 'Museum', 'Nightclub', 'Pub', 'Mall']
        self.outdoor_types = ['Street', 'Park', 'Cemetery', 'Monument', 'Carpark']
        self.neighbourhood_groups = {}

        self.building_type_groups = {block_type: pygame.sprite.Group() for block_type in self.building_types}
        self.building_group = pygame.sprite.Group()
        self.outdoor_type_groups = {block_type: pygame.sprite.Group() for block_type in self.outdoor_types}
        self.outdoor_group = pygame.sprite.Group()
        self.cityblock_group = pygame.sprite.Group()

        self._load_block_names()
        self.generate_city()
        self.generate_neighbourhoods()

    # Load descriptive phrases of city blocks from CSV file for assembly
    def load_descriptions_from_csv(self, file_path):
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

    def _load_block_names(self):
        """Load block names from text files into a dictionary."""
        for block_type, filename in BLOCKNAME_FILES.items():
            filepath = Path(f"{BLOCKNAME_LISTS_FOLDER}/{filename}")
            if filepath.exists():
                with open(filepath, "r", encoding="utf-8") as f:
                    contents = f.read()
                names = contents.splitlines()
                self.block_name_pool[block_type] = names
            else:
                print(f"Warning: {filepath} does not exist!")


    def _get_unique_block_name(self, block_type):
        """Retrieve a block name for the given type."""
        block_type = block_type
        if self.block_name_pool[block_type]:
            name = random.choice(self.block_name_pool[block_type])
            return name
        else:
            return f"{block_type} (Generic)"  # Fallback if no names are left

    def generate_city(self):
        """Generate a pool of 10,000 block sprites"""
        self._load_block_names()
        block_pool = []

        # Generate 5000 building blocks
        for _ in range(CITY_SIZE * 50):
            building_block = BuildingBlock()
            self.building_group.add(building_block)
            self.cityblock_group.add(building_block)
            block_type = random.choice(self.building_types)
            building_block.block_type = block_type
            image_filename = BLOCK_IMAGES[block_type]
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
            building_block.image = image
            self.building_type_groups[block_type].add(building_block)
            block_name = self._get_unique_block_name(block_type)
            block_desc = BLOCKNAME_DESC[block_type]
            building_block.block_name = block_name
            building_block.block_desc = block_desc
            building_block.generate_descriptions(self.descriptions, block_type)
            
            building_block.render_label()
            
            block_pool.append(building_block)

        # Generate 2500 outdoor blocks
        for _ in range(CITY_SIZE * 25):
            outdoor_block = CityBlock()
            self.outdoor_group.add(outdoor_block)
            self.cityblock_group.add(outdoor_block)
            block_type = random.choice(self.outdoor_types)
            outdoor_block.block_type = block_type
            image_filename = BLOCK_IMAGES[block_type]
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
            outdoor_block.image = image
            self.outdoor_type_groups[block_type].add(outdoor_block)
            block_name = self._get_unique_block_name(block_type)
            block_desc = BLOCKNAME_DESC[block_type]
            outdoor_block.block_name = block_name
            outdoor_block.block_desc = block_desc
            outdoor_block.generate_descriptions(self.descriptions, block_type)
            
            if block_type == 'Street':
                outdoor_block.apply_zoomed_image(image)

            outdoor_block.render_label()
            
            block_pool.append(outdoor_block)

        # Generate 2500 street blocks
        for _ in range(CITY_SIZE * 25):
            street_block = CityBlock()
            self.outdoor_group.add(street_block)
            self.cityblock_group.add(street_block)
            block_type = 'Street'
            street_block.block_type = block_type
            image_filename = BLOCK_IMAGES[block_type]
            image = pygame.image.load(image_filename)
            image = pygame.transform.scale(image, (BLOCK_SIZE, BLOCK_SIZE))
            street_block.image = image
            self.outdoor_type_groups[block_type].add(street_block)
            block_name = self._get_unique_block_name(block_type)
            block_desc = BLOCKNAME_DESC[block_type]
            street_block.block_name = block_name
            street_block.block_desc = block_desc
            street_block.generate_descriptions(self.descriptions, block_type)
            
            street_block.apply_zoomed_image(image)

            street_block.render_label()
            
            block_pool.append(street_block)

        random.shuffle(block_pool)

        # Now, randomly place blocks into a 100x100 grid
        for y in range(CITY_SIZE):
            for x in range(CITY_SIZE):
                block = block_pool.pop()
                self.x_groups[x].add(block)
                self.y_groups[y].add(block)

        # Implement mall spreading logic
        mall_sizes = {}  # Track the size of each mall (keyed by block_name)

        for y, blocks_in_row in enumerate(self.y_groups):
            for x, block_set in enumerate(self.x_groups):
                for block in block_set:
                    if block in self.building_type_groups['Mall']:
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
                        if x + 1 < len(self.x_groups):  # Ensure within bounds
                            adjacent_blocks = set(self.x_groups[x + 1]) & set(blocks_in_row)
                            for right_block in adjacent_blocks:
                                if right_block in self.outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                                    new_block = self._replace_block(right_block, block, 'Mall')
                                    if new_block:
                                        self.x_groups[x + 1].remove(right_block)
                                        self.y_groups[y].remove(right_block)
                                        self.x_groups[x + 1].add(new_block)
                                        self.y_groups[y].add(new_block)
                                        mall_sizes[mall_name] += 1
                                        right_spread = True

                        # Bottom neighbor
                        if y + 1 < len(self.y_groups):  # Ensure within bounds
                            adjacent_blocks = set(self.y_groups[y + 1]) & set(block_set)
                            for bottom_block in adjacent_blocks:
                                if bottom_block in self.outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                                    new_block = self._replace_block(bottom_block, block, 'Mall')
                                    if new_block:
                                        self.x_groups[x].remove(bottom_block)
                                        self.y_groups[y + 1].remove(bottom_block)
                                        self.x_groups[x].add(new_block)
                                        self.y_groups[y + 1].add(new_block)
                                        mall_sizes[mall_name] += 1
                                        below_spread = True

                        # Diagonal neighbor (only if right or below spread occurred)
                        if (right_spread or below_spread) and x + 1 < len(self.x_groups) and y + 1 < len(self.y_groups):
                            diagonal_blocks = set(self.x_groups[x + 1]) & set(self.y_groups[y + 1])
                            for diagonal_block in diagonal_blocks:
                                if diagonal_block in self.outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                                    new_block = self._replace_block(diagonal_block, block, 'Mall')
                                    if new_block:
                                        self.x_groups[x + 1].remove(diagonal_block)
                                        self.y_groups[y + 1].remove(diagonal_block)
                                        self.x_groups[x + 1].add(new_block)
                                        self.y_groups[y + 1].add(new_block)
                                        mall_sizes[mall_name] += 1

    def _replace_block(self, target_block, source_block, block_type):
        """Replace a target block with a new block of the specified type."""
        if target_block in self.outdoor_type_groups['Street']:
            new_block = BuildingBlock()
            new_block.block_name = source_block.block_name
            new_block.block_desc = source_block.block_desc
            new_block.image = source_block.image
            new_block.generate_descriptions(self.descriptions, block_type)

            # Update group memberships
            self.outdoor_type_groups['Street'].remove(target_block)
            self.outdoor_group.remove(target_block)
            self.cityblock_group.remove(target_block)

            self.building_type_groups[block_type].add(new_block)
            self.building_group.add(new_block)
            self.cityblock_group.add(new_block)
            return new_block
        return None


    def generate_neighbourhoods(self):
        neighbourhood_index = 0

        for y_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over rows in steps of 10
            for x_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over columns in steps of 10
                neighbourhood_name = list(NEIGHBOURHOODS.values())[neighbourhood_index]
                neighbourhood_group = pygame.sprite.Group()
                neighbourhood_index += 1

                # Collect blocks and add to neighbourhood group
                for y in range(y_start, y_start + NEIGHBOURHOOD_SIZE):
                    for x in range(x_start, x_start + NEIGHBOURHOOD_SIZE):
                        block = set(self.x_groups[x]) & set(self.y_groups[y]) & set(self.cityblock_group)
                        neighbourhood_group.add(block)

                # Store the neighbourhood group
                self.neighbourhood_groups[neighbourhood_name] = neighbourhood_group

    # Store zoom coordinates for street blocks to give streets variety
    def initialize_zoom_coordinates(self, city):
        for row in city:
            for block in row:
                if block.block_type == "Street":
                    image_width, image_height = 200, 200
                    zoom_factor = 2
                    zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor
                    
                    # Precompute random zoom position
                    block.zoom_x = random.randint(0, image_width - zoom_width)
                    block.zoom_y = random.randint(0, image_height - zoom_height)