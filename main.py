# main.py
import os
import pickle
import pygame
import sys
from pygame.locals import *
from collections import defaultdict

from settings import *
from player import Player
from city import City
from npc import NPC
import ui
import populate
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
    """Initialize the game, centralizing resources."""
    def __init__(self):
        self.player = None
        self.city = None
        self.cursor = ui.Cursor()
        self.paused = False
        self.pause_menu = menus.PauseMenu()
        self.popup_menu = None
        self.reading_map = False
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
            self.player, self.city, self.zombies, self.humans = game_state.reconstruct_game(
                self, Player, City, NPC, populate.GenerateNPCs, 
                blocks.BuildingBlock, blocks.CityBlock,
            )
            self.game_ui = ui.DrawUI(self, screen)
            self.game_ui.update_npc_sprites()

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
            self.city, name="Jane", occupation="Doctor", x=50, y=50,
        )

        # Populate the city
        self.zombies = populate.GenerateNPCs(self, total_npcs=1000, is_human=False)
        self.humans = populate.GenerateNPCs(self, total_npcs=1000, is_human=True)

        # Initialize UI
        self.game_ui = ui.DrawUI(self, screen)
        self.game_ui.update_npc_sprites()

        print("New game created.")

    def save_game(self):
        """Save the game state to a file."""
        saveload.Gamestate.save_game("savegame.pkl", self)

    def pause_game(self):
        """Toggle game pause state."""
        if not self.paused:
            self.paused = True
        elif self.paused:
            self.paused = False

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

        # Handle events
        events = pygame.event.get()
        game.action_handler.handle_events(events, menus.ContextMenu)

        # Handle pause menu
        if game.paused:
            game.pause_menu.draw_pause_menu(screen)

        # Handle opening the map
        elif game.reading_map:
            game.game_ui.map.draw()

        else:
            # Draw game elements to screen
            game.game_ui.draw(game.chat_history)

            # Handle right-click menu
            if game.popup_menu:
                game.popup_menu.handle_events(events)
                game.popup_menu.draw()

        # Draw the cursor
        game.cursor.update(game.game_ui)
        game.cursor.draw()

        # Handle player death
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
