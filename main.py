# main.py
import os
import pickle
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
import saveload
import items
import blocks

# Initialize Pygame
pygame.init()

# Create screen and clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Zombie Apocalypse")
clock = pygame.time.Clock()

class GameInitializer:
    def __init__(self):
        self.player = None
        self.city = None
        self.cursor = menus.Cursor()
        self.button_group = None
        self.popup_menu = None

        self.initialize_game()

    def initialize_game(self):
        """Initialize the game state by loading or creating a new game."""
        try:
            game_state = saveload.Gamestate.load_game("savegame.pkl")
            self.button_group = ui.create_button_group()
            self.zombie_display_group = pygame.sprite.Group()
            self.player, self.city, self.zombie_group = game_state.reconstruct_game(
                Player, City, zombie.Zombie, items.Item, blocks.BuildingBlock, blocks.CityBlock, 
                logic.create_xy_groups, ui.update_observations, utils.get_block_at_player, utils.get_block_at_xy,
            )
            logic.update_viewport(self.player)

        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print("Save file not found or corrupted. Creating a new game.")
            # Generate a new game if save file doesn't exist
            self._create_new_game()

    def _create_new_game(self):
        """Generate a new game state."""

        # Initialize city
        self.city = City()

        # Create buttons
        self.button_group = ui.create_button_group()

        # Create zombie display group
        self.zombie_display_group = pygame.sprite.Group()

        # Create player
        self.player = Player(
            self.city, self.button_group, ui.update_observations, utils.get_block_at_player,
            name="Alice", occupation="Doctor", x=50, y=50,
        )

        # TEST ZOMBIES
        zombie1 = zombie.Zombie(self.player, utils.get_block_at_xy, self.zombie_display_group, 51, 51)
        zombie2 = zombie.Zombie(self.player, utils.get_block_at_xy, self.zombie_display_group, 51, 51)

        # Initialize viewport based on player's starting position
        logic.update_viewport(self.player)

        print("New game created.")

    def save_game(self):
        """Save the game state to a file."""
        saveload.Gamestate.save_game("savegame.pkl", self.player)

    def quit_game(self):
        """Handle cleanup and save the game on exit."""
        self.save_game()
        pygame.quit()
        sys.exit()


# Initialize game
game = GameInitializer()

# Main game loop
def main():
    running = True
    chat_history = ["The city is in ruins. Can you make it through the night?", 
                    "Use 'w', 'a', 's', 'd' to move. ESC to quit."
                    ]
    scroll_offset = 0

    while running:
        screen.fill(DARK_GREEN)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                game.quit_game()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    game.quit_game()

                # Arrow key movement
                if event.key == pygame.K_UP and game.player.move(0, -1):
                    logic.update_viewport(game.player)
                elif event.key == pygame.K_DOWN and game.player.move(0, 1):
                    logic.update_viewport(game.player)
                elif event.key == pygame.K_LEFT and game.player.move(-1, 0):                    
                    logic.update_viewport(game.player)
                elif event.key == pygame.K_RIGHT and game.player.move(1, 0):
                    logic.update_viewport(game.player)

                # WASD movement
                if event.key == pygame.K_w and game.player.move(0, -1):
                    logic.update_viewport(game.player)
                elif event.key == pygame.K_s and game.player.move(0, 1):
                    logic.update_viewport(game.player)
                elif event.key == pygame.K_a and game.player.move(-1, 0):                    
                    logic.update_viewport(game.player)
                elif event.key == pygame.K_d and game.player.move(1, 0):
                    logic.update_viewport(game.player)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    scroll_offset -= 1
                elif event.button == 5: # Scroll down
                    scroll_offset += 1
                #if popup_menu:
                #    popup_menu.hide()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                target, sprite = utils.get_click_target(mouse_pos, game.player, logic.viewport_group)
                game.popup_menu = menus.create_context_menu(target, game.player, utils.get_sprite_coordinates, menus.NonBlockingPopupMenu, sprite)
                if game.popup_menu:
                    game.popup_menu.show()

            elif event.type == MOUSEMOTION:
                game.cursor.rect.center = event.pos

            for button in game.player.button_group:
                action = button.handle_event(event)
                if action:
                    if action == 'barricade':
                        if hasattr(game.player, 'barricade') and callable(game.player.barricade):
                            result = game.player.barricade()
                            chat_history.append(result)
                            logic.update_viewport(game.player)
                        else:
                            chat_history.append(f"You can't barricade here.")
                    elif action == 'search':
                        if hasattr(game.player, 'search') and callable(game.player.search):
                            result = game.player.search()
                            chat_history.append(result)
                            logic.update_viewport(game.player)
                        else:
                            chat_history.append(f"There is nothing to search here.")
                    elif action == 'enter':
                        if hasattr(game.player, 'enter') and callable(game.player.enter):
                            result = game.player.enter()
                            chat_history.append(result)
                            logic.update_viewport(game.player)
                        else:
                            chat_history.append(f"There is no building to enter here.")
                    elif action == 'leave':
                        if hasattr(game.player, 'leave') and callable(game.player.leave):
                            result = game.player.leave()
                            chat_history.append(result)
                            logic.update_viewport(game.player)
                        else:
                            chat_history.append(f"You are already outside.")

        # Draw game elements to screen
        logic.update_zombie_sprites(game.player, game.zombie_display_group)
        ui.draw_viewport(screen, game.player, logic.viewport_group)
        ui.draw_actions_panel(screen)
        game.player.button_group.update()
        game.player.button_group.draw(screen)
        ui.draw_description_panel(screen, game.player, game.zombie_display_group)
        ui.draw_chat(screen, chat_history, scroll_offset)
        ui.draw_status(screen, game.player)
        ui.draw_inventory_panel(screen, game.player)
        game.player.inventory.update()
        game.player.inventory.draw(screen)

        if game.popup_menu:
            game.popup_menu.handle_events(events)
            game.popup_menu.draw()

        for event in events:
            if event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    game.popup_menu = None
                else:
                    menus.handle_menu_action(
                        game.player, logic.update_viewport, 
                        game.zombie_display_group, 
                        event.name, event.text, chat_history
                    )
                    game.popup_menu = None

        game.cursor.update()
        game.cursor.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
