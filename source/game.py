# game.py

import pygame
import sys
from pygame.locals import *
from dataclasses import dataclass
import time

import menus
import events
import saveload
import ui
from city import City
from characters import Character
from populate import GenerateNPCs
from blocks import CityBlock, BuildingBlock
from data import Occupation


@dataclass
class GameState:
    player: object
    city: object
    npcs: object


class GameInitializer:
    """Initialize the game, centralizing resources."""
    def __init__(self, screen):
        self.screen = screen
        self.state = None
        self.cursor = ui.Cursor()
        self.menu = menus.GameMenu(self)         
        self.paused = False
        self.save_menu = False
        self.load_menu = False
        self.skills_menu = False
        self.popup_menu = None
        self.ticker = 0
        self.reading_map = False
        self.start_new_game = False
        self.title_event_handler = events.TitleEventHandler(self) 
        self.title_screen = True

    def initialize_game(self):
        """Generate a new game state."""
        self.state = self._create_new_game()
        self._create_resources()

    def _create_new_game(self):
        # Initialize city
        city = City()

        # Create player
        player = Character(
            self, occupation=Occupation.DOCTOR, x=50, y=50, is_human=True
        )

        # Populate the city
        npcs = GenerateNPCs(self, total_humans=500, total_zombies=500)

        print("New game created.")
        return GameState(player, city, npcs)

    def save_game(self, index):
        """Save the game state to a file."""
        saveload.GameData.save_game(index, self)

    def load_game(self, index):
        """Load the game state from a file."""
        game_state = saveload.GameData.load_game(index)
        player, city, npcs = game_state.reconstruct_game(
            self, Character, City, GenerateNPCs, 
            BuildingBlock, CityBlock,
        )
        self.state = GameState(player, city, npcs)

        self._create_resources(set_time=game_state.game_time)

    def _create_resources(self, set_time=None):
        """Create or reinitialize game resources."""
        # Initialize event handlers
        self.event_handler = events.EventHandler(self) 
        self.map_event_handler = events.MapEventHandler(self)
        self.menu_event_handler = events.MenuEventHandler(self) 

        # Initialize chat history
        self.chat_history = [
            "The city is in ruins. Can you make it through the night?", 
            "Use 'w', 'a', 's', 'd' to move. ESC to quit.",
            "Diagonally 'q', 'e', 'z', 'c'."
        ]         

        # Initialize game UI and set clock
        self.game_ui = ui.DrawUI(self, self.screen)  

        if set_time:
            self.game_ui.description_panel.clock.time_in_minutes = set_time

        # Initialize day/night cycle manager
        self.day_cycle = ui.DayCycleManager(self)

        # Opening scene transition
        self.game_ui.screen_transition.start_scene(self.chat_history)   

        if self.load_menu:
            self.load_menu = False          

    def pause_game(self):
        """Toggle game pause state."""
        if not self.paused:
            print("Pausing game")
            self.paused = True
        elif self.paused:
            print("Unpausing game")
            self.paused = False
            self.save_menu = False
            self.load_menu = False

    def quit_game(self):
        """Handle cleanup and save the game on exit."""
        pygame.quit()
        sys.exit()