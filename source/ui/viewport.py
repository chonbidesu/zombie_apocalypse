import pygame
import random

from settings import *
from data import BLOCKS, BlockType
from ui.utils import WrapText

class Viewport:
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.frame = pygame.image.load(ResourcePath('assets/viewport_frame.png').path).convert_alpha()
        self.frame_size = SCREEN_HEIGHT // 2
        self.grid_topleft = (self.frame_size // 9) + 12
        self.viewport_group = self._create_viewport_group()

    def draw(self):
        scaled_viewport_frame = pygame.transform.scale(self.frame, (self.frame_size, self.frame_size))
        self.screen.blit(scaled_viewport_frame, (10, 10))
        self.viewport_group.draw(self.screen)
        self.draw_neighbourhood_name()

    #  Set up viewport group
    def _create_viewport_group(self):
        viewport_group = pygame.sprite.Group()

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                block_sprite = BlockSprite(dx, dy, self.game, self.grid_topleft)
                viewport_group.add(block_sprite)
        return viewport_group

    def update(self):
        for sprite in self.viewport_group:
            sprite.update_data()
            sprite.block.is_known = True

    def draw_viewport_frame(self):
        """Draw the 3x3 viewport representing the player's surroundings."""
        scaled_viewport_frame = pygame.transform.scale(self.viewport_frame, (self.viewport_frame_width, self.viewport_frame_height))
        self.screen.blit(scaled_viewport_frame, (10, 10))

    def draw_neighbourhood_name(self):
        # Draw neighbourhood name
        x, y = self.game.state.player.location
        current_block = self.game.state.city.block(x, y)
        pygame.draw.rect(self.screen, ORANGE, (10, self.frame_size + 10, self.frame_size, 30))
        text = font_large.render(current_block.neighbourhood, True, WHITE)
        self.screen.blit(text, ((self.frame_size // 2) - (text.get_width() // 2), self.frame_size + 15))        


class BlockSprite(pygame.sprite.Sprite):
    """Represents a visual sprite for a CityBlock in the viewport."""
    def __init__(self, dx, dy, game, grid_topleft):
        super().__init__()
        self.dx = dx
        self.dy = dy
        self.game = game
        self.block = None # The block this sprite represents
        self.properties = None # Properties of the block
        self.viewport_x = grid_topleft + (dx + 1) * BLOCK_SIZE  # Translate relative dx to viewport position
        self.viewport_y = grid_topleft + (dy + 1) * BLOCK_SIZE  # Translate relative dy to viewport position
        self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.rect = self.image.get_rect(topleft=(self.viewport_x, self.viewport_y))
        self.viewport_npcs = []


    def update_data(self):
        """
        Update the sprite's data based on the player's current location and CityBlock objects.
        """
        # Determine the target block coordinates based on player location and dx, dy offsets
        x = self.game.state.player.location[0] + self.dx
        y = self.game.state.player.location[1] + self.dy

        # Check if the target coordinates are within city bounds
        if 0 <= x < CITY_SIZE and 0 <= y < CITY_SIZE:
            self.block = self.game.state.city.block(x, y)  # Retrieve the CityBlock at (x, y)
            self.properties = BLOCKS[self.block.type]

            # Load the block image
            image_filename = self.properties.image_file
            self.image = pygame.image.load(image_filename).convert_alpha()
            self.image = pygame.transform.scale(self.image, (BLOCK_SIZE, BLOCK_SIZE))

            # Apply zoom effect for street blocks
            if self.block.type == BlockType.STREET:
                self.apply_zoomed_image()

            # Update the block label
            self.draw_block_label()

            # Clear the current list of viewport npcs
            self.viewport_npcs.clear()

            # Add ViewportNPCs if they are present in this block
            matching_npcs = [
                npc for npc in self.game.state.npcs.list if npc.location[0] == x and npc.location[1] == y and not npc.is_dead
            ]
            npc_count = len(matching_npcs)
            for index, npc in enumerate(matching_npcs):
                viewport_npc = ViewportNPC(npc, index, npc_count)
                self.viewport_npcs.append(viewport_npc)

            # Draw the npcs onto the block image
            self.draw_npcs()

        else:
            self.image.set_alpha(0)

                        
    def draw_npcs(self):
        """Draw NPC sprites onto the block."""
        for viewport_npc in self.viewport_npcs:
            npc_image = viewport_npc.image
            npc_rect = npc_image.get_rect(center=viewport_npc.position)                
            if viewport_npc.npc.inside and self.game.state.player.inside and viewport_npc.npc.location == self.game.state.player.location:
                self.image.blit(npc_image, npc_rect)
            elif not viewport_npc.npc.inside and not self.game.state.player.inside:
                self.image.blit(npc_image, npc_rect)

    def draw_block_label(self):
        """Render the block label onto the block's surface."""
        block_text = WrapText(self.block.name, font_small, BLOCK_SIZE - 2)
        text_height = sum(font_small.size(line)[1] for line in block_text.lines)

        image_copy = self.image.copy()

        label_rect = pygame.Rect(
            0, BLOCK_SIZE - text_height - 2, BLOCK_SIZE, text_height + 2
        )
        if self.properties.is_building:
            if self.block.lights_on:
                pygame.draw.rect(image_copy, PALE_YELLOW, label_rect)
            else:
                pygame.draw.rect(image_copy, WHITE, label_rect)
        else:
            pygame.draw.rect(image_copy, WHITE, label_rect)

        # Draw text onto the block surface
        y_offset = label_rect.top + 5
        for line in block_text.lines:
            text_surface = font_small.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(BLOCK_SIZE // 2, y_offset))
            image_copy.blit(text_surface, text_rect)
            y_offset += font_small.size(line)[1]

        self.image = image_copy

    def apply_zoomed_image(self):
        """Apply a zoomed-in portion of the block image for street appearance."""
        image_width, image_height = self.image.get_width(), self.image.get_height()

        # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
        zoom_factor = 2
        zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

        # Check if zoom coordinates are already set
        if not hasattr(self, "zoom_x") or not hasattr(self, "zoom_y"):
            # Generate random top-left coordinates for the zoomed-in area
            self.zoom_x = random.randint(0, image_width - zoom_width)
            self.zoom_y = random.randint(0, image_height - zoom_height)

        # Extract the zoomed-in portion
        zoomed_surface = self.image.subsurface((self.zoom_x, self.zoom_y, zoom_width, zoom_height))

        # Scale it to the target block size and assign it to the sprite
        self.image = pygame.transform.scale(zoomed_surface, (BLOCK_SIZE, BLOCK_SIZE))


class ViewportNPC:
    """A NPC representation for drawing in the viewport."""
    def __init__(self, npc, index, total_npcs):
        self.npc = npc
        self.index = index
        self.total_npcs = total_npcs
        self.size = BLOCK_SIZE // 6  # NPC size as a fraction of the block size

        self._position_square()

    def _position_square(self):
        # Determine row and column for this NPC
        row = self.index // 3  # Row 0 or 1 plus row offset
        col = self.index % 3   # Column 0, 1, or 2

        # Calculate horizontal positioning for each column
        row_width = min(self.total_npcs - row * 3, 3) * (self.size + 2)  # Width of the row
        row_start_x = (BLOCK_SIZE - row_width) // 2  # Center the row horizontally
        x = row_start_x + col * (self.size + 2) + self.size // 2

        # Determine colour and vertical positioning based on NPC state
        if self.npc.is_human:
            colour = (0, 0, 255)
            row_offset = 1
        else:
            colour = (0, 255, 0)
            row_offset = 0

        # Calculate vertical positioning for each row
        row_height = self.size + 2
        y = (BLOCK_SIZE // 3) + (row + row_offset - 0.5) * row_height  # Row 0 above, row 1 below

        self.position = (x, y)

        # Create the npc image
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.fill(colour)
