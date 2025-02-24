# events.py

import pygame


from actions import *
from .quit_handler import QuitHandler
from .keydown_handler import KeydownHandler
from .mousebutton_down_handler import MouseButtonDownHandler
from .mousebutton_up_handler import MouseButtonUpHandler


class EventHandler:
    def __init__(self, game):
        self.game = game
        self.quit_handler = QuitHandler(game)
        self.keydown_handler = KeydownHandler(game)
        self.mouse_down_handler = MouseButtonDownHandler(game)
        self.mouse_up_handler = MouseButtonUpHandler(game)

    def handle_events(self, events):
        """Handle all game events."""

        for event in events:
            if event.type == pygame.QUIT:
                self.quit_handler.handle(event)
            elif event.type == pygame.KEYDOWN:
                self.keydown_handler.handle(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_down_handler.handle(event)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_up_handler.handle(event)

            elif event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    self.game.popup_menu = None # Close menu if no option selected
                else:
                    target = self.mouse_up_handler.context_menu.sprite
                    self.handle_popup_menu(event.text, target)
                    self.game.popup_menu = None # Close menu after selection                

    def handle_popup_menu(self, action_type, target=None):
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
            if action.message:
                self.handle_feedback(action.message)

    def handle_feedback(self, message):
        """Handle feedback messages from actions."""
        self.game.chat_history.append(message)
                        