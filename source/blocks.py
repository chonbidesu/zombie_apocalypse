# blocks.py
import random
from collections import defaultdict

from settings import *
from data import BarricadeState, BARRICADE_DESCRIPTIONS

class CityBlock:
    """Base class for a city block."""
    def __init__(self):
        self.name = 'City Block'
        self.type = None
        self.x, self.y = 0, 0
        self.block_outside_desc = 'A non-descript city block.'
        self.observations = []
        self.neighbourhood = ''
        self.current_zombies = 0 # Number of zombies currently in the block
        self.current_humans = 0
        self.is_known = False # Has the player seen the block

    def generate_descriptions(self, descriptions_data):
        """Randomly construct three-sentence descriptions of city blocks."""
        if self.type.name in descriptions_data:
            data = descriptions_data[self.type.name]
            
            # Randomly assemble outside descriptions
            outside = data.get("outside", defaultdict(list))
                       
            self.block_outside_desc = " ".join([
                random.choice(outside["first"]) if outside["first"] else "",
                random.choice(outside["second"]) if outside["second"] else "",
                random.choice(outside["third"]) if outside["third"] else ""
            ])
        else:
            # Default descriptions if block type is not found
            self.block_outside_desc = "This place shows signs of decay and neglect."

class BuildingBlock(CityBlock):
    """A block with a building that can be barricaded and searched."""
    def __init__(self):
        super().__init__()
        self.barricade = self.BarricadeLevel()
        self.fuel_expiration = 0
        self.block_inside_desc = 'The inside of a building.'
        self.ransack_level = 0
        self.ruined = False
        self.lights_on = False
        self.generator_installed = False

    def generate_descriptions(self, descriptions_data):
        """Randomly construct three-sentence descriptions of building blocks."""
        if self.type.name in descriptions_data:
            data = descriptions_data[self.type.name]
            
            # Randomly assemble inside and outside descriptions
            inside = data.get("inside", defaultdict(list))
            outside = data.get("outside", defaultdict(list))
            
            self.block_inside_desc = " ".join([
                random.choice(inside["first"]) if inside["first"] else "",
                random.choice(inside["second"]) if inside["second"] else "",
                random.choice(inside["third"]) if inside["third"] else ""
            ])
            
            self.block_outside_desc = " ".join([
                random.choice(outside["first"]) if outside["first"] else "",
                random.choice(outside["second"]) if outside["second"] else "",
                random.choice(outside["third"]) if outside["third"] else ""
            ])
        else:
            # Default descriptions if block type is not found
            self.block_inside_desc = "Inside, this place looks abandoned and forgotten."
            self.block_outside_desc = "Outside, the building shows signs of decay and neglect."


    class BarricadeLevel:
        """Model barricade levels for buildings"""
        def __init__(self, level=0):
            # Set default barricade level (0 by default, i.e., no barricade)
            self.level = level
            self.set_barricade_level(level)
            self.sublevel = 0
            self.successful_hits = 0

        def set_barricade_level(self, level):
            """
            Sets the barricade level. 
            If the level is out of bounds (less than 0 or greater than 7), it will be capped at 0 or 7.
            """
            self.level = max(0, min(level, 7))  # Keep the level within the bounds
            self.description = self.get_barricade_description()

        def adjust_barricade_level(self, delta):
            """
            Adjust the barricade level by adding or subtracting `delta`.
            """
            new_level = self.level + delta
            self.set_barricade_level(new_level)

        def adjust_barricade_sublevel(self, delta):
            """
            Adjust the barricade sublevel by adding or subtracting `delta`.
            Levels 0-1 have 1 sublevel. Levels 2-6 have 3 sublevels. Level 7 has 5 sublevels.
            """
            new_sublevel = self.sublevel + delta

            if self.level <= 1 and new_sublevel > 0:
                self.adjust_barricade_level(1)
                self.successful_hits = 0
                return True
            
            elif self.level <= 2 and new_sublevel < 0:
                self.adjust_barricade_level(-1)
                self.successful_hits = 0
                return True

            elif 3 <= self.level <= 7 and new_sublevel < 0:
                self.adjust_barricade_level(-1)
                self.sublevel = 2
                self.successful_hits = 0
                return True

            elif 2 <= self.level < 7 and new_sublevel < 3:
                self.sublevel = new_sublevel
                self.successful_hits = 0
                return True

            elif 2 <= self.level < 7 and new_sublevel >= 3:
                self.adjust_barricade_level(1)
                self.sublevel = 0
                self.successful_hits = 0
                return True

            elif self.level == 7 and 0 <= new_sublevel < 5:
                self.sublevel = new_sublevel
                self.successful_hits = 0
                return True

            else:
                return False
            

        def register_hit(self):
            """Register a successful hit on the barricade."""
            self.successful_hits += 1
            if self.successful_hits == 3:
                self.adjust_barricade_sublevel(-1)
                self.successful_hits = 0

        def get_barricade_description(self):
            """
            Returns the current description of the barricade.
            """
            barricade_state = list(BarricadeState)[self.level]
            return BARRICADE_DESCRIPTIONS[barricade_state]