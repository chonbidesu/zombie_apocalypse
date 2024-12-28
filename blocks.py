# blocks.py
import random
from collections import defaultdict

class CityBlock:
    """Base class for a city block."""
    def __init__(self, block_type):
        self.block_type = block_type
        self.block_name = 'City Block'
        self.block_desc = 'city block'
        self.block_outside_desc = 'A non-descript city block.'
        self.can_barricade = False
        self.zoom_x = None
        self.zoom_y = None
        self.is_building = False
        self.observations = []
        self.outside_observations = []
    
    def generate_descriptions(self, descriptions_data):
        if self.block_type in descriptions_data:
            data = descriptions_data[self.block_type]
            
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


    def add_outside_observation(self, observation):
        """Add a new outside observation to the list."""
        self.outside_observations.append(observation)


class BuildingBlock(CityBlock):
    """A block with a building that can be barricaded and searched."""
    def __init__(self, block_type):
        super().__init__(block_type)
        self.can_barricade = True
        self.barricade = self.BarricadeLevel()
        self.powered = False
        self.lights_on = False
        self.door_open = True
        self.is_building = True
        self.block_inside_desc = 'The inside of a building.'
        self.inside_observations = []

    def generate_descriptions(self, descriptions_data):
        if self.block_type in descriptions_data:
            data = descriptions_data[self.block_type]
            
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

    def add_inside_observation(self, observation):
        """Add a new inside observation to the list."""
        self.inside_observations.append(observation)

    class BarricadeLevel:
        """Model barricade levels for buildings"""
        # Mapping integer values to descriptive barricade states
        BARRICADE_DESCRIPTIONS = {
            0: "not barricaded",
            1: "loosely barricaded",
            2: "lightly barricaded",
            3: "strongly barricaded",
            4: "very strongly barricaded",
            5: "heavily barricaded",
            6: "very heavily barricaded",
            7: "extremely heavily barricaded"
        }

        def __init__(self, level=0):
            # Set default barricade level (0 by default, i.e., no barricade)
            self.set_barricade_level(level)

        def set_barricade_level(self, level):
            """
            Sets the barricade level. 
            If the level is out of bounds (less than 0 or greater than 7), it will be capped at 0 or 7.
            """
            self.level = max(0, min(level, 7))  # Keep the level within the bounds
            self.description = self.BARRICADE_DESCRIPTIONS[self.level]

        def adjust_barricade(self, delta):
            """
            Adjust the barricade level by adding or subtracting `delta`.
            """
            new_level = self.level + delta
            if new_level > 7:
                return False
            self.set_barricade_level(new_level)  # Automatically handles out-of-bound levels
            return True

        def get_barricade_description(self):
            """
            Returns the current description of the barricade.
            """
            return self.description