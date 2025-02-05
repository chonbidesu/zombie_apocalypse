# game.py

import pickle
import pygame
import sys
from pygame.locals import *

import menus
import events as events
import saveload
import ui
from city import City
from characters import Character
from populate import GenerateNPCs
from blocks import CityBlock, BuildingBlock
from data import Occupation

class GameInitializer:
    """Initialize the game, centralizing resources."""
    def __init__(self, screen):
        self.player = None
        self.city = None
        self.cursor = ui.Cursor()
        self.paused = False
        self.menu = menus.GameMenu()
        self.popup_menu = None
        self.ticker = 0
        self.reading_map = False
        self.chat_history = [
            "The city is in ruins. Can you make it through the night?", 
            "Use 'w', 'a', 's', 'd' to move. ESC to quit.",
            "Diagonally 'q', 'e', 'z', 'c'."
        ]

        self.initialize_game(screen)

    def initialize_game(self, screen):
        """Initialize the game state by loading or creating a new game."""
        try:
            game_state = saveload.Gamestate.load_game("savegame.pkl")
            self.player, self.city, self.npcs, = game_state.reconstruct_game(
                self, Character, City, GenerateNPCs, 
                BuildingBlock, CityBlock,
            )
            self.game_ui = ui.DrawUI(self, screen)

        except (FileNotFoundError, EOFError, pickle.UnpicklingError):
            print("Save file not found or corrupted. Creating a new game.")
            # Generate a new game if save file doesn't exist
            self._create_new_game(screen)

        self.event_handler = events.EventHandler(self) 
        self.map_event_handler = events.MapEventHandler(self)
        self.menu_event_handler = events.MenuEventHandler(self)      

    def _create_new_game(self, screen):
        """Generate a new game state."""

        # Initialize city
        self.city = City()

        # Create player
        self.player = Character(
            self, occupation=Occupation.DOCTOR, x=50, y=50, is_human=True
        )

        # Populate the city
        self.npcs = GenerateNPCs(self, total_humans=500, total_zombies=500)

        # Initialize UI
        self.game_ui = ui.DrawUI(self, screen)
        self.game_ui.update()

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