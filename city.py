# city.py
import csv
import random
import pygame
from collections import defaultdict
from pathlib import Path


from blocks import CityBlock, BuildingBlock
from settings import *

class City:
    def __init__(self):
        self.descriptions = self._load_descriptions_from_csv("assets/descriptions.csv")
        self.block_name_pool = {}

        self._load_block_names()
        self.grid = self._generate_city()

    def block(self, x, y):
        """Retrieve a block at coordinates."""
        return self.grid[y][x]

    # Load descriptive phrases of city blocks from CSV file for assembly
    def _load_descriptions_from_csv(self, file_path):
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
        """Load block names from assets/block_names.csv into a dictionary."""
        csv_path = Path("assets/block_names.csv")
        
        if not csv_path.exists():
            print(f"Error: {csv_path} does not exist!")
            return

        try:
            with open(csv_path, "r", encoding="utf-8") as csv_file:
                reader = csv.DictReader(csv_file)

                # Populate block_name_pool from the CSV
                for row in reader:
                    for block_type, name in row.items():
                        if name:  # Ignore empty cells
                            self.block_name_pool.setdefault(block_type, []).append(name)

        except Exception as e:
            print(f"Error reading {csv_path}: {e}")

    def _get_unique_block_name(self, block_type):
        """Retrieve a block name for the given type."""
        block_type = block_type
        if self.block_name_pool[block_type]:
            name = random.choice(self.block_name_pool[block_type])
            return name
        else:
            return f"{block_type} (Generic)"  # Fallback if no names are left

    def _generate_city(self):
        """Generate a pool of 10,000 block sprites"""
        self._load_block_names()
        block_pool = []
        block_pool = self._generate_buildings(block_pool)
        block_pool = self._generate_outdoor_spaces(block_pool)
        block_pool = self._generate_streets(block_pool)
        random.shuffle(block_pool)
        grid = self._assign_xy(block_pool)
        grid = self._spread_malls(grid)
        grid = self._generate_neighbourhoods(grid)
        return grid

    def _generate_buildings(self, block_pool):
        # Generate 5000 building blocks
        for _ in range(CITY_SIZE * 50):
            building_block = BuildingBlock()
            building_block.block_type = random.choice(BUILDING_TYPES)
            building_block.block_name = self._get_unique_block_name(building_block.block_type.name)
            building_block.block_desc = building_block.block_type.description
            building_block.generate_descriptions(self.descriptions)          
            block_pool.append(building_block)
        return block_pool

    def _generate_outdoor_spaces(self, block_pool):
        # Generate 2500 outdoor blocks
        for _ in range(CITY_SIZE * 25):
            outdoor_block = CityBlock()
            outdoor_block.block_type = random.choice(OUTDOOR_TYPES)
            outdoor_block.block_name = self._get_unique_block_name(outdoor_block.block_type.name)
            outdoor_block.block_desc = outdoor_block.block_type.description
            outdoor_block.generate_descriptions(self.descriptions)
            block_pool.append(outdoor_block)
        return block_pool

    def _generate_streets(self, block_pool):
        # Generate 2500 street blocks
        for _ in range(CITY_SIZE * 25):
            street_block = CityBlock()
            street_block.block_type = CityBlockType.STREET
            street_block.block_name = self._get_unique_block_name(street_block.block_type.name)
            street_block.block_desc = street_block.block_type.description
            street_block.generate_descriptions(self.descriptions)         
            block_pool.append(street_block)
        return block_pool

    def _assign_xy(self, block_pool):
        # Now, randomly place blocks into a 100x100 grid
        grid = []
        for y in range(CITY_SIZE):
            row = []
            for x in range(CITY_SIZE):
                block = block_pool.pop()
                block.x = x
                block.y = y
                row.append(block)
            grid.append(row)
        return grid

    def _spread_malls(self, grid):
        # Implement mall spreading logic
        mall_sizes = {}  # Track the size of each mall (keyed by block_name)

        for y, row in enumerate(grid):
            for x, block in enumerate(row):
                if block.block_type == CityBlockType.MALL:
                    # Get or initialize the mall size
                    mall_name = block.block_name
                    if mall_name not in mall_sizes:
                        mall_sizes[mall_name] = 1  # Start with the original block

                    # Skip if the mall has reached its maximum size
                    if mall_sizes[mall_name] >= 4:
                        continue

                    # Try to expand the mall to adjacent blocks
                    #right_spread = False
                    #below_spread = False

                    # Right neighbor
                    if x + 1 < CITY_SIZE and 0 < y - 1 and y + 1 < CITY_SIZE:  # Ensure within bounds
                        adjacent_blocks = [grid[y - 1][x + 1], grid[y][x + 1], grid[y + 1][x + 1]]
                        for right_block in adjacent_blocks:
                            if right_block.block_type == CityBlockType.STREET and mall_sizes[mall_name] < 4:
                                new_block = self._replace_block(right_block, block, 'MALL', right_block.x, right_block.y)
                                if new_block:
                                    mall_sizes[mall_name] += 1
                                    #right_spread = True
                                    right_block = new_block

                    # Bottom neighbor
                    if y + 1 < CITY_SIZE and 0 < x - 1 and x + 1 < CITY_SIZE:  # Ensure within bounds
                        adjacent_blocks = [grid[y + 1][x - 1], grid[y + 1][x], grid[y + 1][x + 1]]
                        for bottom_block in adjacent_blocks:
                            if bottom_block.block_type == CityBlockType.STREET and mall_sizes[mall_name] < 4:
                                new_block = self._replace_block(bottom_block, block, 'MALL', bottom_block.x, bottom_block.y)
                                if new_block:
                                    mall_sizes[mall_name] += 1
                                    #below_spread = True
                                    bottom_block = new_block

                    # Diagonal neighbor (only if right or below spread occurred)
                    #if (right_spread or below_spread) and x + 1 < CITY_SIZE and y + 1 < CITY_SIZE:
                    #    diagonal_blocks = [grid[y - 1][x - 1], grid[y + 1][x], grid[y + 1][x + 1]]
                    #    for diagonal_block in diagonal_blocks:
                    #        if diagonal_block in self.outdoor_type_groups['Street'] and mall_sizes[mall_name] < 4:
                    #            new_block = self._replace_block(diagonal_block, block, 'Mall')
                    #            if new_block:
                    #                self.x_groups[x + 1].remove(diagonal_block)
                    #                self.y_groups[y + 1].remove(diagonal_block)
                    #                self.x_groups[x + 1].add(new_block)
                    #                self.y_groups[y + 1].add(new_block)
                    #                mall_sizes[mall_name] += 1

        return grid

    def _replace_block(self, target_block, source_block, block_type, x, y):
        """Replace a target block with a new block of the specified type."""
        if target_block.block_type == CityBlockType.STREET:
            new_block = BuildingBlock()
            new_block.block_type = getattr(CityBlockType, block_type)
            new_block.block_name = source_block.block_name
            new_block.block_desc = source_block.block_desc
            new_block.generate_descriptions(self.descriptions)
            new_block.x, new_block.y = x, y
            return new_block

        return None


    def _generate_neighbourhoods(self, grid):
        neighbourhood_index = 0

        for y_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over rows in steps of 10
            for x_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over columns in steps of 10
                neighbourhood_name = list(NEIGHBOURHOODS.values())[neighbourhood_index]
                neighbourhood_index += 1

                # Collect blocks and add to neighbourhood group
                for y in range(y_start, y_start + NEIGHBOURHOOD_SIZE):
                    for x in range(x_start, x_start + NEIGHBOURHOOD_SIZE):
                        grid[y][x].neighbourhood = neighbourhood_name

        return grid