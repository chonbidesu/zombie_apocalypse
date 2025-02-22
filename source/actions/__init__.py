# actions.py

from settings import *
from combat import Attack, Heal, Inject
from environment import CloseDoors, OpenDoors, AddBarricades, Decade, Ransack, Dump, Search
from movement import Move, Enter, Leave, Stand
from system import Quit, OpenSaveMenu, SaveGame, OpenLoadMenu, LoadGame, OpenNewgameMenu, StartGame, OpenSkillsMenu, Back, Pause, ZoomIn, ZoomOut

   
class ActionCommand:
    """Base class for all actions."""
    def __init__(self, character):
        self.character = character
        self.is_player = character == character.game.state.player
        self.success = False
        self.target = None
        self.message = ""
        self.witness = ""
        self.attacked = ""
        self.sfx = ""  
    
    def execute(self, target=None):
        """Executes the action. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def get_block(self):
        x, y = self.character.location
        city = self.character.game.state.city
        block = city.block(x, y)
        return block            
    
    def get_block_npcs(self):
        x, y = self.character.location
        block_npcs = self.character.state.filter_characters_at_location(x, y, inside=True)    
        return block_npcs        



