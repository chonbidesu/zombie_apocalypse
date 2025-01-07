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
import zombulate
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
        self.popup_menu = None

        self.initialize_game()

    def initialize_game(self):
        """Initialize the game state by loading or creating a new game."""
        try:
            game_state = saveload.Gamestate.load_game("savegame.pkl")
            self.player, self.city, self.zombies = game_state.reconstruct_game(
                Player, City, zombie.Zombie, zombulate.GenerateZombies, 
                blocks.BuildingBlock, blocks.CityBlock,
            )
            self.game_ui = ui.DrawUI(screen, self.player, self.city, self.zombies)

        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print("Save file not found or corrupted. Creating a new game.")
            # Generate a new game if save file doesn't exist
            self._create_new_game()

    def _create_new_game(self):
        """Generate a new game state."""

        # Initialize city
        self.city = City()

        # Create player
        self.player = Player(
            self.city, name="Alice", occupation="Doctor", x=50, y=50,
        )

        # Zombulate the city
        self.zombies = zombulate.GenerateZombies(self.player, self.city)

        # Initialize UI
        self.game_ui = ui.DrawUI(screen, self.player, self.city, self.zombies)

        print("New game created.")

    def save_game(self):
        """Save the game state to a file."""
        saveload.Gamestate.save_game("savegame.pkl", self.player, self.city, self.zombies)

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
                if event.key == pygame.K_UP:
                    game.player.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    game.player.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    game.player.move(-1, 0)                    
                elif event.key == pygame.K_RIGHT:
                    game.player.move(1, 0)

                # WASD movement
                if event.key == pygame.K_w:
                    game.player.move(0, -1)
                elif event.key == pygame.K_s:
                    game.player.move(0, 1)
                elif event.key == pygame.K_a:
                    game.player.move(-1, 0)                    
                elif event.key == pygame.K_d:
                    game.player.move(1, 0)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Scroll up
                    scroll_offset -= 1
                elif event.button == 5: # Scroll down
                    scroll_offset += 1
                #if popup_menu:
                #    popup_menu.hide()

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                mouse_pos = pygame.mouse.get_pos()
                target, sprite = utils.get_click_target(mouse_pos, game.player, game.game_ui.viewport_group)
                game.popup_menu = menus.create_context_menu(target, game.player, menus.NonBlockingPopupMenu, sprite)
                if game.popup_menu:
                    game.popup_menu.show()

            elif event.type == MOUSEMOTION:
                game.cursor.rect.center = event.pos

            for button in game.game_ui.button_group:
                action = button.handle_event(event)
                if action:
                    if action == 'barricade':
                        if hasattr(game.player, 'barricade') and callable(game.player.barricade):
                            result = game.player.barricade()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"You can't barricade here.")
                    elif action == 'search':
                        if hasattr(game.player, 'search') and callable(game.player.search):
                            result = game.player.search()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"There is nothing to search here.")
                    elif action == 'enter':
                        if hasattr(game.player, 'enter') and callable(game.player.enter):
                            result = game.player.enter()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"There is no building to enter here.")
                    elif action == 'leave':
                        if hasattr(game.player, 'leave') and callable(game.player.leave):
                            result = game.player.leave()
                            chat_history.append(result)
                        else:
                            chat_history.append(f"You are already outside.")

        # Draw game elements to screen
        game.game_ui.draw(chat_history, scroll_offset)

        if game.popup_menu:
            game.popup_menu.handle_events(events)
            game.popup_menu.draw()

        game.cursor.update()
        game.cursor.draw()

        for event in events:
            if event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    game.popup_menu = None
                else:
                    menus.handle_menu_action(
                        game.player, event.name, event.text, chat_history
                    )
                    game.game_ui.update_viewport()
                    game.popup_menu = None


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
