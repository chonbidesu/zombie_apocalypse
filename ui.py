# ui.py

import pygame
import random

from settings import *

class DrawUI:
    """A class to draw the ui panel to the screen."""
    def __init__(self, screen, player, city, zombies):
        self.screen = screen
        self.player = player
        self.city = city
        self.zombies = zombies
        self.viewport_frame = pygame.image.load('assets/viewport_frame.png')
        self.description_panel_image = pygame.image.load("assets/description_panel.png")
        self.viewport_frame_width, self.viewport_frame_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2
        self.grid_start_x, self.grid_start_y = (self.viewport_frame_width // 9) + 12, (self.viewport_frame_height // 9) + 12
        self.viewport_group = self.create_viewport_group()
        self.button_group = self.create_button_group()
        self.zombie_display_group = pygame.sprite.Group()

    def draw(self, chat_history, scroll_offset):
        self.draw_viewport_frame()
        self.draw_neighbourhood_name()
        self.draw_actions_panel()
        self.draw_chat(chat_history, scroll_offset)
        self.draw_description_panel()
        self.draw_status()
        self.draw_inventory_panel()
        self.update_viewport()
        self.viewport_group.draw(self.screen)

    #  Set up viewport group
    def create_viewport_group(self):
        viewport_group = pygame.sprite.Group()

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                block_sprite = self.BlockSprite(dx, dy, self.player, self.city, self.grid_start_x, self.grid_start_y, self.wrap_text)
                viewport_group.add(block_sprite)
        return viewport_group

    def update_viewport(self):
        for sprite in self.viewport_group:
            sprite.update_data()

    # Set up action button group
    def create_button_group(self):
        button_group = pygame.sprite.Group()

        buttons = ['barricade', 'search', 'enter']
        for i, button_name in enumerate(buttons):
            button = self.Button(button_name, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
            button_group.add(button)
        leave_button = self.Button('leave', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
        button_group.add(leave_button)
        return button_group

    # Handle text wrapping
    def wrap_text(self, text, font, max_width):
        """Wrap the text to fit inside a given width."""
        lines = []
        words = text.split(" ")
        current_line = ""

        for word in words:
            # Check if adding the word exceeds the width
            test_line = current_line + (word if current_line == "" else " " + word)
            test_width, _ = font.size(test_line)

            if test_width <= max_width:
                current_line = test_line  # Add the word to the current line
            else:
                if current_line != "":
                    lines.append(current_line)  # Append the current line if it's not empty
                current_line = word  # Start a new line with the current word

        if current_line != "":  # Append the last line if it has any content
            lines.append(current_line)

        return lines

    def draw_viewport_frame(self):
        """Draw the 3x3 viewport representing the player's surroundings."""
        
        scaled_viewport_frame = pygame.transform.scale(self.viewport_frame, (self.viewport_frame_width, self.viewport_frame_height))
        self.screen.blit(scaled_viewport_frame, (10, 10))

        # grid_start_x, grid_start_y = (viewport_frame_width // 9) + 12, (viewport_frame_height // 9) + 12

        #self.viewport_group.draw(self.screen)

    def draw_neighbourhood_name(self):
        # Draw neighbourhood name
        current_x, current_y = self.player.location
        current_block = self.city.block(current_x, current_y)
        pygame.draw.rect(self.screen, ORANGE, (10, self.viewport_frame_height + 10, self.viewport_frame_width, 20))
        text = font_small.render(current_block.neighbourhood, True, WHITE)
        self.screen.blit(text, ((self.viewport_frame_width // 2) - (text.get_width() // 2), self.viewport_frame_height + 15))

    # Draw actions panel
    def draw_actions_panel(self):
        """Draw the Available Actions panel with button sprites."""

        # Panel dimensions
        panel_x = 10
        panel_y = (SCREEN_HEIGHT // 2) + 30
        panel_width = SCREEN_HEIGHT // 2
        panel_height = (SCREEN_HEIGHT // 4) - 80

        # Draw the panel background and border
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

        # Render the title
        title_text = font_large.render("Available Actions", True, BLACK)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 20))
        self.screen.blit(title_text, title_rect)

    def get_current_observations(self):
        """Get the current observations based on the player's surroundings."""
        current_x, current_y = self.player.location
        current_block = self.city.block(current_x, current_y)        
        current_observations = ""

        # Inside building observations
        if self.player.inside:
            current_observations += f'You are standing inside {current_block.block_name}. '
            if not current_block.lights_on:
                current_observations += 'With the lights out, you can hardly see anything. '
            current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "

            # Check if the building has a running generator
            if current_block in self.player.generator_installed:
                current_observations += "A portable generator has been set up here. "
                if current_block.lights_on:
                    current_observations += "It is running. "
                else:
                    current_observations += "It is out of fuel. "
        # Outside building observations
        else:
            if current_block.is_building:
                current_observations += f'You are standing outside {current_block.block_desc}. A sign reads "{current_block.block_name}". '
                current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "
                if current_block.lights_on:
                    current_observations += "Lights are on inside. "
            else:
                current_observations += f'You are standing in {current_block.block_desc}.'

        # Add observations for zombies and dead bodies
        zombies_here = [
            zombie for zombie in self.zombies.list
            if zombie.location == self.player.location and zombie.inside == self.player.inside
        ]
        living_zombies = [zombie for zombie in zombies_here if not zombie.is_dead]
        dead_zombies = [zombie for zombie in zombies_here if zombie.is_dead]

        if living_zombies:
            if len(living_zombies) == 1:
                current_observations += "There is a lone zombie here. "
            else:
                current_observations += f"There are {len(living_zombies)} zombies here. "

        if dead_zombies:
            if len(dead_zombies) == 1:
                current_observations += "You see a dead body."
            else:
                current_observations += f"You see {len(dead_zombies)} dead bodies."

        return current_observations


    def update_observations(self):
        """Update the observations list based on the player's current state."""
        current_x, current_y = self.player.location
        current_block = self.city.block(current_x, current_y)        
        current_block.observations.clear()  # Clear existing observations
        if self.player.inside:
            current_block.observations.append(self.get_current_observations())
            current_block.observations.append(current_block.block_inside_desc)
        else:
            current_block.observations.append(self.get_current_observations())
            current_block.observations.append(current_block.block_outside_desc)

    def description(self):
        """Return the current list of observations as a list."""
        current_x, current_y = self.player.location
        current_block = self.city.block(current_x, current_y)        
        self.update_observations()  # Ensure observations are current
        return current_block.observations

    def draw_description_panel(self):
        """Draw the description panel on the right side of the screen."""

        description_start_x = SCREEN_WIDTH // 3 + 10
        description_width = SCREEN_WIDTH * 2 // 3 - 10
        description_height = SCREEN_HEIGHT * 25 // 32

        scaled_panel_image = pygame.transform.scale(self.description_panel_image, (description_width, description_height))
        self.screen.blit(scaled_panel_image, (description_start_x, 10))

        # Determine the setting image
        current_x, current_y = self.player.location
        current_block = self.city.block(current_x, current_y)        
        image_suffix = "inside" if self.player.inside else "outside"
        image_path = f"assets/{current_block.block_type.lower()}_{image_suffix}.png"

        try:
            setting_image = pygame.image.load(image_path)
        except FileNotFoundError:
            setting_image = pygame.Surface((1, 1))  # Fallback if image not found
            setting_image.fill((0, 0, 0))

        # Scale the setting image
        setting_image_width = description_width * 5 // 6
        setting_image_height = setting_image_width * 4 // 9  # 9:4 aspect ratio
        scaled_setting_image = pygame.transform.scale(setting_image, (setting_image_width, setting_image_height))

        # Blit the setting image at the top of the panel
        setting_image_x = description_start_x + (description_width - setting_image_width) // 2
        setting_image_y = 50
        self.screen.blit(scaled_setting_image, (setting_image_x, setting_image_y))
        self.zombie_display_group.draw(self.screen)

        # Get the description text and wrap it to fit within the panel
        text_start_y = setting_image_y + setting_image_height + 20
        paragraphs = []
        current_observations = self.description()
        for observation in current_observations:
            wrapped_text = self.wrap_text(observation, font_large, description_width - 100)  # 50px padding on each side
            for line in wrapped_text:
                paragraphs.append(line)
            paragraphs.append(" ")

        # Render each paragraph inside the description panel
        for line in paragraphs:
            text = font_large.render(line, True, BLACK)
            text_rect = text.get_rect(x=description_start_x + 50, y=text_start_y)  # Padding of 50px on the left
            self.screen.blit(text, text_rect)
            text_start_y += font_large.size(line)[1]  # Move down for the next line

    # Draw the chat panel
    def draw_chat(self, chat_history, scroll_offset):
        """Draw the chat window with scrolling support and text wrapping."""
        chat_width, chat_height = SCREEN_WIDTH // 3 - 10, CHAT_HEIGHT
        chat_start_x, chat_start_y = 10, SCREEN_HEIGHT - chat_height - 10


        # Draw the chat window.
        pygame.draw.rect(self.screen, BLACK, (chat_start_x, chat_start_y, chat_width, chat_height))
        pygame.draw.rect(self.screen, WHITE, (chat_start_x, chat_start_y, chat_width, chat_height), 2)

        # Draw messages starting from the bottom of the chat area
        # Calculate the max number of visible lines.
        max_visible_lines = (chat_height - 20) // 20
        wrapped_history = []
        for message in chat_history:
            wrapped_history.extend(self.wrap_text(f">> {message}", font_chat, chat_width - 20))

        total_lines = len(wrapped_history)

        # Limit scroll_offset to valid bounds.
        scroll_offset = max(0, min(scroll_offset, max(0, total_lines - max_visible_lines)))

        # Determine which messages to display based on scroll_offset
        visible_history = wrapped_history[scroll_offset:scroll_offset + max_visible_lines]
        y_offset = chat_start_y + chat_height - 30

        line_height = font_chat.get_linesize()

        for message in reversed(visible_history):
                text = font_chat.render(message, True, WHITE)
                self.screen.blit(text, (chat_start_x + 10, y_offset))
                y_offset -= line_height

    # Draw the player status panel
    def draw_status(self):
        """Draw the player status panel."""
        status_start_x, status_start_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT - 150
        status_width, status_height = SCREEN_WIDTH // 4 - 20, 140

        pygame.draw.rect(self.screen, BLACK, (status_start_x, status_start_y, status_width, status_height))
        pygame.draw.rect(self.screen, WHITE, (status_start_x, status_start_y, status_width, status_height), 2)

        y_offset = status_start_y + 10
        status_text = []
        for status_type, status in self.player.status().items():
            line = f"{status_type}: {status}"
            status_text.append(line)

        for line in status_text:
            text = font_large.render(line, True, WHITE)
            self.screen.blit(text, (status_start_x + 10, y_offset))
            y_offset += 20

    # Draw the inventory panel
    def draw_inventory_panel(self):
        """Render the inventory panel in the bottom-right corner of the screen."""
        # Panel dimensionss
        panel_width = SCREEN_WIDTH * 5 // 12 - 20
        panel_height = 140
        panel_x = SCREEN_WIDTH - panel_width - 10
        panel_y = SCREEN_HEIGHT - panel_height - 10

        # Sub-panel dimensions
        equipped_panel_width = panel_width // 4
        equipped_panel_height = panel_height
        equipped_panel_x = panel_x
        equipped_panel_y = panel_y

        inventory_panel_width = panel_width - equipped_panel_width
        inventory_panel_height = panel_height
        inventory_panel_x = panel_x + equipped_panel_width
        inventory_panel_y = panel_y

        # Draw main panel
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

        # Draw equipped sub-panel
        pygame.draw.rect(self.screen, WHITE, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height))
        pygame.draw.rect(self.screen, BLACK, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height), 2)

        # Draw "Equipped" label
        equipped_label = font_large.render("Equipped", True, BLACK)
        label_rect = equipped_label.get_rect(center=(equipped_panel_x + equipped_panel_width // 2, equipped_panel_y + 20))
        self.screen.blit(equipped_label, label_rect)

        # Render equipped item (if any)
        if self.player.weapon:
            # Draw enlarged equipped item
            enlarged_image = pygame.transform.scale(self.player.weapon.sprite.image, (64, 64))
            equipped_item_x = equipped_panel_x + (equipped_panel_width - 64) // 2
            equipped_item_y = equipped_panel_y + 40
            self.screen.blit(enlarged_image, (equipped_item_x, equipped_item_y))

        # Draw inventory sub-panel
        pygame.draw.rect(self.screen, WHITE, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height))
        pygame.draw.rect(self.screen, BLACK, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height), 2)

        # Position inventory items
        item_x = inventory_panel_x + 10  # Start with padding
        item_y = inventory_panel_y + (inventory_panel_height // 2 - 16)  # Center items vertically
        for item in self.player.inventory:
            
            # Update item rect with its position
            item.rect.x = item_x
            item.rect.y = item_y

            # Highlight the equipped item
            if item == self.player.weapon:
                pygame.draw.rect(self.screen, WHITE, (item_x - 2, item_y - 2, 36, 36), 2)

            # Move to the next position
            item_x += 36  # Item width + spacing
            if item_x + 36 > inventory_panel_x + inventory_panel_width:  # Wrap to next line if out of space
                item_x = inventory_panel_x + 10
                item_y += 36



    class BlockSprite(pygame.sprite.Sprite):
        """
        Represents a visual sprite for a CityBlock in the viewport.

        The sprite remains fixed at a dx, dy position in the viewport and dynamically updates
        its data (block_type, block_name) based on the player's current location and
        surrounding CityBlock objects.
        """

        def __init__(self, dx, dy, player, city, grid_start_x, grid_start_y, wrap_text):
            """
            Initialize the BlockSprite.

            Args:
                dx (int): The relative x position (-1, 0, 1) in the 3x3 grid.
                dy (int): The relative y position (-1, 0, 1) in the 3x3 grid.
                grid_start_x (int): The top-left x-coordinate of the viewport.
                grid_start_y (int): The top-left y-coordinate of the viewport.
            """
            super().__init__()
            self.dx = dx
            self.dy = dy
            self.player = player
            self.city = city
            self.block = None # The block this sprite represents
            self.is_building = False
            self.wrap_text = wrap_text
            self.viewport_x = grid_start_x + (dx + 1) * BLOCK_SIZE  # Translate relative dx to viewport position
            self.viewport_y = grid_start_y + (dy + 1) * BLOCK_SIZE  # Translate relative dy to viewport position
            self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            self.rect = self.image.get_rect(topleft=(self.viewport_x, self.viewport_y))


        def update_data(self):
            """
            Update the sprite's data based on the player's current location and CityBlock objects.

            Args:
                player (Player): The player object, containing the current location.
                city (City): The city object, which provides access to CityBlock objects.
            """
            # Determine the target block coordinates based on player location and dx, dy offsets
            target_x = self.player.location[0] + self.dx
            target_y = self.player.location[1] + self.dy

            # Check if the target coordinates are within city bounds
            if 0 <= target_x < CITY_SIZE and 0 <= target_y < CITY_SIZE:
                self.block = self.city.block(target_x, target_y)  # Retrieve the CityBlock at (x, y)

                image_filename = BLOCK_IMAGES[self.block.block_type]
                self.image = pygame.image.load(image_filename).convert_alpha()
                self.image = pygame.transform.scale(self.image, (BLOCK_SIZE, BLOCK_SIZE))

                if self.block.block_type == 'Street':
                    self.apply_zoomed_image()

                # Update the visual representation
                self.draw_block_label()

        def draw_block_label(self):
            """Render the block label onto the block's surface."""
            block_text = self.wrap_text(self.block.block_name, font_small, BLOCK_SIZE - 10)
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


    class ViewportZombie(pygame.sprite.Sprite):
        """A green square to represent a zombie in the viewport."""
        def __init__(self, zombie, dx, dy):
            """
            Initialize the ViewportZombie sprite.

            Args:
                zombie (Zombie): Reference to the parent zombie object.
                dx (int): Relative x position in the viewport (-1, 0, 1).
                dy (int): Relative y position in the viewport (-1, 0, 1).
                viewport_start_x (int): Top-left x-coordinate of the viewport.
                viewport_start_y (int): Top-left y-coordinate of the viewport.
            """
            super().__init__()
            self.zombie = zombie
            self.dx = dx
            self.dy = dy
            self.image = pygame.Surface((BLOCK_SIZE // 2, BLOCK_SIZE // 2))  # Smaller green square
            self.image.fill((0, 255, 0))  # Green color for zombies
            self.rect = self.image.get_rect()
            self.viewport_x = self.viewport_start_x + (dx + 1) * BLOCK_SIZE + (BLOCK_SIZE // 4)
            self.viewport_y = self.viewport_start_y + (dy + 1) * BLOCK_SIZE + (BLOCK_SIZE // 4)
            self.rect.topleft = (self.viewport_x, self.viewport_y)

        def update_position(self, dx, dy):
            """
            Update the zombie's position based on dx, dy in the viewport.
            
            Args:
                dx (int): Updated relative x position.
                dy (int): Updated relative y position.
            """
            self.rect.topleft = (
                self.viewport_x + dx * BLOCK_SIZE,
                self.viewport_y + dy * BLOCK_SIZE,
            )


    class ZombieSprite(pygame.sprite.Sprite):
        """A detailed zombie sprite for the description panel."""
        def __init__(self, zombie, image_path, panel_position):
            super().__init__()
            self.zombie = zombie  # Reference to the parent zombie
            self._image = None  # Private attribute for image
            self.image_path = image_path  # Store the path for lazy loading
            self.rect = pygame.Rect(panel_position, (100, 150))  # Example size for sprite rect

        @property
        def image(self):
            """Lazy load the image when accessed."""
            if self._image is None:
                # Load and transform the image when it's first needed
                self._image = pygame.image.load(self.image_path).convert_alpha()
                self._image = pygame.transform.scale(self._image, (100, 150))  # Scale to desired size
            return self._image

        @image.setter
        def image(self, value):
            """Setter for image, useful if you need to manually set the image."""
            self._image = value

    class Button(pygame.sprite.Sprite):
        """A button that changes images on mouse events."""
        def __init__(self, name, x, y):
            super().__init__()
            self.name = name
            self.x, self.y = x, y
            self.is_pressed = False
            self._image_up = None  # Private attributes for lazy-loaded images
            self._image_down = None
            self.rect = pygame.Rect(x, y, 100, 49)  # Initial rect size (scale later when image is loaded)

        @property
        def image_up(self):
            """Lazy load the 'up' image when first accessed."""
            if self._image_up is None:
                self._image_up = pygame.image.load(f"assets/{self.name}_up.bmp")
                self._image_up = pygame.transform.scale(self._image_up, (100, 49))  # Scale when loading
            return self._image_up

        @property
        def image_down(self):
            """Lazy load the 'down' image when first accessed."""
            if self._image_down is None:
                self._image_down = pygame.image.load(f"assets/{self.name}_down.bmp")
                self._image_down = pygame.transform.scale(self._image_down, (100, 49))  # Scale when loading
            return self._image_down

        @property
        def image(self):
            """Return the current image based on button state."""
            if self.is_pressed:
                return self.image_down
            else:
                return self.image_up

        @image.setter
        def image(self, value):
            """Setter for image, in case the image needs to be manually set."""
            # This can be used if you want to manually change the image
            pass

        def handle_event(self, event):
            """Handle mouse events to change button state."""
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.rect.collidepoint(event.pos):
                    self.is_pressed = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.is_pressed:
                    self.is_pressed = False
                    if self.rect.collidepoint(event.pos):
                        return self.name  # Return the button name when clicked
                    
            return None
        
        def update(self):
            """Update the button's visual state."""
            # Update image based on button press state
            self.image = self.image  # This just triggers the lazy loading based on current state
