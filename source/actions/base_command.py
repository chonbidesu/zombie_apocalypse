# base_command.py

import pygame

class ActionCommand:
    """Base class for all actions."""
    def __init__(self, character):
        self.character = character
        self.is_player = self._is_player()
        self.success = False
        self.target = None
        self.message = ""
        self.witness = ""
        self.attacked = ""
        self.sfx = ""  
    
    def execute(self, target=None):
        """Executes the action. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement execute()")
    
    def play_sound(self):
        game = self.character.game
        pygame.mixer.Sound.play(game.sounds[self.sfx])        

    def _is_player(self):
        if self.character:
            return self.character == self.character.game.state.player
        else:
            return False

    def get_block(self):
        x, y = self.character.location
        city = self.character.game.state.city
        block = city.block(x, y)
        return block            
    
    def get_block_npcs(self):
        x, y = self.character.location
        block_npcs = self.character.helper.filter_characters_at_location(x, y, inside=True)    
        return block_npcs      