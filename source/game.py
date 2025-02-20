# game.py

import pygame
import sys
from pygame.locals import *
from dataclasses import dataclass

import menus
import events
import saveload
import ui
from city import City
from characters import Character, CharacterName
from populate import GenerateNPCs
from blocks import CityBlock, BuildingBlock
from data import Occupation, ResourcePath


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
        self.cursor = ui.Cursor(self)
        self.menu = menus.GameMenu(self)         
        self.paused = False
        self.newgame_menu = False
        self.save_menu = False
        self.load_menu = False
        self.skills_menu = False
        self.popup_menu = None
        self.ticker = 0
        self.reading_map = False
        self.start_new_game = False
        self.title_event_handler = events.TitleEventHandler(self) 
        self.title_screen = True
        pygame.mixer.init()  # Initialize the mixer
        self.load_sounds()    # Load sound effects

    def load_sounds(self):
        """Load sound effects for actions."""
        self.sounds = {
            #"attack": pygame.mixer.Sound("sfx/attack.wav"),
            #"damage": pygame.mixer.Sound("sfx/damage.wav"),
            "reload": pygame.mixer.Sound(ResourcePath("sfx/reload.mp3").path),
            "gun_shot": pygame.mixer.Sound(ResourcePath("sfx/gun_shot.mp3").path),
            "zombie_sounds": pygame.mixer.Sound(ResourcePath("sfx/zombie_sounds.wav").path),
            "search": pygame.mixer.Sound(ResourcePath("sfx/search.wav").path),
            "footsteps": pygame.mixer.Sound(ResourcePath("sfx/footsteps.wav").path),
            "door_open": pygame.mixer.Sound(ResourcePath("sfx/door_open.wav").path),
            "door_close": pygame.mixer.Sound(ResourcePath("sfx/door_close.wav").path),
            "decade": pygame.mixer.Sound(ResourcePath("sfx/decade.wav").path),
            "barricade": pygame.mixer.Sound(ResourcePath("sfx/barricade.wav").path),
            "human_death": pygame.mixer.Sound(ResourcePath("sfx/human_death.wav").path),
            "zombie_death": pygame.mixer.Sound(ResourcePath("sfx/zombie_death.wav").path),

        }        

    def initialize_game(self, player, portrait):
        """Generate a new game state."""
        self.state = self._create_new_game(player)
        self._create_resources(portrait)

    def initialize_simulation(self):
        """Generate a new simulation to test outcomes."""
        self.state = self._create_new_simulation()
        self._create_resources("sprite_sheets/male1_sprite_sheet.png")

    def _create_new_game(self, player):
        # Initialize city
        city = City()

        # Populate the city
        npcs = GenerateNPCs(self, total_humans=500, total_zombies=500)

        print("New game created.")
        return GameState(player, city, npcs)

    def _create_new_simulation(self):
        # Initialize city
        city = City()

        # Create dummy player
        player_name = CharacterName('Jane', 'Doe', 'Jiggly')
        player = Character(self, player_name, Occupation.CONSUMER, 50, 50, is_human=True)

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

        self._create_resources(game_state.portrait, set_time=game_state.game_time)

    def _create_resources(self, portrait, set_time=None):
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
        self.game_ui = ui.DrawUI(self, self.screen, portrait)
        self.menu.skills_menu.create_resources()

        if set_time:
            self.game_ui.description_panel.clock.time_in_minutes = set_time

        # Opening scene transition
        self.game_ui.day_cycle.start_new_day()
        self.game_ui.screen_transition.start_scene(self.chat_history) 

        if self.load_menu:
            self.load_menu = False          

    def quit_game(self):
        """Handle cleanup and save the game on exit."""
        pygame.quit()
        sys.exit()