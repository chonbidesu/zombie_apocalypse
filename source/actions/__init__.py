# actions.py

from settings import *


class ActionExecutor:
    """Handles executing actions for both player and AI characters."""

    def __init__(self, game, character):
        self.game = game
        self.character = character  # Define the acting character
        self.is_player = character == game.state.player
        self.action_progress = game.game_ui.action_progress

    def execute(self, action, target=None):
        """Execute an ActionCommand instance."""

        if isinstance(action, ActionCommand):
            return action.execute(self, target)

        print(f"Unknown action: {action}  Target: {target}")

    
class ActionCommand:
    """Base class for all actions."""
    def __init__(self):
        self.action = None
        self.success = False
        self.target = None
        self.message = ""
        self.witness = ""
        self.attacked = ""
        self.sfx = ""  
    
    def execute(self, executor, target=None):
        """Executes the action. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement execute()")



