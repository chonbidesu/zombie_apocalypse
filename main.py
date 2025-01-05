# main.py
import pygame
import sys
import random
from pygame.locals import *
from collections import defaultdict


from settings import *
from player import Player
from city import City
import ui
import logic
import utils
import menus
import zombie

# Initialize Pygame
pygame.init()

# Create screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Apocalypse")
clock = pygame.time.Clock()

# Initialize coordinates
x_groups, y_groups = logic.create_xy_groups()

# Initialize city
city = City(x_groups, y_groups)

# Create buttons
button_group = ui.create_button_group()

# Create zombie groups
zombie_group, zombie_display_group = logic.create_zombie_groups()

zombie1 = zombie.Zombie(x_groups, y_groups, zombie_group, 51, 51)
zombie2 = zombie.Zombie(x_groups, y_groups, zombie_group, 51, 51)

# Create player
player = Player(
    city, x_groups, y_groups, zombie_group,
    button_group, ui.update_observations, utils.get_block_at_player,
    name="Alice", occupation="Doctor", x=50, y=50, 
)

# Initialize viewport based on player's starting position
logic.update_viewport(player, zombie_group, zombie_display_group)

# Initialize cursor
cursor = menus.Cursor()

menu_viewport_dxy = None
menu_item = None
popup_menu = None

# Main game loop
def main():
    running = True
    global popup_menu
    chat_history = ["The city is in ruins. Can you make it through the night?", 
                    "Use 'w', 'a', 's', 'd' to move. ESC to quit."
                    ]
    scroll_offset = 0

    while running:
        screen.fill(DARK_GREEN)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                # Arrow key movement
                if event.key == pygame.K_UP and player.move(0, -1):
                    logic.update_viewport(player, zombie_group, zombie_display_group)
                elif event.key == pygame.K_DOWN and player.move(0, 1):
                    logic.update_viewport(player, zombie_group, zombie_display_group)
                elif event.key == pygame.K_LEFT and player.move(-1, 0):                    
                    logic.update_viewport(player, zombie_group, zombie_display_group)
                elif event.key == pygame.K_RIGHT and player.move(1, 0):
                    logic.update_viewport(player, zombie_group, zombie_display_group)

                # WASD movement
                if event.key == pygame.K_w and player.move(0, -1):
                    logic.update_viewport(player, zombie_group, zombie_display_group)
                elif event.key == pygame.K_s and player.move(0, 1):
                    logic.update_viewport(player, zombie_group, zombie_display_group)
                elif event.key == pygame.K_a and player.move(-1, 0):                    
                    logic.update_viewport(player, zombie_group, zombie_display_group)
                elif event.key == pygame.K_d and player.move(1, 0):
                    logic.update_viewport(player, zombie_group, zombie_display_group)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    scroll_offset -= 1
                elif event.button == 5: # Scroll down
                    scroll_offset += 1
                #if popup_menu:
                #    popup_menu.hide()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                target, sprite = utils.get_click_target(mouse_pos, player, logic.viewport_group)
                popup_menu = menus.create_context_menu(target, player, utils.get_sprite_coordinates, menus.NonBlockingPopupMenu, sprite)
                if popup_menu:
                    popup_menu.show()

            elif event.type == MOUSEMOTION:
                cursor.rect.center = event.pos

            for button in button_group:
                action = button.handle_event(event)
                if action:
                    if action == 'barricade':
                        if hasattr(player, 'barricade') and callable(player.barricade):
                            result = player.barricade()
                            chat_history.append(result)
                            logic.update_viewport(player, zombie_group, zombie_display_group)
                        else:
                            chat_history.append(f"You can't barricade here.")
                    elif action == 'search':
                        if hasattr(player, 'search') and callable(player.search):
                            result = player.search()
                            chat_history.append(result)
                            logic.update_viewport(player, zombie_group, zombie_display_group)
                        else:
                            chat_history.append(f"There is nothing to search here.")
                    elif action == 'enter':
                        if hasattr(player, 'enter') and callable(player.enter):
                            result = player.enter()
                            chat_history.append(result)
                            logic.update_viewport(player, zombie_group, zombie_display_group)
                        else:
                            chat_history.append(f"There is no building to enter here.")
                    elif action == 'leave':
                        if hasattr(player, 'leave') and callable(player.leave):
                            result = player.leave()
                            chat_history.append(result)
                            logic.update_viewport(player, zombie_group, zombie_display_group)
                        else:
                            chat_history.append(f"You are already outside.")

        # Draw game elements to screen
        ui.draw_viewport(screen, player, logic.viewport_group)
        ui.draw_actions_panel(screen)
        button_group.update()
        button_group.draw(screen)
        ui.draw_description_panel(screen, player, zombie_display_group)
        ui.draw_chat(screen, chat_history, scroll_offset)
        ui.draw_status(screen, player)
        ui.draw_inventory_panel(screen, player)
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
                    menus.handle_menu_action(
                        player, logic.update_viewport, 
                        zombie_group, zombie_display_group, 
                        event.name, event.text, chat_history
                    )
                    popup_menu = None

        cursor.update()
        cursor.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
