# city.py
import csv
import random
from collections import defaultdict
from pathlib import Path


from blocks import CityBlock, BuildingBlock
from settings import *
from data import BLOCKS, BlockType, NEIGHBOURHOODS

class City:
    def __init__(self):
        self.descriptions = self._load_descriptions_from_csv(DataPath("tables/descriptions.csv").path)
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
        """Load block names from tables/block_names.csv into a dictionary."""
        csv_path = Path(DataPath("tables/block_names.csv").path)
        
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
        block_pool = self._generate_offices(block_pool)
        block_pool = self._generate_outdoor_spaces(block_pool)
        block_pool = self._generate_streets(block_pool)
        block_pool = self._generate_malls(block_pool)
        random.shuffle(block_pool)
        grid = self._assign_xy(block_pool)
        grid = self._spread_malls(grid)
        grid = self._generate_neighbourhoods(grid)
        return grid

    def _generate_block(self, block_type):
        """Generate a city block."""
        properties = BLOCKS[block_type]
        if properties.is_building:
            block = BuildingBlock()
        else:
            block = CityBlock()
        block.type = block_type
        block.name = self._get_unique_block_name(block.type.name)
        block.generate_descriptions(self.descriptions)
        return block

    def _generate_buildings(self, block_pool):
        """Generate 5130 building blocks"""
        for _ in range(int(CITY_SIZE * 51.3)):
            building_blocks = [block_type for block_type, properties in BLOCKS.items() if properties.is_building and not block_type == BlockType.MALL]
            building_block = self._generate_block(random.choice(building_blocks))         
            block_pool.append(building_block)
        return block_pool
    
    def _generate_offices(self, block_pool):
        """Generate 500 office buildings."""
        for _ in range(CITY_SIZE * 5):
            office_block = self._generate_block(BlockType.OFFICE)
            block_pool.append(office_block)
        return block_pool

    def _generate_outdoor_spaces(self, block_pool):
        """Generate 1250 outdoor blocks"""
        for _ in range(int(CITY_SIZE * 12.5)):
            outdoor_blocks = [block_type for block_type, properties in BLOCKS.items() if not properties.is_building]
            outdoor_block = self._generate_block(random.choice(outdoor_blocks))
            block_pool.append(outdoor_block)
        return block_pool

    def _generate_streets(self, block_pool):
        """Generate 3100 street blocks"""
        for _ in range(CITY_SIZE * 31):
            street_block = self._generate_block(BlockType.STREET)
            block_pool.append(street_block)
        return block_pool
    
    def _generate_malls(self, block_pool):
        """Generate 20 mall blocks"""
        for _ in range(int(CITY_SIZE * 0.2)):
            mall_block = self._generate_block(BlockType.MALL)
            block_pool.append(mall_block)
        return block_pool

    def _assign_xy(self, block_pool):
        """Place blocks into a 100x100 grid"""
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
        """Implement mall spreading logic."""
        mall_sizes = {}  # Track the size of each mall (keyed by name)

        for y, row in enumerate(grid):
            for x, block in enumerate(row):
                if block.type == BlockType.MALL:
                    # Get or initialize the mall size
                    mall_name = block.name
                    if mall_name not in mall_sizes:
                        mall_sizes[mall_name] = 1  # Start with the original block

                    # Skip if the mall has reached its maximum size
                    if mall_sizes[mall_name] >= 4:
                        continue

                    # Try to expand the mall to adjacent blocks
                    right_spread = False
                    below_spread = False

                    # Right neighbor
                    if x + 1 < CITY_SIZE:  # Ensure within bounds
                        right_block = grid[y][x + 1]
                        if right_block.type == BlockType.STREET and mall_sizes[mall_name] < 4:
                            new_block = self._replace_block(right_block, block, 'MALL', right_block.x, right_block.y)
                            if new_block:
                                mall_sizes[mall_name] += 1
                                right_spread = True
                                grid[right_block.y][right_block.x] = new_block

                    # Bottom neighbor
                    if y + 1 < CITY_SIZE:  # Ensure within bounds
                        bottom_block = grid[y + 1][x]
                        if bottom_block.type == BlockType.STREET and mall_sizes[mall_name] < 4:
                            new_block = self._replace_block(bottom_block, block, 'MALL', bottom_block.x, bottom_block.y)
                            if new_block:
                                mall_sizes[mall_name] += 1
                                below_spread = True
                                grid[bottom_block.y][bottom_block.x] = new_block

                    # Diagonal neighbor
                    if right_spread or below_spread:
                        if y + 1 < CITY_SIZE and x + 1 < CITY_SIZE:  # Ensure within bounds
                            diagonal_block = grid[y + 1][x]
                            if diagonal_block.type == BlockType.STREET and mall_sizes[mall_name] < 4:
                                new_block = self._replace_block(diagonal_block, block, 'MALL', bottom_block.x, bottom_block.y)
                                if new_block:
                                    mall_sizes[mall_name] += 1
                                    grid[diagonal_block.y][diagonal_block.x] = new_block

        return grid

    def _replace_block(self, target_block, source_block, type, x, y):
        """Replace a target block with a new block of the specified type."""
        if target_block.type == BlockType.STREET:
            new_block = BuildingBlock()
            new_block.type = getattr(BlockType, type)
            new_block.name = source_block.name
            new_block.generate_descriptions(self.descriptions)
            new_block.x, new_block.y = x, y
            return new_block

        return None


    def _generate_neighbourhoods(self, grid):
        neighbourhood_index = 0

        for y_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over rows in steps of 10
            for x_start in range(0, CITY_SIZE, NEIGHBOURHOOD_SIZE): # Iterate over columns in steps of 10
                neighbourhood_name = NEIGHBOURHOODS[neighbourhood_index]
                neighbourhood_index += 1

                # Collect blocks and add to neighbourhood group
                for y in range(y_start, y_start + NEIGHBOURHOOD_SIZE):
                    for x in range(x_start, x_start + NEIGHBOURHOOD_SIZE):
                        grid[y][x].neighbourhood = neighbourhood_name

        return grid