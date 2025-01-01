# ui.py

import pygame

from settings import *

class Button(pygame.sprite.Sprite):
    """A button that changes images on mouse events."""
    def __init__(self, name, x, y):
        super().__init__()
        self.name = name
        self.image_up = pygame.image.load(f"assets/{name}_up.bmp")
        self.image_up = pygame.transform.scale(self.image_up, (100, 49))
        self.image_down = pygame.image.load(f"assets/{name}_down.bmp")
        self.image_down = pygame.transform.scale(self.image_down, (100, 49))
        self.image = self.image_up
        self.rect = self.image.get_rect(topleft = (x, y))
        self.is_pressed = False

    def handle_event(self, event):
        """Handle mouse events to change button state."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.image = self.image_down
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.image = self.image_up
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    return self.name # Return the button name when clicked
                
        return None
    
    def update(self):
        """Update the button's visual state."""
        # The image has already been changed in handle_event; nothing extra needed here
        pass

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

def draw_viewport(screen, player, viewport_rows, font_small):
    """Draw the 3x3 viewport representing the player's surroundings."""
    viewport_frame_width, viewport_frame_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2
    grid_start_x, grid_start_y = (viewport_frame_width // 9) + 12, (viewport_frame_height // 9) + 12
    player_x, player_y = player.location
    current_block = player.get_block_at_player()
    neighbourhood_groups = player.neighbourhood_groups

    scaled_viewport_frame = pygame.transform.scale(viewport_frame, (viewport_frame_width, viewport_frame_height))
    screen.blit(scaled_viewport_frame, (10, 10))

    for row_index, row in enumerate(viewport_rows):
        for col_index, block in enumerate(row):
            if block is None:
                continue

            # Calculate the block's position relative to the viewport
            block_rect_x = grid_start_x + col_index * BLOCK_SIZE
            block_rect_y = grid_start_y + row_index * BLOCK_SIZE

            screen.blit(block.image, (block_rect_x, block_rect_y))

            block_text = wrap_text(block.block_name, font_small, BLOCK_SIZE - 10)
            text_height = sum(font_small.size(line)[1] for line in block_text)
            # Adjust button_rect to align with bottom of block_rect
            button_rect = pygame.Rect(
                block_rect_x, block_rect_y + BLOCK_SIZE - text_height - 10, 
                BLOCK_SIZE, text_height + 10)
            pygame.draw.rect(screen, WHITE, button_rect)
            y_offset = button_rect.top + (button_rect.height - text_height)  # Center text vertically

            for line in block_text:
                text = font_small.render(line, True, BLACK)
                text_rect = text.get_rect(center=(button_rect.centerx, y_offset))
                screen.blit(text, text_rect)
                y_offset += font_small.size(line)[1]  # Move down for the next line

    # Draw neighbourhood name
    pygame.draw.rect(screen, ORANGE, (10, viewport_frame_height + 10, viewport_frame_width, 20))
    neighbourhood_name = get_neighbourhood(current_block, neighbourhood_groups)
    text = font_small.render(neighbourhood_name, True, WHITE)
    screen.blit(text, ((viewport_frame_width // 2) - (text.get_width() // 2), viewport_frame_height + 15))

# Draw actions panel
def draw_actions_panel(screen, font_large):
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

# Draw description panel
description_panel_image = pygame.image.load("assets/description_panel.png")

def draw_description_panel(screen, player, font_large):
    """Draw the description panel on the right side of the screen."""

    description_start_x = SCREEN_WIDTH // 3 + 10
    description_width = SCREEN_WIDTH * 2 // 3 - 10
    description_height = SCREEN_HEIGHT * 25 // 32

    scaled_panel_image = pygame.transform.scale(description_panel_image, (description_width, description_height))
    screen.blit(scaled_panel_image, (description_start_x, 10))

    # Get the description text and wrap it to fit within the panel
    paragraphs = []
    current_observations = player.description()
    for observation in current_observations:
        wrapped_text = wrap_text(observation, font_large, description_width - 100)  # 50px padding on each side
        for line in wrapped_text:
            paragraphs.append(line)
        paragraphs.append(" ")

    # Calculate the total height of the formatted text
    total_text_height = sum(font_large.size(line)[1] for line in paragraphs)
    
    # Calculate the starting y_offset to center the text vertically with padding
    y_offset = 20 + (description_height - total_text_height) // 2  # 20px padding at the top of the panel

    # Render each paragraph inside the description panel
    for line in paragraphs:
        text = font_large.render(line, True, BLACK)
        text_rect = text.get_rect(x=description_start_x + 50, y=y_offset)  # Padding of 50px on the left
        screen.blit(text, text_rect)
        y_offset += font_large.size(line)[1]  # Move down for the next line

# Draw the chat panel
def draw_chat(screen, chat_history, input_text, scroll_offset, font_large):
    """Draw the chat window with scrolling support and text wrapping."""
    chat_width, chat_height = SCREEN_WIDTH // 3 - 10, SCREEN_HEIGHT * 1 // 4
    chat_start_x, chat_start_y = 10, SCREEN_HEIGHT - chat_height - 40


    # Draw the chat window.
    pygame.draw.rect(screen, BLACK, (chat_start_x, chat_start_y, chat_width, chat_height))
    pygame.draw.rect(screen, WHITE, (chat_start_x, chat_start_y, chat_width, chat_height), 2)

    # Draw messages starting from the bottom of the chat area
    # Calculate the max number of visible lines.
    max_visible_lines = (chat_height - 20) // 20
    wrapped_history = []
    for message in chat_history:
        wrapped_history.extend(wrap_text(f">> {message}", font_large, chat_width - 20))

    total_lines = len(wrapped_history)

    # Limit scroll_offset to valid bounds.
    scroll_offset = max(0, min(scroll_offset, max(0, total_lines - max_visible_lines)))

    # Determine which messages to display based on scroll_offset
    visible_history = wrapped_history[scroll_offset:scroll_offset + max_visible_lines]
    y_offset = chat_start_y + chat_height - 30

    for message in reversed(visible_history):
            text = font_large.render(message, True, WHITE)
            screen.blit(text, (chat_start_x + 10, y_offset))
            y_offset -= 20

    # Draw input box
    input_box = pygame.Rect(chat_start_x, chat_start_y + chat_height + 5, chat_width - 10, 25)
    pygame.draw.rect(screen, GRAY, input_box)
    input_text_rendered = font_large.render(input_text, True, WHITE)
    screen.blit(input_text_rendered, (input_box.x + 5, input_box.y + 5))

# Draw the player status panel
def draw_status(screen, player, font_large):
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
def draw_inventory_panel(screen, player, font_large):
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
    pygame.draw.rect(screen, GRAY, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height))
    pygame.draw.rect(screen, WHITE, (equipped_panel_x, equipped_panel_y, equipped_panel_width, equipped_panel_height), 2)

    # Draw "Equipped" label
    equipped_label = font_large.render("Equipped", True, WHITE)
    label_rect = equipped_label.get_rect(center=(equipped_panel_x + equipped_panel_width // 2, equipped_panel_y + 20))
    screen.blit(equipped_label, label_rect)

    # Render equipped item (if any)
    if player.weapon:
        # Draw enlarged equipped item
        enlarged_image = pygame.transform.scale(player.weapon.image, (64, 64))
        equipped_item_x = equipped_panel_x + (equipped_panel_width - 64) // 2
        equipped_item_y = equipped_panel_y + 40
        screen.blit(enlarged_image, (equipped_item_x, equipped_item_y))

    # Draw inventory sub-panel
    pygame.draw.rect(screen, GRAY, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height))
    pygame.draw.rect(screen, WHITE, (inventory_panel_x, inventory_panel_y, inventory_panel_width, inventory_panel_height), 2)

    # Render inventory items
    item_x = inventory_panel_x + 10  # Start with padding
    item_y = inventory_panel_y + (inventory_panel_height // 2 - 16)  # Center items vertically
    for item in player.inventory:
        # Draw item image
        screen.blit(item.image, (item_x, item_y))

        # Highlight the equipped item
        if item == player.weapon:
            pygame.draw.rect(screen, WHITE, (item_x - 2, item_y - 2, 36, 36), 2)

        # Move to the next position
        item_x += 36  # Item width + spacing
        if item_x + 36 > inventory_panel_x + inventory_panel_width:  # Wrap to next line if out of space
            item_x = inventory_panel_x + 10
            item_y += 36