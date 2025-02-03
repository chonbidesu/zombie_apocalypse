# map.py

import pygame
import random

from settings import *
from ui.utils import WrapText
from data import BLOCKS, BlockType, NEIGHBOURHOODS


class Map:
    def __init__(self, game, screen):
        self.screen = screen
        self.player = game.player
        self.city = game.city
        self.GRID_ROWS = 10
        self.GRID_COLS = 10
        self.BLOCK_PADDING = 2
        self.zoom_in = True
        self.cached_zoom = {}

        self.MAP_SIZE = SCREEN_HEIGHT - 50
        self.block_size = (self.MAP_SIZE - (self.GRID_ROWS + 1) * self.BLOCK_PADDING) // self.GRID_ROWS
        self.map_surface = pygame.Surface((SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
        self.map_surface.fill((255, 255, 255))
        self.city_map = pygame.Surface((self.MAP_SIZE, self.MAP_SIZE))
        self.city_map.fill((0, 0, 0))

        self.block_images = {
            block_type: pygame.transform.scale(
                pygame.image.load(properties.image_file).convert_alpha(), 
                (self.block_size, self.block_size)
            ) 
            for block_type, properties in BLOCKS.items()
        }

    def draw(self):
        blink_state = pygame.time.get_ticks() // 500 % 2 == 0
        player_block = self.city.block(self.player.location[0], self.player.location[1])

        self.screen.blit(self.map_surface, (10, 10))

        map_data = self._get_map_data(player_block)
        self._draw_map(map_data)
        if blink_state:
            self._draw_player_location(map_data)  
        
        self.screen.blit(self.city_map, (25, 25))

        self._draw_map_info()

    def _draw_map(self, map_data): 
        index = 0
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                # Calculate top-left corner of the block
                x = self.BLOCK_PADDING + col * (self.block_size + self.BLOCK_PADDING) + 4
                y = self.BLOCK_PADDING + row * (self.block_size + self.BLOCK_PADDING) + 4

                if self.zoom_in:
                    player_block = self.city.block(self.player.location[0], self.player.location[1])
                    neighbourhood_index = NEIGHBOURHOODS.index(player_block.neighbourhood)
                    col_offset = neighbourhood_index % 10 * 10
                    row_offset = int(neighbourhood_index // 10) * 10
                    current_block = self.city.block(col + col_offset, row + row_offset)

                    # Check if the player has seen the block before
                    if current_block.is_known:
                        # Draw block
                        block_image = self.block_images[current_block.type]
                        if current_block.type == BlockType.STREET:
                            image_width, image_height = block_image.get_width(), block_image.get_height()

                            # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
                            zoom_factor = 2
                            zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

                            # Check if zoom coordinates are cached
                            if (col, row) in self.cached_zoom:
                                (zoom_x, zoom_y) = self.cached_zoom[(col, row)]
                            else:
                                zoom_x = random.randint(0, image_width - zoom_width)
                                zoom_y = random.randint(0, image_height - zoom_height)

                                self.cached_zoom[(col, row)] = (zoom_x, zoom_y)

                            # Extract the zoomed-in portion
                            zoomed_surface = block_image.subsurface((zoom_x, zoom_y, zoom_width, zoom_height))

                            # Scale it to the target block size and assign it to the sprite
                            block_image = pygame.transform.scale(zoomed_surface, (self.block_size, self.block_size))

                        label_name = map_data[index]
                        block_image = self._draw_block_label(block_image, label_name)

                        self.city_map.blit(block_image, (x, y))

                    else:
                        # Draw fog of war block
                        pygame.draw.rect(self.city_map, (125, 125, 125), (x, y, self.block_size, self.block_size))

                else:
                    # Draw neighbourhood
                    neighbourhood_block = pygame.Surface((self.block_size, self.block_size))
                    neighbourhood_block.fill((255, 255, 255))
                    label_name = map_data[index]
                    neighbourhood_block = self._draw_block_label(neighbourhood_block, label_name)
                    self.city_map.blit(neighbourhood_block, (x, y))

                index += 1

    def _draw_block_label(self, block_image, label_name):
        """Render the block label onto the block's surface."""
        label_text = WrapText(label_name, font_xs, self.block_size - 2)
        text_height = sum(font_xs.size(line)[1] for line in label_text.lines)

        image_copy = block_image.copy()
        label_rect = pygame.Rect(
            0, self.block_size - text_height - 2, self.block_size, text_height + 2
        )

        if self.zoom_in:
            pygame.draw.rect(image_copy, WHITE, label_rect)
        else:
            pygame.draw.rect(image_copy, ORANGE, label_rect)

        # Draw text onto the block surface
        y_offset = label_rect.top + 5
        for line in label_text:
            text_surface = font_xs.render(line, True, BLACK)
            text_rect = text_surface.get_rect(center=(self.block_size // 2, y_offset))
            image_copy.blit(text_surface, text_rect)
            y_offset += font_xs.size(line)[1]

        return image_copy

    def _get_map_data(self, player_block):
        if self.zoom_in:
            map_data = []
            neighbourhood_index = NEIGHBOURHOODS.index(player_block.neighbourhood)
            neighbourhood_x = neighbourhood_index % 10 * 10
            neighbourhood_y = int(neighbourhood_index // 10) * 10

            for y in range(neighbourhood_y, neighbourhood_y + 10):
                for x in range(neighbourhood_x, neighbourhood_x + 10):
                    block = self.city.block(x, y)
                    map_data.append(block.name)
            return map_data
        
        else:
            return NEIGHBOURHOODS
                    

    def _draw_player_location(self, map_data):
        (player_x, player_y) = self.player.location
        current_block = self.city.block(player_x, player_y)
        for index, datum in enumerate(map_data):
            if self.zoom_in:
                if datum == current_block.name:
                    player_index = index
            else:
                if datum == current_block.neighbourhood:
                    player_index = index
        
        # Count the city blocks until player location is reached
        index = 0
        for row in range(self.GRID_ROWS):
            for col in range(self.GRID_COLS):
                if index == player_index:                    
                    # Calculate top-left corner of the city block
                    x = self.BLOCK_PADDING + col * (self.block_size + self.BLOCK_PADDING) + 4
                    y = self.BLOCK_PADDING + row * (self.block_size + self.BLOCK_PADDING) + 4

                    pygame.draw.circle(self.city_map, (255, 0, 0), (x + self.block_size // 2, y + self.block_size // 2 - 10), 10)
                
                index += 1

    def _draw_map_info(self):
        map_info_width = SCREEN_WIDTH - self.MAP_SIZE - 30
        self.map_info = pygame.Surface((map_info_width, self.MAP_SIZE))
        self.map_info.fill((255, 255, 255))
        map_info_text = {
            'preheader': 'The City of',
            'header': 'MALTON',
            'body_1': 'Press ESC to exit map.',
            'body_2': 'Use PAGE UP and PAGE DOWN to zoom.',
        }
        y_offset = 50
        for format, text in map_info_text.items():
            if format == 'header':
                line_size = font_xl.size(text)[1]
                line_surface = font_xl.render(text, True, BLACK)
                line_rect = line_surface.get_rect(midtop=(map_info_width // 2, y_offset))
                self.map_info.blit(line_surface, line_rect)
                y_offset += line_size
            else:
                line_size = font_large.size(text)[1]
                line_surface = font_large.render(text, True, BLACK)
                line_rect = line_surface.get_rect(midtop=(map_info_width // 2, y_offset))
                self.map_info.blit(line_surface, line_rect)
                y_offset += line_size                    

        self.map_surface.blit(self.map_info, (self.MAP_SIZE + 20, 20))