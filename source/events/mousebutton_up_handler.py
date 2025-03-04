# mousebutton_up_handler.py

import pygame

from actions import (StartGame, Pause, Back, OpenNewgameMenu, OpenLoadMenu, OpenSkillsMenu, SaveGame, OpenSaveMenu, LoadGame, OpenLoadMenu, Quit,
                    CloseDoors, OpenDoors, AddBarricades, Search, Enter, Leave, Dump, Ransack, Decade, Stand
)
from menus import ContextMenu
from events.click_target import ClickTarget


class MouseButtonUpHandler:
    """Handles mouse button releases based on game state."""

    def __init__(self, game):
        self.game = game

    def handle(self, event):
        """Processes mouse releases based on game state."""
        if self.game.title_screen:
            self.handle_title(event)
        elif self.game.paused or self.game.skills_menu:
            self.handle_menu(event)
        else:
            self.handle_game(event)

    def handle_title(self, event):
        """Handles mouse releases on the title screen."""
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

    def handle_menu(self, event):
        if self.game.paused:

            # Handle saving and loading from the pause menu
            if self.game.save_menu:
                for slot in self.game.menu.save_menu.slots:
                    if slot.rect.collidepoint(event.pos):
                        SaveGame(self.game).execute(slot.index)
                        slot.update_image()

                back_button = self.game.menu.save_menu.back_button
                if back_button.sprite.rect.collidepoint(event.pos):
                    Back(self.game).execute()
                        
            elif self.game.load_menu:
                for slot in self.game.menu.load_menu.slots:
                    if slot.rect.collidepoint(event.pos) and slot.player_name not in ["<<empty>>", "<<incompatible save>>", "<<corrupted save>>"]:
                        Pause(self.game).execute()
                        LoadGame(self.game).execute(slot.index)

                back_button = self.game.menu.load_menu.back_button
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

            # Handle general UI buttons
            else:
                for button in self.game.menu.pause_menu.button_group:
                    action_name = button.handle_event(event)
                    if action_name:
                        button_to_action = {
                            'menu_newgame': OpenNewgameMenu,
                            'menu_save': OpenSaveMenu,
                            'menu_load': OpenLoadMenu,
                            'menu_play': Pause,
                            'menu_exit': Quit,
                        }
                        action = button_to_action.get(action_name)
                        if action:
                            action(self.game).execute()

        else:
            # Handle the skills menu
            if self.game.skills_menu:
                skills_menu = self.game.menu.skills_menu
                back_button = self.game.menu.skills_menu.back_button

                if back_button.sprite.rect.collidepoint(event.pos):
                    Back(self.game).execute()

                if skills_menu.selected_skill and hasattr(skills_menu, 'gain_button_rect'):
                    if skills_menu.gain_button_rect.collidepoint(event.pos):
                        skills_menu._gain_skill()                       

    def handle_game(self, event):
        """Handle mouse button up events."""
        player = self.game.state.player

        if event.button == 3:  # Right-click for popup menu
            mouse_pos = pygame.mouse.get_pos()
            target = ClickTarget(self.game, mouse_pos)
            self.context_menu = ContextMenu(target, self.game.state.player)
            if self.context_menu:
                self.game.popup_menu = self.context_menu.menu
                if self.game.popup_menu:
                    self.game.popup_menu.show()

        elif event.button == 1:
            if self.game.popup_menu:
                menu_rect = self.game.popup_menu.menus[-1].rect
                if not menu_rect.collidepoint(event.pos):
                    self.game.popup_menu.hide()
                    self.game.popup_menu = None

            # Handle the skills menu
            else:
                skills_button = self.game.game_ui.status_panel.button_group.sprite
                if skills_button.rect.collidepoint(event.pos):
                    action = OpenSkillsMenu(self.game)
                    action.execute()                    

        # Handle actions for button clicks
        for button in self.game.game_ui.actions_panel.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'close_doors': CloseDoors,
                    'open_doors': OpenDoors,
                    'barricade': AddBarricades,
                    'search': Search,
                    'enter': Enter,
                    'leave': Leave,
                    'dump': Dump,
                    'ransack': Ransack,
                    'break_cades': Decade,
                    'stand': Stand,
                }
                action_class = button_to_action.get(action_name)
                if action_class:
                    action = action_class(player)
                    action.execute()
                    if action.sfx:
                        action.play_sound()
                    if action.message:
                        self.handle_feedback(action.message)      


    def handle_feedback(self, message):
        """Handle feedback messages from actions."""
        self.game.chat_history.append(message)                           
