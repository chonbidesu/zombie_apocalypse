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
from zombie import Zombie
import ui
import zombulate
import menus
import saveload
import items
import blocks
import actions

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
        self.menu_target = None
        self.menu_dxy = None
        self.action_handler = actions.ActionHandler(self)

        self.initialize_game()

    def initialize_game(self):
        """Initialize the game state by loading or creating a new game."""
        try:
            game_state = saveload.Gamestate.load_game("savegame.pkl")
            self.player, self.city, self.zombies = game_state.reconstruct_game(
                Player, City, Zombie, zombulate.GenerateZombies, 
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
        self.zombies = zombulate.GenerateZombies(self.player, self.city, total_zombies=1000)

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
        game.action_handler.handle_events(events, chat_history, scroll_offset, menus.create_context_menu)

        # Draw game elements to screen
        game.game_ui.draw(chat_history, scroll_offset)

        if game.popup_menu:
            game.popup_menu.handle_events(events)
            game.popup_menu.draw()

        game.cursor.update()
        game.cursor.draw()

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
