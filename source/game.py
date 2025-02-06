# game.py

import pickle
import pygame
import sys
from pygame.locals import *

import menus
import events
import saveload
import ui
from city import City
from characters import Character
from populate import GenerateNPCs
from blocks import CityBlock, BuildingBlock
from data import Occupation

class GameInitializer:
    """Initialize the game, centralizing resources."""
    def __init__(self, screen, new_game=False):
        self.player = None
        self.city = None
        self.cursor = ui.Cursor()
        self.paused = False
        self.menu = menus.GameMenu()
        self.save_menu = False
        self.load_menu = False
        self.popup_menu = None
        self.ticker = 0
        self.reading_map = False
        self.start_new_game = False
        self.chat_history = [
            "The city is in ruins. Can you make it through the night?", 
            "Use 'w', 'a', 's', 'd' to move. ESC to quit.",
            "Diagonally 'q', 'e', 'z', 'c'."
        ]

        self.initialize_game(screen, new_game)
        self.game_ui = ui.DrawUI(self, screen)

    def initialize_game(self, screen, new_game):
        """Initialize the game state by loading or creating a new game."""
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

        print("New game created.")

    def save_game(self, index):
        """Save the game state to a file."""
        saveload.Gamestate.save_game(index, self)

    def load_game(self, index):
        """Load the game state from a file."""
        game_state = saveload.Gamestate.load_game(index)
        self.player, self.city, self.npcs, = game_state.reconstruct_game(
            self, Character, City, GenerateNPCs, 
            BuildingBlock, CityBlock,
        )

    def pause_game(self):
        """Toggle game pause state."""
        if not self.paused:
            self.paused = True
        elif self.paused:
            self.save_menu = False
            self.load_menu = False
            self.paused = False

    def quit_game(self):
        """Handle cleanup and save the game on exit."""
        pygame.quit()
        sys.exit()