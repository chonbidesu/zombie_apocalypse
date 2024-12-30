# main.py
import pygame
import sys
import random
from settings import *
from player import Player
from city_generation import outdoor_type_groups, building_type_groups, cityblock_group, outdoor_group, building_group, neighbourhood_groups, generate_city, generate_neighbourhoods


# Initialize Pygame
pygame.init()

# Create dictionaries to manage the x, y coordinate groups
x_groups = {x: pygame.sprite.Group() for x in range(100)}
y_groups = {y: pygame.sprite.Group() for y in range(100)}

# Initialize city
generate_city(x_groups, y_groups)
generate_neighbourhoods(x_groups, y_groups)
lights_on = pygame.sprite.Group()
generator_installed = pygame.sprite.Group()

# Create screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Apocalypse")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont(None, 16)
font_large = pygame.font.SysFont(None, 24)

# Create player
player = Player(
    human_name="Alice",
    zombie_name="Raven",
    gender="Female",
    age=25,
    occupation="Doctor",
    x=50,
    y=50,
)

# Apply zoomed-in image of street grid to street sprites to randomize street appearance
def apply_zoomed_image(block_image):
    """Apply a zoomed-in portion of the block image."""
    street_group = outdoor_type_groups['Street']
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

# Get all sprites at (x, y)
def get_sprites_at(x, y):
    sprites_x = x_groups[x]
    sprites_y = y_groups[y]
    return set(sprites_x) & set(sprites_y)

# Get filtered sprites at (x, y)
def get_filtered_sprites_at(x, y, group):
    all_sprites = get_sprites_at(x, y)
    filtered_sprites = []
    for sprite in all_sprites:
        if sprite in group:
            filtered_sprites.append(sprite)
    
    return filtered_sprites

# Get the city block at player's current location
def get_block_at_player():
    block = get_filtered_sprites_at(player.location[0], player.location[1], cityblock_group)[0]
    return block

# Get the neighbourhood of a city block
def get_neighbourhood(block):
    for group_name, group in neighbourhood_groups.items():
        if block in group:
            return group_name
    return None

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
                blocks = set(x_groups[block_x]) & set(y_groups[block_y]) & set(cityblock_group)
                if blocks:
                    block = next(iter(blocks))
                    row.append(block)
        viewport_rows.append(row)

    return viewport_rows

#    # Determine the bounds of the viewport
#    x_start, x_end = player.location[0] - 1, player.location[0] + 1
#    y_start, y_end = player.location[1] - 1, player.location[1] + 1

#    for x in range(x_start, x_end + 1):
#        for y in range(y_start, y_end + 1):
#            # Get block at this coordinate
#            block = get_filtered_sprites_at(x, y, cityblock_group)
#            # Add to the appropriate row and column groups
#            viewport_rows[y - y_start].add(block)
#            viewport_columns[x - x_start].add(block)

#    return viewport_rows

# Initialize viewport based on player's starting position
viewport_rows = update_viewport()

# Draw viewport
def draw_viewport():
    """Draw the 3x3 viewport representing the player's surroundings."""
    grid_start_x, grid_start_y = 10, 10
    player_x, player_y = player.location

    for row_index, row in enumerate(viewport_rows):
        for col_index, block in enumerate(row):
            if block is None:
                continue

            # Calculate the block's position relative to the viewport
            block_rect_x = grid_start_x + col_index * BLOCK_SIZE
            block_rect_y = grid_start_y + row_index * BLOCK_SIZE + 20

            screen.blit(block.image, (block_rect_x, block_rect_y))

#            block_x, block_y = get_sprite_coordinates(block)
#            block_rect_x = grid_start_x + ((block_x - player_x) + 1) * BLOCK_SIZE
#            block_rect_y = grid_start_y + ((block_y - player_y) + 1) * BLOCK_SIZE + 20
#            screen.blit(block.image, (block_rect_x, block_rect_y))

            block_text = wrap_text(block.block_name, font_small, BLOCK_SIZE - 10)
            text_height = sum(font_small.size(line)[1] for line in block_text)
            button_rect = pygame.Rect(block_rect_x, block_rect_y, BLOCK_SIZE, text_height + 10)
            pygame.draw.rect(screen, WHITE, button_rect)
            y_offset = button_rect.top + (button_rect.height - text_height)  # Center text vertically

            for line in block_text:
                text = font_small.render(line, True, BLACK)
                text_rect = text.get_rect(center=(button_rect.centerx, y_offset))
                screen.blit(text, text_rect)
                y_offset += font_small.size(line)[1]  # Move down for the next line

    # Draw neighbourhood name
    pygame.draw.rect(screen, GRAY, (grid_start_x, grid_start_y, VIEWPORT_SIZE * BLOCK_SIZE, 20))
    neighbourhood_name = get_neighbourhood(get_block_at_player())
    text = font_small.render(neighbourhood_name, True, WHITE)
    screen.blit(text, (grid_start_x + 10, grid_start_y + 5))

# Draw description panel
def draw_description_panel():
    """Draw the description panel on the right side of the screen."""

    description_start_x = SCREEN_WIDTH // 3 + 10
    description_width = SCREEN_WIDTH - description_start_x - 10
    description_height = SCREEN_HEIGHT - 170

    pygame.draw.rect(screen, WHITE, (description_start_x, 10, description_width, description_height))

    # Get the description text and wrap it to fit within the panel
    paragraphs = []
    current_observations = player.description(get_block_at_player(), building_group, lights_on, generator_installed)
    for observation in current_observations:
        wrapped_text = wrap_text(observation, font_large, description_width - 20)  # 10px padding on each side
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
        text_rect = text.get_rect(x=description_start_x + 10, y=y_offset)  # Padding of 10px on the left
        screen.blit(text, text_rect)
        y_offset += font_large.size(line)[1]  # Move down for the next line

def draw_chat(chat_history, input_text, scroll_offset):
    """Draw the chat window with scrolling support and text wrapping."""
    chat_start_x, chat_start_y = 10, SCREEN_HEIGHT // 2 + 30
    chat_width, chat_height = SCREEN_WIDTH // 3 - 10, SCREEN_HEIGHT // 2 - 70

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

def draw_status():
    """Draw the player status panel."""
    status_start_x, status_start_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT - 150
    status_width, status_height = SCREEN_WIDTH * 2 // 3 - 20, 140

    pygame.draw.rect(screen, BLACK, (status_start_x, status_start_y, status_width, status_height))
    pygame.draw.rect(screen, WHITE, (status_start_x, status_start_y, status_width, status_height), 2)

    y_offset = status_start_y + 10
    status_text = [
        f"Player Name: {player.human_name}",
        f"HP: {player.hp}/{player.max_hp}",
        f"Actions taken: {player.ticker}",
        f"Location: {player.location}",
    ]

    for line in status_text:
        text = font_large.render(line, True, WHITE)
        screen.blit(text, (status_start_x + 10, y_offset))
        y_offset += 20


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
            result = player.enter(get_block_at_player(), building_group, lights_on, generator_installed)
            chat_history.append(result)
        else:
            chat_history.append(f"There is no building to enter here.")

    elif cmd == "where":
        if hasattr(player, 'where') and callable(player.where):
            result = player.where(get_block_at_player())
            chat_history.append(result)
        else:
            chat_history.append(f"I don't know where we are.")

    elif cmd == "leave":
        if hasattr(player, 'leave') and callable(player.leave):
            result = player.leave(get_block_at_player(), building_group, lights_on, generator_installed)
            chat_history.append(result)
        else:
            chat_history.append(f"You are already outside.")

    elif cmd == "search":
        if hasattr(player, 'search') and callable(player.search):
            result = player.search(get_block_at_player(), building_group, lights_on)
            chat_history.append(result)
        else:
            chat_history.append(f"There is nothing to search here.")

    elif cmd == "barricade":
        if hasattr(player, 'barricade') and callable(player.barricade):
            result = player.barricade(get_block_at_player(), building_group, lights_on)
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

                if event.key == pygame.K_UP and player.move(0, -1, building_group, lights_on):
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_DOWN and player.move(0, 1, building_group, lights_on):
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_LEFT and player.move(-1, 0, building_group, lights_on):                    
                    viewport_rows = update_viewport()
                elif event.key == pygame.K_RIGHT and player.move(1, 0, building_group, lights_on):
                    viewport_rows = update_viewport()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    scroll_offset -= 1
                elif event.button == 5: # Scroll down
                    scroll_offset += 1


        draw_viewport()
        draw_description_panel()
        draw_chat(chat_history, input_text, scroll_offset)
        draw_status()


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
