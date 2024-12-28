# main.py
import pygame
import sys
import random
from settings import *
from player import Player
import city_generation


# Initialize Pygame
pygame.init()

# Initialize city
city = city_generation.generate_city()

# Initialize zoom coordinates for street block rect images
city_generation.initialize_zoom_coordinates(city)

# Load images for block types
BLOCK_IMAGES = {
    "FireStation": pygame.image.load("assets/fire_station.gif"),
    "PoliceDepartment": pygame.image.load("assets/police_department.gif"),
    "Street": pygame.image.load("assets/streets.gif"),
    "Park": pygame.image.load("assets/park.gif"),
    "Carpark": pygame.image.load("assets/carpark.gif"),
    "Cemetery": pygame.image.load("assets/cemetery.gif"),
    "Monument": pygame.image.load("assets/monument.gif"),
    "Hospital": pygame.image.load("assets/hospital.gif"),
    "Mall": pygame.image.load("assets/mall.gif"),
    "Church": pygame.image.load("assets/church.gif"),
    "Warehouse": pygame.image.load("assets/warehouse.gif"),
    "Factory": pygame.image.load("assets/factory.gif"),
    "School": pygame.image.load("assets/school.gif"),
    "NecroTechLab": pygame.image.load("assets/necrotech_lab.gif"),
    "Junkyard": pygame.image.load("assets/junkyard.gif"),
    "Museum": pygame.image.load("assets/museum.gif"),
    "Nightclub": pygame.image.load("assets/nightclub.gif"),
    "Pub": pygame.image.load("assets/pub.gif"),
    "Library": pygame.image.load("assets/library.gif"),
    "AutoRepair": pygame.image.load("assets/auto_repair.gif"),
}

# Create screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Apocalypse")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont(None, 16)
font_large = pygame.font.SysFont(None, 24)

# Create player
player = Player(
    city,
    human_name="Alice",
    zombie_name="Raven",
    gender="Female",
    age=25,
    occupation="Doctor",
    x=50,
    y=50,
)

# Draw zoomed-in image to randomize street appearance
def draw_zoomed_image(screen, block_image, rect_x, rect_y, zoom_x, zoom_y):
    """Draw a zoomed-in portion of the block image."""
    image_width, image_height = block_image.get_width(), block_image.get_height()

    # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
    zoom_factor = 2
    zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

    # Extract the zoomed-in portion
    zoomed_surface = block_image.subsurface((zoom_x, zoom_y, zoom_width, zoom_height))

    # Scale it to the target block size and blit it
    zoomed_surface = pygame.transform.scale(zoomed_surface, (BLOCK_SIZE, BLOCK_SIZE))
    screen.blit(zoomed_surface, (rect_x, rect_y))

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

# Draw grid
def draw_grid(city, player):
    """Draw the 3x3 grid representing the player's surroundings."""
    grid_start_x, grid_start_y = 10, 10
    x, y = player.location
    start_x, start_y = max(0, x - 1), max(0, y - 1)

    neighbourhood_name = "Unknown"
    for key, name in NEIGHBOURHOODS.items():
        nx, ny = (key - 1) % 10, (key - 1) // 10
        if nx * 10 <= x < (nx + 1) * 10 and ny * 10 <= y < (ny + 1) * 10:
            neighbourhood_name = name
            break

    # Draw neighbourhood name
    pygame.draw.rect(screen, GRAY, (grid_start_x, grid_start_y, GRID_SIZE * BLOCK_SIZE, 20))
    text = font_small.render(neighbourhood_name, True, WHITE)
    screen.blit(text, (grid_start_x + 10, grid_start_y + 5))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            grid_x = start_x + col
            grid_y = start_y + row

            if 0 <= grid_x < 100 and 0 <= grid_y < 100:
                rect_x = grid_start_x + col * BLOCK_SIZE 
                rect_y = grid_start_y + row * BLOCK_SIZE + 20

                block = city[grid_y][grid_x]
                block_image = BLOCK_IMAGES.get(block.block_type, None)

                if block_image:
                    if block.block_type == "Street":
                        draw_zoomed_image(screen, block_image, rect_x, rect_y, block.zoom_x, block.zoom_y)
                    else:
                        screen.blit(pygame.transform.scale(block_image, (BLOCK_SIZE, BLOCK_SIZE)), (rect_x, rect_y))

                # Wrap the block name text to fit inside the button
                wrapped_text = wrap_text(block.block_name, font_small, BLOCK_SIZE - 10)

                # Calculate the total height of the wrapped text
                total_height = sum(font_small.size(line)[1] for line in wrapped_text)

                # Once height of text is known, set button height.
                # Draw centered text on light-colored button
                button_rect = pygame.Rect(
                    rect_x, rect_y,
                    BLOCK_SIZE, total_height + 10
                )
                pygame.draw.rect(screen, WHITE, button_rect)

                y_offset = button_rect.top + (button_rect.height - total_height)  # Center text vertically

                for line in wrapped_text:
                    text = font_small.render(line, True, BLACK)
                    text_rect = text.get_rect(center=(button_rect.centerx, y_offset))
                    screen.blit(text, text_rect)
                    y_offset += font_small.size(line)[1] # Move down for the next line

# Draw description panel
def draw_description_panel(city, player):
    """Draw the description panel on the right side of the screen."""
    x, y = player.location
    block = city[y][x]

    description_start_x = SCREEN_WIDTH // 3 + 10
    description_width = SCREEN_WIDTH - description_start_x - 10
    description_height = SCREEN_HEIGHT - 170

    pygame.draw.rect(screen, WHITE, (description_start_x, 10, description_width, description_height))

    # Get the description text and wrap it to fit within the panel
    paragraphs = []
    current_observations = player.description()
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

def draw_status(player):
    """Draw the player status panel."""
    status_start_x, status_start_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT - 150
    status_width, status_height = SCREEN_WIDTH * 2 // 3 - 20, 140

    pygame.draw.rect(screen, BLACK, (status_start_x, status_start_y, status_width, status_height))
    pygame.draw.rect(screen, WHITE, (status_start_x, status_start_y, status_width, status_height), 2)

    y_offset = status_start_y + 10
    status_text = [
        f"Human Name: {player.human_name}",
        f"Zombie Name: {player.zombie_name}",
        f"HP: {player.hp}/{player.max_hp}",
        f"AP: {player.action_points}/{player.max_action_points}",
        f"Location: {player.location}",
        f"State: {'Human' if player.is_human else 'Zombie'}"
    ]

    for line in status_text:
        text = font_large.render(line, True, WHITE)
        screen.blit(text, (status_start_x + 10, y_offset))
        y_offset += 20


def process_command(command, player, city, chat_history):
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

    elif cmd == "search":
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
                    process_command(input_text.strip(), player, city, chat_history)
                    input_text = ""
                    scroll_offset = max(0, len(chat_history) - ((SCREEN_HEIGHT // 2) - 90) // 20)
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

                if event.key == pygame.K_UP:
                    player.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    scroll_offset -= 1
                elif event.button == 5: # Scroll down
                    scroll_offset += 1


        draw_grid(city, player)
        draw_description_panel(city, player)
        draw_chat(chat_history, input_text, scroll_offset)
        draw_status(player)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
