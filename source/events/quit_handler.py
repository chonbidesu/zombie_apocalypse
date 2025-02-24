# quit_handler.py

from actions import Quit


class QuitHandler:
    """Handles the QUIT event (when the player closes the game)."""

    def __init__(self, game):
        self.game = game

    def handle(self, event):
        """Executes the quit action."""
        Quit(self.game).execute()