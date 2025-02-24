# events.py

import pygame


from actions import *
from .quit_handler import QuitHandler
from .keydown_handler import KeydownHandler
from .mousebutton_down_handler import MouseButtonDownHandler
from .mousebutton_up_handler import MouseButtonUpHandler
from .popup_handler import PopupHandler


class EventHandler:
    def __init__(self, game):
        self.game = game
        self.quit_handler = QuitHandler(game)
        self.keydown_handler = KeydownHandler(game)
        self.mouse_down_handler = MouseButtonDownHandler(game)
        self.mouse_up_handler = MouseButtonUpHandler(game)
        self.popup_handler = PopupHandler(game)

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
                    self.game.close_popup() # Close menu if no option selected
                else:
                    target = self.mouse_up_handler.context_menu.sprite
                    self.popup_handler.handle(event.text, target)
                    self.game.close_popup # Close menu after selection                

                        