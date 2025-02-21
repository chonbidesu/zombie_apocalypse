# actions.py

from settings import *

class ActionExecutor:
    """Handles executing actions for both player and AI characters."""

    def __init__(self, game, actor):
        self.game = game
        self.actor = actor  # Define the acting character

    def execute(self, action, target=None):
        """Execute an ActionCommand instance."""

        if isinstance(action, ActionCommand):
            return action.execute(self.actor, self, target)

        print(f"Unknown action: {action}  Target: {target}")

    
class ActionCommand:
    """Base class for all actions."""
    
    def execute(self, character, executor, target=None):
        """Executes the action. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement execute()")



