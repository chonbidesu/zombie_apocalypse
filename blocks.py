# blocks.py
import random
from collections import defaultdict

from settings import *

class CityBlock:
    """Base class for a city block."""
    def __init__(self):
        self.block_name = 'City Block'
        self.block_type = 'Street'
        self.block_desc = 'city block'
        self.block_outside_desc = 'A non-descript city block.'
        self.observations = []
        self.neighbourhood = ''

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

    def render_label(self):
        """Render the block label onto the block's surface."""
        block_text = wrap_text(self.block_name, font_small, BLOCK_SIZE - 10)
        text_height = sum(font_small.size(line)[1] for line in block_text)

        image_copy = self.image.copy()

        label_rect = pygame.Rect(
            0, BLOCK_SIZE - text_height - 10, BLOCK_SIZE, text_height + 10
        )
        pygame.draw.rect(image_copy, WHITE, label_rect)

        # Draw text onto the block surface
        y_offset = label_rect.top + 10
        for line in block_text:
            text_surface = font_small.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(BLOCK_SIZE // 2, y_offset))
            image_copy.blit(text_surface, text_rect)
            y_offset += font_small.size(line)[1]

        self.image = image_copy

    def apply_zoomed_image(self, block_image):
        """Apply a zoomed-in portion of the block image for street appearance."""
        if self.block_type == "Street":
            image_width, image_height = block_image.get_width(), block_image.get_height()

            # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
            zoom_factor = 2
            zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

            # Generate random top-left coordinates for the zoomed-in area
            self.zoom_x = random.randint(0, image_width - zoom_width)
            self.zoom_y = random.randint(0, image_height - zoom_height)

            # Extract the zoomed-in portion
            zoomed_surface = block_image.subsurface((self.zoom_x, self.zoom_y, zoom_width, zoom_height))

            # Scale it to the target block size and assign it to the sprite
            self.image = pygame.transform.scale(zoomed_surface, (BLOCK_SIZE, BLOCK_SIZE))

            self.render_label()

class BuildingBlock(CityBlock):
    """A block with a building that can be barricaded and searched."""
    def __init__(self):
        super().__init__()
        self.barricade = self.BarricadeLevel()
        self.fuel_expiration = 0
        self.block_inside_desc = 'The inside of a building.'

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
            self.barricade_health = 30

        def set_barricade_level(self, level):
            """
            Sets the barricade level. 
            If the level is out of bounds (less than 0 or greater than 7), it will be capped at 0 or 7.
            """
            self.level = max(0, min(level, 7))  # Keep the level within the bounds
            self.description = self.BARRICADE_DESCRIPTIONS[self.level]
            self.barricade_health = 30

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
        
        def item_search(self, modifier):
            return False