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
        self.barricaded = False
        self.can_barricade = True
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