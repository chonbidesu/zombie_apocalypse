import pygame
from settings import *
from ui.utils import wrap_text
from widgets import Button

class ActionsPanel:
    """Draw the actions panel and buttons."""
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.x = 10
        self.y = (SCREEN_HEIGHT // 2) + 40
        self.width = SCREEN_HEIGHT // 2
        self.height = SCREEN_HEIGHT * 3 // 20 - 10
        self.button_group = self.create_button_group()
        self.enter_button = Button('enter', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
        self.leave_button = Button('leave', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)        

    def draw(self):
        # Draw the panel background and border
        pygame.draw.rect(self.screen, WHITE, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(self.screen, BLACK, (self.x, self.y, self.width, self.height), 2)

        # Render the title
        title_text = font_large.render("Available Actions", True, BLACK)
        title_rect = title_text.get_rect(center=(self.x + self.width // 2, self.y + 30))
        self.screen.blit(title_text, title_rect)
        self.button_group.draw(self.screen)        

    # Set up action button group
    def create_button_group(self):
        button_group = pygame.sprite.Group()

        buttons = ['barricade', 'search', 'enter']
        for i, button_name in enumerate(buttons):
            button = Button(button_name, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
            button_group.add(button)
        return button_group        

    # Update action buttons according to player status
    def update_action_buttons(self):
        if self.game.player.inside:
            for button in self.button_group:
                if button.name == 'enter':
                    self.button_group.remove(button)
                    self.button_group.add(self.leave_button)
        else:
            for button in self.button_group:
                if button.name == 'leave':
                    self.button_group.remove(button)
                    self.button_group.add(self.enter_button)        


class StatusPanel:
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.hp_bar = pygame.image.load("assets/hp_bar.png").convert_alpha()
        self.player_frame = pygame.image.load("assets/player_frame.png").convert_alpha()

    def draw(self):
        status_x, status_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT * 25 // 32 + 10
        status_width, status_height = SCREEN_WIDTH // 4 - 10, SCREEN_HEIGHT * 31 // 160
        status_panel = pygame.Surface((status_width, status_height), pygame.SRCALPHA)

        # Draw HP bar
        max_hp = self.game.player.max_hp
        current_hp = self.game.player.hp
        hp_ratio = max(current_hp / max_hp, 0)

        pygame.draw.rect(status_panel, (255, 0, 0), (0, status_height - 20, status_width, 20))
        pygame.draw.rect(status_panel, (0, 255, 0), (0, status_height - 20, status_width * hp_ratio, 20))

        # Blit to screen
        self.screen.blit(status_panel, (status_x, status_y))

class ChatPanel:
    def __init__(self, screen):
        self.screen = screen
        self.chat_image = pygame.image.load("assets/chat_panel.png").convert_alpha()

    def draw(self, chat_history):
        chat_x, chat_y = 10, SCREEN_HEIGHT * 13 // 20 + 30
        chat_width, chat_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT * 3 // 10
        self.screen.blit(pygame.transform.scale(self.chat_image, (chat_width, chat_height)), (chat_x, chat_y))

        # Render chat messages
        wrapped_history = []
        for message in chat_history:
            wrapped_history.extend(wrap_text(f">> {message}", font_chat, chat_width - 50))

        y_offset = chat_y + chat_height - 40
        for message in reversed(wrapped_history[-10:]):  # Show last 10 messages
            text = font_chat.render(message, True, WHITE)
            self.screen.blit(text, (chat_x + 30, y_offset))
            y_offset -= font_chat.get_linesize()


class DescriptionPanel:
    """Draw the description panel on the right side of the screen."""
    def __init__(self, screen, game):
        self.screen = screen
        self.game = game
        self.x = SCREEN_HEIGHT // 2 + 10
        self.width = SCREEN_WIDTH - (SCREEN_HEIGHT // 2) - 20
        self.height = SCREEN_HEIGHT * 25 // 32
        
        self.image = pygame.image.load("assets/description_panel.png").convert_alpha()
        self.scaled_image = pygame.transform.scale(self.image, (self.width, self.height))

        self.setting_image_x = self.x + (self.width - setting_image.get_width()) // 2
        self.setting_image_y = 50
        self.setting_width = self.width * 5 // 6
        self.setting_height = self.setting_width * 4 // 9  # 9:4 aspect ratio

    def draw(self):
        self.screen.blit(self.scaled_image, (self.x, 10))

        # Blit the setting image at the top of the panel
        setting_image = self._get_setting_image()
        self.screen.blit(setting_image, (self.setting_image_x, self.setting_image_y))        

    def _get_setting_image(self):
        """Determine the setting image."""
        current_x, current_y = self.game.player.location
        current_block = self.game.city.block(current_x, current_y)        
        image_suffix = "inside" if self.game.player.inside else "outside"
        image_path = f"assets/{current_block.type.name.lower()}_{image_suffix}.png"

        try:
            setting_image = pygame.image.load(image_path)
        except FileNotFoundError:
            setting_image = pygame.Surface((1, 1))  # Fallback if image not found
            setting_image.fill((0, 0, 0))

        # Scale the setting image
        return pygame.transform.scale(setting_image, (self.setting_width, self.setting_height))

    def _position_npc_sprites(self, zombie_sprite_group, human_sprite_group): #####################
        # Arrange sprite groups in a row, aligning their bottom edges
        sprite_width = 50  # Define the width for each zombie sprite
        sprite_spacing = 20  # Define the spacing between sprites
        zombie_row_start_x = self.setting_image_x + self.setting_width - len(self.zombie_sprite_group) * (sprite_width + sprite_spacing) - 10
        human_row_start_x = self.setting_image_x + 20
        row_start_y = self.setting_image_y + setting_height  # Align with bottom edge of setting image

        for index, sprite in enumerate(self.zombie_sprite_group):
            # Calculate position for each zombie sprite
            sprite.rect.midbottom = (
                zombie_row_start_x + index * (sprite_width + sprite_spacing) + sprite_width // 2,
                row_start_y
            )

        for index, sprite in enumerate(self.human_sprite_group):
            # Calculate position for each zombie sprite
            sprite.rect.midbottom = (
                human_row_start_x + index * (sprite_width + sprite_spacing) + sprite_width // 2,
                row_start_y
            )

        self.zombie_sprite_group.update()
        self.zombie_sprite_group.draw(self.screen)

        self.human_sprite_group.update()
        self.human_sprite_group.draw(self.screen)        

        # Get the description text and wrap it to fit within the panel
        text_start_y = setting_image_y + setting_image_height + 20
        paragraphs = []
        current_observations = self.description()
        for observation in current_observations:
            wrapped_text = self.wrap_text(observation, font_large, self.width - 100)  # 50px padding on each side
            for line in wrapped_text:
                paragraphs.append(line)
            paragraphs.append(" ")

        # Render each paragraph inside the description panel
        for line in paragraphs:
            text = font_large.render(line, True, BLACK)
            text_rect = text.get_rect(x=self.x + 50, y=text_start_y)  # Padding of 50px on the left
            self.screen.blit(text, text_rect)
            text_start_y += font_large.size(line)[1]  # Move down for the next line


class Map:
    def __init__(self, screen, player, wrap_text):
        self.screen = screen
        self.player = player
        self.wrap_text = wrap_text
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
        player_block = self.player.city.block(self.player.location[0], self.player.location[1])

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
                    player_block = self.player.city.block(self.player.location[0], self.player.location[1])
                    neighbourhood_index = NEIGHBOURHOODS.index(player_block.neighbourhood)
                    col_offset = neighbourhood_index % 10 * 10
                    row_offset = int(neighbourhood_index // 10) * 10
                    current_block = self.player.city.block(col + col_offset, row + row_offset)

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
        label_text = self.wrap_text(label_name, font_xs, self.block_size - 2)
        text_height = sum(font_xs.size(line)[1] for line in label_text)

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
                    block = self.player.city.block(x, y)
                    map_data.append(block.name)
            return map_data
        
        else:
            return NEIGHBOURHOODS
                    

    def _draw_player_location(self, map_data):
        (player_x, player_y) = self.player.location
        current_block = self.player.city.block(player_x, player_y)
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