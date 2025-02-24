# events.py

import pygame

from data import ItemType
from menus import ContextMenu
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
                    target = self.context_menu.sprite
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



class MapEventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""
        player = self.game.state.player

        for event in events:
            if event.type == pygame.QUIT:
                Quit(self.game).execute()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
           

class MenuEventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""
        player = self.game.state.player

        for event in events:
            if event.type == pygame.QUIT:
                Quit(self.game).execute()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event)                

         

class TitleEventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""

        for event in events:
            if event.type == pygame.QUIT:
                Quit(self.game).execute()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event)     

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def handle_keydown(self, event):
        """Handle key down events."""
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

    def handle_mousebuttondown(self, event):
        """Handle mouse button down events."""
        title_menu = self.game.menu.title_menu
        newgame_menu = self.game.menu.newgame_menu

        if self.game.newgame_menu:
            for button in newgame_menu.buttons:
                button.handle_event(event)

            # Handle portrait selection
            for i, sprite in enumerate(newgame_menu.portrait_sprites):
                if sprite.rect.collidepoint(event.pos):
                    newgame_menu.selected_portrait = i if not sprite.selected else None
                
            # Handle occupation selection
            for slot in newgame_menu.occupation_slots:
                if slot.rect.collidepoint(event.pos):
                    newgame_menu.selected_occupation = slot.occupation if not slot.selected else None
                    newgame_menu.occupation_slots.update(newgame_menu.selected_occupation)

            for text_input in newgame_menu.text_inputs.values():
                text_input.active = text_input.rect.collidepoint(event.pos)  

        else:
            for button in title_menu.buttons:
                button.handle_event(event)         

    def handle_mousebuttonup(self, event):
        """Handle mouse button up events."""

        # Handle saving and loading from the pause menu                  
        if self.game.load_menu:
            load_menu = self.game.menu.load_menu
            for slot in load_menu.slots:
                if slot.rect.collidepoint(event.pos) and slot.player_name not in ["<<empty>>", "<<incompatible save>>", "<<corrupted save>>"]:
                    self.game.load_game(slot.index)
                    self.game.title_screen = False

            back_button = load_menu.back_button
            if back_button.sprite.rect.collidepoint(event.pos):
                Back(self.game).execute()            

        elif self.game.newgame_menu:
            newgame_menu = self.game.menu.newgame_menu
            for button in newgame_menu.buttons:
                action = button.handle_event(event)
                if action == "menu_start":
                    StartGame(self.game).execute()
                elif action == "menu_back":
                    Back(self.game).execute()

        # Handle actions for button clicks
        else:
            title_menu = self.game.menu.title_menu
            for button in title_menu.buttons:
                action_name = button.handle_event(event)
                if action_name:
                    button_to_action = {
                        'menu_newgame': OpenNewgameMenu,
                        'menu_load': OpenLoadMenu,
                        'menu_exit': Quit,
                    }
                    action = button_to_action.get(action_name)
                    if action:
                        action(self.game).execute()                               