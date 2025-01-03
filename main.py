# main.py
import pygame
import sys
import random
from pygame.locals import *


from settings import *
from player import Player
import city_generation
import ui
import zombie

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
font_large = pygame.font.SysFont(None, 26)
font_chat = pygame.font.SysFont(None, 21)

# Create player
player = Player(
    x_groups, y_groups, city_generation.cityblock_group, city_generation.building_group, 
    city_generation.building_type_groups, city_generation.outdoor_type_groups, city_generation.neighbourhood_groups,
    button_group, enter_button, leave_button, name="Alice", occupation="Doctor", x=50, y=50, 
)

# Create zombies
zombie_group = pygame.sprite.Group()
zombie_display_group = pygame.sprite.Group()

zombie = zombie.Zombie(x_groups, y_groups, zombie_group, 51, 51)

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

def get_viewport_dxy(sprite):
    center_x, center_y = player.location
    block_x, block_y = get_sprite_coordinates(sprite)

    dx = block_x - center_x
    dy = block_y - center_y

    return dx, dy

# Check whether the current block is a building
def is_building():
    current_block = player.get_block_at_player()
    if current_block in city_generation.building_group:
        return True

def calculate_grid_start():
    grid_start_x = (SCREEN_HEIGHT // 5)
    grid_start_y = (SCREEN_HEIGHT // 5)
    return grid_start_x, grid_start_y

# Update viewport centered on player
viewport_group = pygame.sprite.Group()
def update_viewport():
    global viewport_rows
    viewport_rows = []
    viewport_group.empty()
    player_x, player_y = player.location

    grid_start_x, grid_start_y = calculate_grid_start()

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
                    block.rect = pygame.Rect(
                        grid_start_x + col_offset * BLOCK_SIZE,
                        grid_start_y + row_offset * BLOCK_SIZE,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )
                    row.append(block)
                    viewport_group.add(block)
        viewport_rows.append(row)

            # Update zombies in the viewport
    for zombie in zombie_group:
        zombie_x, zombie_y = zombie.get_coordinates()

        # Check if the zombie is within the 3x3 viewport
        if player_x - 1 <= zombie_x <= player_x + 1 and player_y - 1 <= zombie_y <= player_y + 1:
            # Update zombie rect to align with its block's position
            col_offset = zombie_x - player_x
            row_offset = zombie_y - player_y
            zombie.rect = pygame.Rect(
                grid_start_x + col_offset * BLOCK_SIZE + BLOCK_SIZE // 4,  # Center the mini-square
                grid_start_y + row_offset * BLOCK_SIZE + BLOCK_SIZE // 4,
                BLOCK_SIZE // 2,
                BLOCK_SIZE // 2
            )
            viewport_group.add(zombie)

    return viewport_rows

# Initialize viewport based on player's starting position
viewport_rows = update_viewport()

# Get the target of the mouse click
def get_click_target(mouse_pos):
    current_block = player.get_block_at_player()
    if current_block.rect.collidepoint(mouse_pos):
        return 'current block', current_block
    for sprite in player.inventory:
        if sprite.rect.collidepoint(mouse_pos):
            return 'item', sprite
    for sprite in viewport_group:
        if sprite.rect.collidepoint(mouse_pos):
            return 'block', sprite
    return 'screen', None

menu_viewport_dxy = None
menu_item = None

# Create a context-sensitive popup menu based on the target
def create_context_menu(target, sprite=None):
    global popup_menu, menu_viewport_dxy, menu_item
    if target == 'item':
        if sprite is not None:
            if sprite in player.weapon_group:
                menu_data = ['Item', 'Equip', 'Drop']
            else:
                menu_data = ['Item', 'Use', 'Drop']
        if sprite is not None:
            menu_item = sprite
    elif target == 'current block' and is_building():
        if not player.inside:
            menu_data = ['Actions', 'Barricade', 'Search', 'Enter']
        elif target == 'current block' and player.inside:
            menu_data = ['Actions', 'Barricade', 'Search', 'Leave']
    elif target == 'current block' and not is_building():
        menu_data = ['Actions', 'Search']
    elif target == 'block':
        menu_data = ['Go', 'Move']
        if sprite is not None:
            menu_viewport_dxy = (get_viewport_dxy(sprite))
    elif target == 'screen':
        return None

    popup_menu = ui.NonBlockingPopupMenu(menu_data)

# Handle menu actions
def handle_menu_action(menu_name, action, chat_history):
    if menu_name == 'Item':
        if action == 'Equip':
            player.weapon.empty()
            player.weapon.add(menu_item)
        elif action == 'Use':
            print(f"Using item!")
        elif action == 'Drop':
            menu_item.kill()
    elif menu_name == 'Actions':
        if action == 'Barricade':
            result = player.barricade()
            chat_history.append(result)
        elif action == 'Search':
            result = player.search()
            chat_history.append(result)
        elif action == 'Enter':
            player.inside = True
            button_group.remove(enter_button)
            button_group.add(leave_button)
        elif action == 'Leave':
            player.inside = False
            button_group.remove(leave_button)
            button_group.add(enter_button)
    elif menu_name == 'Go':
        if action == 'Move':
            player.move(menu_viewport_dxy[0], menu_viewport_dxy[1])
            print(f"Moving to {menu_viewport_dxy}")
            viewport_rows = update_viewport()
          

## Sprite cursor also runs while menu is posted.
class Cursor(object):
    def __init__(self):
        self.image = pygame.image.load('assets/zombie_hand.png').convert_alpha()
        self.rect = self.image.get_rect(center=(0,0))
        pygame.mouse.set_visible(False)
    
    def update(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.topleft = (mouse_x, mouse_y)

    def draw(self):
        pygame.display.get_surface().blit(self.image, self.rect)
cursor = Cursor()

popup_menu = None
# Main game loop
def main():
    running = True
    global popup_menu
    chat_history = ["The city is in ruins. Can you make it through the night?", 
                    "Use 'w', 'a', 's', 'd' to move. ESC to quit."
                    ]
    input_text = ""
    scroll_offset = 0

    while running:
        screen.fill(DARK_GREEN)

        character_sprite = zombie.update_character_sprite(player, (100, 100))
        if character_sprite:
            if character_sprite not in zombie_display_group:
                zombie_display_group.add(character_sprite)
        else:
            zombie_display_group.remove(character_sprite)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

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
                #if popup_menu:
                #    popup_menu.hide()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                target, sprite = get_click_target(mouse_pos)
                create_context_menu(target, sprite)
                print(target)
                if popup_menu:
                    popup_menu.show()

            elif event.type == MOUSEMOTION:
                cursor.rect.center = event.pos

            #elif event.type == USEREVENT and event.code == 'MENU':
            #    if event.name is None:
            #        print('Hide menu')
            #        popup_menu.hide()
            #    elif event.name == 'Item':
            #        if event.text == 'Equip':
            #            print(f"Equipping item: {sprite.name}")
            #        elif event.text == 'Use':
            #            print(f"Using item: {sprite.name}")
            #        elif event.text == 'Drop':
            #            print(f"Dropping item: {sprite.name}")
            #    elif event.name == 'Actions':
            #        if event.text == 'Barricade':
            #            print(f"Barricading {sprite.name}")
            #        elif event.text == 'Search':
            #            print(f"Searching {sprite.name}")
            #        elif event.text == 'Enter':
            #            print(f"Entering {sprite.name}")
            #        elif event.text == 'Leave':
            #            print(f"Leaving {sprite.name}")
            #    elif event.name == 'Inside Actions':
            #        if event.text == 'Barricade':
            #            print(f"Barricading {sprite.name}")
            #        elif event.text == 'Search':
            #            print(f"Searching {sprite.name}")
            #        elif event.text == 'Leave':
            #            print(f"Leaving {sprite.name}")
            #    elif event.name == 'Go':
            #        if event.text == 'Move':
            #            print(f"Moving to {sprite.name}")
            #    popup_menu.hide()

            for button in button_group:
                action = button.handle_event(event)
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
        ui.draw_viewport(screen, player, viewport_group, font_small)
        ui.draw_actions_panel(screen, font_large)
        button_group.update()
        button_group.draw(screen)
        ui.draw_description_panel(screen, player, font_large)
        ui.draw_chat(screen, chat_history, input_text, scroll_offset, font_chat)
        ui.draw_status(screen, player, font_large)
        ui.draw_inventory_panel(screen, player, font_large)
        player.inventory.update()
        player.inventory.draw(screen)

        if popup_menu:
            popup_menu.handle_events(events)
            popup_menu.draw()

        for event in events:
            if event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    popup_menu = None
                else:
                    handle_menu_action(event.name, event.text, chat_history)
                    popup_menu = None

        cursor.update()
        cursor.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
