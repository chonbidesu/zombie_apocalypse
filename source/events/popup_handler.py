# popup_handler.py

from actions import Use, Drop


class PopupHandler:
    """Handles key press events, adjusting behavior based on game state."""

    def __init__(self, game):
        self.game = game

    def handle(self, action_type, target=None):
        """Handle popup menu actions."""
        player = self.game.state.player

        menu_to_action = {
            'Equip': Use,
            'Unequip': Use,
            'Use': Use,
            'Install': Use,
            'Reload': Use,
            'Drop': Drop,
        }
        action_class = menu_to_action.get(action_type)
        if action_class:
            action = action_class(player)
            action.execute(target)
            self.game.close_popup()
            if action.message:
                self.handle_feedback(action.message)


    def handle_feedback(self, message):
        """Handle feedback messages from actions."""
        self.game.chat_history.append(message)                