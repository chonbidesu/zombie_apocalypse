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
        self.chat_history = [
            "The city is in ruins. Can you make it through the night?", 
            "Use 'w', 'a', 's', 'd' to move. ESC to quit.",
            "Diagonally 'q', 'e', 'z', 'c'."
        ]

        self.action_handler = actions.ActionHandler(self)
        self.initialize_game()

    def initialize_game(self):
        """Initialize the game state by loading or creating a new game."""
        try:
            game_state = saveload.Gamestate.load_game("savegame.pkl")
            self.player, self.city, self.zombies = game_state.reconstruct_game(
                Player, City, Zombie, zombulate.GenerateZombies, 
                blocks.BuildingBlock, blocks.CityBlock, self.chat_history,
            )
            self.game_ui = ui.DrawUI(screen, self.player, self.city, self.zombies)
            self.game_ui.update_zombie_sprites()

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
        self.zombies = zombulate.GenerateZombies(self.player, self.city, self.chat_history, total_zombies=1000)

        # Initialize UI
        self.game_ui = ui.DrawUI(screen, self.player, self.city, self.zombies)
        self.game_ui.update_zombie_sprites()

        print("New game created.")

    def save_game(self):
        """Save the game state to a file."""
        saveload.Gamestate.save_game("savegame.pkl", self.player, self.city, self.zombies)

    def quit_game(self):
        """Handle cleanup and save the game on exit."""
        self.save_game()
        pygame.quit()
        sys.exit()




# Main game loop
def main():
    running = True

    # Initialize game
    game = GameInitializer()

    while running:
        screen.fill(DARK_GREEN)

        events = pygame.event.get()
        game.action_handler.handle_events(events, menus.ContextMenu)

        # Draw game elements to screen
        game.game_ui.draw(game.chat_history)

        if hasattr(game.popup_menu, 'menu'):
            game.popup_menu.menu.handle_events(events)
            game.popup_menu.menu.draw()

        game.cursor.update()
        game.cursor.draw()

        if game.player.is_dead:
            result = game.player.show_death_screen(screen)
            if result == "restart":
                game = GameInitializer()  # Reinitialize the game


        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
