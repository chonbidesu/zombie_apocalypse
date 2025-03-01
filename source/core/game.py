# game.py

import pygame
import sys
from pygame.locals import *
from dataclasses import dataclass
from collections import deque

import menus
from events import EventHandler
import core.saveload as saveload
from core.settings import *
import ui
from world import City, GenerateNPCs, CityBlock, BuildingBlock
from characters import Character, CharacterName
from data import Occupation, ResourcePath
from actions import Stand


@dataclass
class GameState:
    player: object
    city: object
    npcs: object


class GameInitializer:
    """Initialize the game, centralizing resources."""
    def __init__(self, screen, clock, debug=False):
        self.screen = screen
        self.clock = clock
        self.debug = debug
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
        self.action_timer = 0
        self.action_queue = deque()
        self.reading_map = False
        self.start_new_game = False
        self.event_handler = EventHandler(self) 
        self.title_screen = True
        self.parallax = ui.ParallaxBackground(self.menu.title_menu._get_parallax_paths(), self.menu.title_menu._get_parallax_speeds())
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

        if self.debug:
            print("Creating debug NPCs...")
            npcs = GenerateNPCs(self, total_humans=100, total_zombies=100)
        else:
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
        npcs = GenerateNPCs(self, total_humans=10, total_zombies=100)

        print("New game created.")
        return GameState(player, city, npcs)
    
    def start_game(self):
        """Start the game with the chosen settings."""
        first_name = self.menu.newgame_menu.text_inputs["first_name"].text
        last_name = self.menu.newgame_menu.text_inputs["last_name"].text
        dead_word = self.menu.newgame_menu.text_inputs["dead_word"].text
        portrait_index = self.menu.newgame_menu.selected_portrait
        occupation = self.menu.newgame_menu.selected_occupation

        # Validate user input
        if not first_name or not last_name or not dead_word:
            self.menu.newgame_menu.display_warning("Please enter a first and last name, and an adjective that describes your corpse.")
            return  
        if occupation is None:
            self.menu.newgame_menu.display_warning("Please select an occupation.")
            return
        if portrait_index is None:
            self.menu.newgame_menu.display_warning("Please select a player portrait.")
            return
        
        portrait = list(self.menu.newgame_menu.portrait_sprites)[portrait_index]
        character_name = CharacterName(first_name, last_name, dead_word)
        is_human = False if occupation == Occupation.CORPSE else True

        player = Character(self, character_name, occupation, 50, 50, is_human)
        
        # Disable menus and initialize game
        self.title_screen = False
        self.newgame_menu = False
        self.initialize_game(player, portrait.portrait_path)    

    def start_debug_game(self):
        print("Starting debug game...")

        # Define player
        player_name = CharacterName("Debug", "Player", "Test")
        player = Character(self, player_name, Occupation.FIREFIGHTER, 12, 12, is_human=True)
        portrait = list(self.menu.newgame_menu.portrait_sprites)[0]

        self.initialize_game(player, portrait.portrait_path)

    def tick(self, ap_cost=1):
        self.ticker += ap_cost
        print(f"Ticker: {self.ticker}")
                    
        # Check buildings for fuel expiry
        for row in self.state.city.grid:
            for block in row:
                if hasattr(block, 'fuel_expiration') and block.fuel_expiration < self.ticker:
                    if block.lights_on:
                        block.lights_on = False

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

    def handle_events(self, events):
        """Handles all event processing, including menus and gameplay."""
        self.event_handler.handle_events(events)

        if self.popup_menu:
            self.popup_menu.handle_events(events)

    def update_game_state(self):
        """Handles updating NPCs, processing actions, and checking player status."""
        
        if self.debug and not self.state:
            self.title_screen = False
            self.start_debug_game()

        if self.state:
            # Process NPC actions
            self.process_npcs()

            # Handle player death
            if self.state.player.is_dead:
                self.game_ui.death_screen.handle_events(pygame.event.get())
                self.game_ui.death_screen.draw()
                if self.game_ui.death_screen.stand:
                    Stand(self.state.player).execute()

    def process_npcs(self):
        """Processes NPC actions in batches to optimize performance."""
        # Set up AI action queue
        actions_per_frame = 100

        self.action_timer += self.clock.get_time()
        if self.action_timer >= ACTION_INTERVAL:
            self.action_queue = deque(self.state.npcs.list) # Load all NPCs into the queue
            self.action_timer = 0       

        # Process the action queue in batches
        for _ in range(min(actions_per_frame, len(self.action_queue))):
            npc = self.action_queue.popleft() # Get next npc
            if npc.ap > 0:
                npc.goal_manager.evaluate_goal()          
                npc.goal_manager.current_goal.execute() if bool(npc.goal_manager.current_goal) else False
            
    def update_screen(self):
        """Handles drawing game elements and updating UI."""
        
        if self.title_screen:
            self.parallax.update()
            self.parallax.draw(self.screen)
            if self.newgame_menu:
                self.menu.newgame_menu.draw(self.screen)
            elif self.load_menu:
                self.menu.load_menu.draw(self.screen)
            elif self.start_new_game:
                self.initialize_game()
                self.start_new_game = False
                self.title_screen = False
            else:
                self.menu.title_menu.draw(self.screen)

        elif self.paused:
            if self.save_menu:
                self.menu.save_menu.draw(self.screen)
            elif self.load_menu:
                self.menu.load_menu.draw(self.screen)
            elif self.newgame_menu:
                self.menu.newgame_menu.draw(self.screen)
            elif self.start_new_game:
                self.initialize_game()
                self.start_new_game = False
                self.pause_game()
            else:
                self.menu.pause_menu.draw(self.screen)

        elif self.skills_menu:
            self.menu.skills_menu.draw(self.screen)

        elif self.reading_map:
            self.game_ui.map.draw()

        else:
            # Draw game elements
            self.game_ui.update()
            self.game_ui.draw(self.chat_history)

            # Draw right-click menu if active
            if self.popup_menu:
                self.popup_menu.draw()

            # Update cursor
            self.cursor.update()

    def open_skills_menu(self):
        self.skills_menu = True

    def open_save_menu(self):
        self.save_menu = True

    def open_load_menu(self):
        self.load_menu = True

    def open_newgame_menu(self):
        self.newgame_menu = True

    def pause(self):
        if self.paused:
            self.paused = False            
        else:
            self.paused = True
        self.save_menu = False
        self.load_menu = False  

    def back(self):
        self.newgame_menu = False
        self.save_menu = False
        self.load_menu = False
        self.skills_menu = False
        self.reading_map = False

    def zoom_in(self):
        self.game_ui.map.zoom_in = True

    def zoom_out(self):
        self.game_ui.map.zoom_in = False

    def close_popup(self):
        self.popup_menu = None

    def quit_game(self):
        """Handle cleanup and save the game on exit."""
        pygame.quit()
        sys.exit()