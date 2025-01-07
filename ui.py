# ui.py

import pygame

from settings import *

# Set up action button group
def create_button_group():
    button_group = pygame.sprite.Group()

    buttons = ['barricade', 'search', 'enter']
    for i, button_name in enumerate(buttons):
        button = Button(button_name, button_group, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
        button_group.add(button)
    leave_button = Button('leave', button_group, x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
    button_group.add(leave_button)
    return button_group

class Button(pygame.sprite.Sprite):
    """A set of buttons that change images on mouse events."""
    def __init__(self, name, button_group, x, y):
        super().__init__()
        self.name = name
        self.x, self.y = x, y
        self.button_group = button_group
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

# Handle text wrapping
def wrap_text(text, font, max_width):
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

# Get the neighbourhood of a city block
def get_neighbourhood(block, neighbourhood_groups):
    for group_name, group in neighbourhood_groups.items():
        if block in group:
            return group_name
    return None

# Draw viewport
viewport_frame = pygame.image.load('assets/viewport_frame.png')

def draw_viewport(screen, player, viewport_group):
    """Draw the 3x3 viewport representing the player's surroundings."""
    
    viewport_frame_width, viewport_frame_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2
    # grid_start_x, grid_start_y = (viewport_frame_width // 9) + 12, (viewport_frame_height // 9) + 12
    current_block = player.get_block_at_player(player)

    scaled_viewport_frame = pygame.transform.scale(viewport_frame, (viewport_frame_width, viewport_frame_height))
    screen.blit(scaled_viewport_frame, (10, 10))

    viewport_group.draw(screen)

    # Draw neighbourhood name
    pygame.draw.rect(screen, ORANGE, (10, viewport_frame_height + 10, viewport_frame_width, 20))
    neighbourhood_name = get_neighbourhood(current_block, player.city.neighbourhood_groups)
    text = font_small.render(neighbourhood_name, True, WHITE)
    screen.blit(text, ((viewport_frame_width // 2) - (text.get_width() // 2), viewport_frame_height + 15))

# Draw actions panel
def draw_actions_panel(screen):
    """Draw the Available Actions panel with button sprites."""

    # Panel dimensions
    panel_x = 10
    panel_y = (SCREEN_HEIGHT // 2) + 30
    panel_width = SCREEN_HEIGHT // 2
    panel_height = (SCREEN_HEIGHT // 4) - 80

    # Draw the panel background and border
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

    # Render the title
    title_text = font_large.render("Available Actions", True, BLACK)
    title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 20))
    screen.blit(title_text, title_rect)

def get_current_observations(player):
    """Get the current observations based on the player's surroundings."""
    current_block = player.get_block_at_player(player)
    current_observations = ""

    # Inside building observations
    if player.inside:
        current_observations += f'You are standing inside {current_block.block_name}. '
        if not current_block in player.lights_on:
            current_observations += 'With the lights out, you can hardly see anything. '
        current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "

        # Check if the building has a running generator
        if current_block in player.generator_installed:
            current_observations += "A portable generator has been set up here. "
            if current_block in player.lights_on:
                current_observations += "It is running. "
            else:
                current_observations += "It is out of fuel. "
    # Outside building observations
    else:
        if current_block in player.city.building_group:
            current_observations += f'You are standing outside {current_block.block_desc}. A sign reads "{current_block.block_name}". '
            current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "
            if current_block in player.lights_on:
                current_observations += "Lights are on inside. "
        else:
            current_observations += f'You are standing in {current_block.block_desc}.'

    # Add observations for zombies and dead bodies
    zombies_here = [
        zombie for zombie in player.zombie_group
        if zombie.get_coordinates() == player.location and zombie.inside == player.inside
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


def update_observations(player):
    """Update the observations list based on the player's current state."""
    current_block = player.get_block_at_player(player)
    current_block.observations.clear()  # Clear existing observations
    if player.inside:
        current_block.observations.append(get_current_observations(player))
        current_block.observations.append(current_block.block_inside_desc)
    else:
        current_block.observations.append(get_current_observations(player))
        current_block.observations.append(current_block.block_outside_desc)

def description(player):
    """Return the current list of observations as a list."""
    current_block = player.get_block_at_player(player)
    update_observations(player)  # Ensure observations are current
    return current_block.observations

# Draw description panel
description_panel_image = pygame.image.load("assets/description_panel.png")

def draw_description_panel(screen, player, zombie_display_group):
    """Draw the description panel on the right side of the screen."""

    description_start_x = SCREEN_WIDTH // 3 + 10
    description_width = SCREEN_WIDTH * 2 // 3 - 10
    description_height = SCREEN_HEIGHT * 25 // 32

    scaled_panel_image = pygame.transform.scale(description_panel_image, (description_width, description_height))
    screen.blit(scaled_panel_image, (description_start_x, 10))

    # Determine the setting image
    current_block = player.get_block_at_player(player)
    for group, blocks in player.city.outdoor_type_groups.items():
        if current_block in blocks:
            block_type = group.lower()
    for group, blocks in player.city.building_type_groups.items():
        if current_block in blocks:
            block_type = group.lower()
    image_suffix = "inside" if player.inside else "outside"
    image_path = f"assets/{block_type}_{image_suffix}.png"

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
    screen.blit(scaled_setting_image, (setting_image_x, setting_image_y))
    zombie_display_group.draw(screen)

    # Get the description text and wrap it to fit within the panel
    text_start_y = setting_image_y + setting_image_height + 20
    paragraphs = []
    current_observations = description(player)
    for observation in current_observations:
        wrapped_text = wrap_text(observation, font_large, description_width - 100)  # 50px padding on each side
        for line in wrapped_text:
            paragraphs.append(line)
        paragraphs.append(" ")

    # Render each paragraph inside the description panel
    for line in paragraphs:
        text = font_large.render(line, True, BLACK)
        text_rect = text.get_rect(x=description_start_x + 50, y=text_start_y)  # Padding of 50px on the left
        screen.blit(text, text_rect)
        text_start_y += font_large.size(line)[1]  # Move down for the next line

# Draw the chat panel
def draw_chat(screen, chat_history, scroll_offset):
    """Draw the chat window with scrolling support and text wrapping."""
    chat_width, chat_height = SCREEN_WIDTH // 3 - 10, CHAT_HEIGHT
    chat_start_x, chat_start_y = 10, SCREEN_HEIGHT - chat_height - 10


    # Draw the chat window.
    pygame.draw.rect(screen, BLACK, (chat_start_x, chat_start_y, chat_width, chat_height))
    pygame.draw.rect(screen, WHITE, (chat_start_x, chat_start_y, chat_width, chat_height), 2)

    # Draw messages starting from the bottom of the chat area
    # Calculate the max number of visible lines.
    max_visible_lines = (chat_height - 20) // 20
    wrapped_history = []
    for message in chat_history:
        wrapped_history.extend(wrap_text(f">> {message}", font_chat, chat_width - 20))

    total_lines = len(wrapped_history)

    # Limit scroll_offset to valid bounds.
    scroll_offset = max(0, min(scroll_offset, max(0, total_lines - max_visible_lines)))

    # Determine which messages to display based on scroll_offset
    visible_history = wrapped_history[scroll_offset:scroll_offset + max_visible_lines]
    y_offset = chat_start_y + chat_height - 30

    line_height = font_chat.get_linesize()

    for message in reversed(visible_history):
            text = font_chat.render(message, True, WHITE)
            screen.blit(text, (chat_start_x + 10, y_offset))
            y_offset -= line_height

# Draw the player status panel
def draw_status(screen, player):
    """Draw the player status panel."""
    status_start_x, status_start_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT - 150
    status_width, status_height = SCREEN_WIDTH // 4 - 20, 140

    pygame.draw.rect(screen, BLACK, (status_start_x, status_start_y, status_width, status_height))
    pygame.draw.rect(screen, WHITE, (status_start_x, status_start_y, status_width, status_height), 2)

    y_offset = status_start_y + 10
    status_text = []
    for status_type, status in player.status().items():
        line = f"{status_type}: {status}"
        status_text.append(line)

    for line in status_text:
        text = font_large.render(line, True, WHITE)
        screen.blit(text, (status_start_x + 10, y_offset))
        y_offset += 20

# Draw the inventory panel
def draw_inventory_panel(screen, player):
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
    pygame.draw.rect(screen, BLACK, (panel_x, panel_y, panel_width, panel_height))
    pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

    # Draw equipped sub-panel
    pygame.draw.rect(screen, WHITE, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height))
    pygame.draw.rect(screen, BLACK, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height), 2)

    # Draw "Equipped" label
    equipped_label = font_large.render("Equipped", True, BLACK)
    label_rect = equipped_label.get_rect(center=(equipped_panel_x + equipped_panel_width // 2, equipped_panel_y + 20))
    screen.blit(equipped_label, label_rect)

    # Render equipped item (if any)
    if player.weapon:
        # Draw enlarged equipped item
        enlarged_image = pygame.transform.scale(player.weapon.sprite.image, (64, 64))
        equipped_item_x = equipped_panel_x + (equipped_panel_width - 64) // 2
        equipped_item_y = equipped_panel_y + 40
        screen.blit(enlarged_image, (equipped_item_x, equipped_item_y))

    # Draw inventory sub-panel
    pygame.draw.rect(screen, WHITE, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height))
    pygame.draw.rect(screen, BLACK, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height), 2)

    # Position inventory items
    item_x = inventory_panel_x + 10  # Start with padding
    item_y = inventory_panel_y + (inventory_panel_height // 2 - 16)  # Center items vertically
    for item in player.inventory:
        
        # Update item rect with its position
        item.rect.x = item_x
        item.rect.y = item_y

        # Highlight the equipped item
        if item == player.weapon:
            pygame.draw.rect(screen, WHITE, (item_x - 2, item_y - 2, 36, 36), 2)

        # Move to the next position
        item_x += 36  # Item width + spacing
        if item_x + 36 > inventory_panel_x + inventory_panel_width:  # Wrap to next line if out of space
            item_x = inventory_panel_x + 10
            item_y += 36