# main.py
import pygame
import sys
import random

from settings import *
from player import Player
import city_generation
import ui

# Initialize Pygame
pygame.init()

# Create dictionaries to manage the x, y coordinate groups
x_groups = {x: pygame.sprite.Group() for x in range(100)}
y_groups = {y: pygame.sprite.Group() for y in range(100)}

# Set up action button group
button_group = pygame.sprite.Group()
buttons = ['barricade', 'search']
for i, button_name in enumerate(buttons):
    button = ui.Button(button_name, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
    button_group.add(button)
enter_button = ui.Button('enter', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
button_group.add(enter_button)
leave_button = ui.Button('leave', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)

# Initialize city
city_generation.generate_city(x_groups, y_groups)
city_generation.generate_neighbourhoods(x_groups, y_groups)

# Create screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Apocalypse")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont(None, 16)
font_large = pygame.font.SysFont(None, 24)

# Create player
player = Player(
    x_groups, y_groups, city_generation.cityblock_group, city_generation.building_group, city_generation.building_type_groups, city_generation.neighbourhood_groups,
    button_group, enter_button, leave_button, name="Alice", occupation="Doctor", x=50, y=50, 
)

# Apply zoomed-in image of street grid to street sprites to randomize street appearance
def apply_zoomed_image(block_image):
    """Apply a zoomed-in portion of the block image."""
    street_group = city_generation.outdoor_type_groups['Street']
    image_width, image_height = block_image.get_width(), block_image.get_height()

    # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
    zoom_factor = 2
    zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

    for sprite in street_group:
        # Generate random top-left coordinates for the zoomed-in area
        zoom_x = random.randint(0, image_width - zoom_width)
        zoom_y = random.randint(0, image_height - zoom_height)

        # Extract the zoomed-in portion
        zoomed_surface = block_image.subsurface((zoom_x, zoom_y, zoom_width, zoom_height))

        # Scale it to the target block size and assign to sprite
        zoomed_surface = pygame.transform.scale(zoomed_surface, (BLOCK_SIZE, BLOCK_SIZE))
        sprite.image = zoomed_surface

# Load the street images
street_image = pygame.image.load(BLOCK_IMAGES['Street'])
apply_zoomed_image(street_image)

# Get (x, y) of a specific sprite
def get_sprite_coordinates(sprite):
    for x, group in x_groups.items():
        if sprite in group:
            x_coordinate = x
            break

    for y, group in y_groups.items():
        if sprite in group:
            y_coordinate = y
            break

    return x_coordinate, y_coordinate

# Update viewport centered on player
def update_viewport():
    viewport_rows = []
    player_x, player_y = player.location

    # Collect blocks in a 3x3 grid around the player
    for row_offset in range(-1, 2):
        row = []
        for col_offset in range(-1, 2):
            block_x, block_y = player_x + col_offset, player_y + row_offset

            #Ensure block coordinates are within city bounds
            if block_x in x_groups and block_y in y_groups:
                blocks = set(x_groups[block_x]) & set(y_groups[block_y]) & set(city_generation.cityblock_group)
                if blocks:
                    block = next(iter(blocks))
                    row.append(block)
        viewport_rows.append(row)

    return viewport_rows

# Initialize viewport based on player's starting position
viewport_rows = update_viewport()

# Process user commands
def process_command(command, chat_history):
    """Process player commands."""
    # Parse the command and arguments
    parts = command.lower().split()
    if not parts:
        return

    cmd = parts[0]
    args = parts[1:]

    # Handle commands
    if cmd == "enter":
        if hasattr(player, 'enter') and callable(player.enter):
            result = player.enter()
            chat_history.append(result)
        else:
            chat_history.append(f"There is no building to enter here.")

    elif cmd == "where":
        if hasattr(player, 'where') and callable(player.where):
            result = player.where()
            chat_history.append(result)
        else:
            chat_history.append(f"I don't know where we are.")

    elif cmd == "leave":
        if hasattr(player, 'leave') and callable(player.leave):
            result = player.leave()
            chat_history.append(result)
        else:
            chat_history.append(f"You are already outside.")

    elif cmd == "search" or cmd == "s":
        if hasattr(player, 'search') and callable(player.search):
            result = player.search()
            chat_history.append(result)
        else:
            chat_history.append(f"There is nothing to search here.")

    elif cmd == "barricade":
        if hasattr(player, 'barricade') and callable(player.barricade):
            result = player.barricade()
            chat_history.append(result)
        else:
            chat_history.append(f"You can't barricade here.")

    elif cmd == "help":
        chat_history.append(
            "Available commands: enter, leave, search, barricade, where, help."
        )

    else:
        chat_history.append(f"Unknown command: {cmd}")


# Main game loop
def main():
    running = True
    global viewport_rows
    chat_history = ["The city is in ruins. Can you make it through the night?",
                    "Use arrow keys to move around.", 
                    "Type 'help' for a list of commands."]
    input_text = ""
    scroll_offset = 0

    while running:
        screen.fill(DARK_GREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    chat_history.append(input_text.strip())
                    process_command(input_text.strip(), chat_history)
                    input_text = ""
                    scroll_offset = max(0, len(chat_history) - ((SCREEN_HEIGHT // 2) - 90) // 20)
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

                # Arrow key movement
                if event.key == pygame.K_UP and player.move(0, -1):
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_DOWN and player.move(0, 1):
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_LEFT and player.move(-1, 0):                    
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_RIGHT and player.move(1, 0):
                    viewport_rows = update_viewport()

                # WASD movement
                if event.key == pygame.K_w and player.move(0, -1):
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_s and player.move(0, 1):
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_a and player.move(-1, 0):                    
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_d and player.move(1, 0):
                    viewport_rows = update_viewport()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    scroll_offset -= 1
                elif event.button == 5: # Scroll down
                    scroll_offset += 1

            for button in button_group:
                action = button.handle_event(event)
                current_block = player.get_block_at_player()
                if action:
                    if action == 'barricade':
                        if hasattr(player, 'barricade') and callable(player.barricade):
                            result = player.barricade()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"You can't barricade here.")
                    elif action == 'search':
                        if hasattr(player, 'search') and callable(player.search):
                            result = player.search()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"There is nothing to search here.")
                    elif action == 'enter':
                        if hasattr(player, 'enter') and callable(player.enter):
                            result = player.enter()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"There is no building to enter here.")
                    elif action == 'leave':
                        if hasattr(player, 'leave') and callable(player.leave):
                            result = player.leave()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"You are already outside.")

        # Draw game elements to screen
        ui.draw_viewport(screen, player, viewport_rows, font_small)
        ui.draw_actions_panel(screen, font_large)
        button_group.update()
        button_group.draw(screen)
        ui.draw_description_panel(screen, player, font_large)
        ui.draw_chat(screen, chat_history, input_text, scroll_offset, font_large)
        ui.draw_status(screen, player, font_large)
        ui.draw_inventory_panel(screen, player, font_large)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
