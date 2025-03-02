# keydown_handler.py

import pygame

from actions import Pause, Move, MoveTarget, ZoomOut, ZoomIn, Back


class KeydownHandler:
    """Handles key press events, adjusting behavior based on game state."""

    def __init__(self, game):
        self.game = game

    def handle(self, event):
        """Processes keyboard inputs based on the current game state."""
        if self.game.title_screen:
            self.handle_title(event)
        elif self.game.paused or self.game.skills_menu:
            self.handle_menu(event)
        elif self.game.reading_map:
            self.handle_map(event)
        else:
            self.handle_game(event)

    def handle_title(self, event):
        """Handles key presses on the title screen."""
        if self.game.newgame_menu:
            newgame_menu = self.game.menu.newgame_menu  
            for _, text_input in newgame_menu.text_inputs.items():
                if text_input.active:
                    if event.key == pygame.K_RETURN:
                        text_input.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        text_input.text = text_input.text[:-1]
                    elif event.key == pygame.K_TAB:
                        newgame_menu.cycle_text_input() 
                        return
                    elif event.unicode.isprintable() and len(text_input.text) < text_input.max_length:
                        text_input.text += event.unicode

    def handle_menu(self, event):
        """Handles key presses when the game is paused."""
        if self.game.skills_menu:
            key_to_action = {
                pygame.K_ESCAPE: Back,
            }
            action = key_to_action.get(event.key)
            if action:
                action(self.game).execute()  

        elif self.game.newgame_menu:
            newgame_menu = self.game.menu.newgame_menu  
            for _, text_input in newgame_menu.text_inputs.items():
                if text_input.active:
                    if event.key == pygame.K_RETURN:
                        text_input.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        text_input.text = text_input.text[:-1]
                    elif event.key == pygame.K_TAB:
                        newgame_menu.cycle_text_input()
                    elif event.unicode.isprintable() and len(text_input.text) < text_input.max_length:
                        text_input.text += event.unicode

        else:
            key_to_action = {
                pygame.K_ESCAPE: Pause,
            }
            action = key_to_action.get(event.key)
            if action:
                action(self.game).execute()  

    def handle_map(self, event):
        """Handle key press events."""
        key_to_action = {
            pygame.K_PAGEDOWN: ZoomOut,
            pygame.K_PAGEUP: ZoomIn,
            pygame.K_ESCAPE: Back,
        }
        action = key_to_action.get(event.key)
        if action:
            action(self.game).execute()         

    def handle_game(self, event):
        """Handles key presses during gameplay."""
        key_to_movement = {
            pygame.K_w: (0, -1),  # Move up
            pygame.K_s: (0, 1),   # Move down
            pygame.K_a: (-1, 0),  # Move left
            pygame.K_d: (1, 0),   # Move right
            pygame.K_q: (-1, -1), # Move up-left
            pygame.K_e: (1, -1),  # Move up-right
            pygame.K_z: (-1, 1),  # Move down-left
            pygame.K_c: (1, 1),   # Move down-right
        }

        if event.key in key_to_movement:
            player = self.game.state.player
            dx, dy = key_to_movement[event.key]
            Move(player).execute(MoveTarget(dx, dy))

        if event.key == pygame.K_ESCAPE:
            Pause(self.game).execute()            