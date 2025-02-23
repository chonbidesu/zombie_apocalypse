# events.py

import pygame
from dataclasses import dataclass

from data import ItemType
from menus import ContextMenu
from actions import *


@dataclass
class MoveTarget:
    dx: int = 0
    dy: int = 0


class EventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""
        player = self.game.state.player

        for event in events:
            if event.type == pygame.QUIT:
                Quit(player).execute()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event)

            elif event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    self.game.popup_menu = None # Close menu if no option selected
                else:
                    target = self.context_menu.sprite
                    self.handle_popup_menu(event.text, target)
                    self.game.popup_menu = None # Close menu after selection

    def handle_keydown(self, event):
        """Handle key press events."""
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

        # Check if the pressed key is mapped to movement
        if event.key in key_to_movement:
            player = self.game.state.player
            dx, dy = key_to_movement[event.key]     # Get movement offset
            target = MoveTarget(dx, dy)             # Create a movement target
            move_command = Move(player)             # Create move command
            move_command.execute(target)            # Execute the movement
        if event.key == pygame.K_ESCAPE:
            command = Pause(self.game)
            command.execute()

    def handle_mousebuttondown(self, event):
        """Handle mouse button down events."""
        player = self.game.state.player
        action = None

        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            target = ClickTarget(self.game, mouse_pos)
            if (player.is_human and target.type == 'zombie') or (not player.is_human and target.type == 'human'):
                if player.equipped and player.equipped.type == ItemType.DNA_EXTRACTOR:
                    action = ExtractDNA(player)
                elif player.equipped and player.equipped.type == ItemType.SYRINGE:
                    action = Inject(player)
                else:
                    action = Attack(player)
                action.execute(target.sprite.npc)

            elif target.type == 'block' and not self.game.popup_menu:
                action = Move(player)
                action.execute(target.sprite)  
            
            elif player.is_human and target.type == 'human':
                if player.equipped:
                    if player.equipped.type == ItemType.FIRST_AID_KIT:
                        action = Heal(player)
                        action.execute(target.sprite.npc)

                else:
                    #action = Speak(player)
                    #action.execute(target.sprite.npc)  
                    pass     
            
            elif player.is_human and target.type == 'self':
                if player.equipped:
                    if player.equipped.type == ItemType.FIRST_AID_KIT:
                        action = Heal(player)
                        action.execute(player)

            else:
                skills_button = self.game.game_ui.status_panel.button_group.sprite
                skills_button.handle_event(event)

            if action and action.message:
                self.handle_feedback(action.message)

        # Handle graphical changes for button clicks
        for button in self.game.game_ui.actions_panel.button_group:
            button.handle_event(event)

    def handle_mousebuttonup(self, event):
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
                status_panel_x, status_panel_y = self.game.game_ui.status_panel.x, self.game.game_ui.status_panel.y
                button_abs_rect = skills_button.rect.move(status_panel_x, status_panel_y)
                if button_abs_rect.collidepoint(event.pos):
                    print("Opening skills menu")
                    action = OpenSkillsMenu(player)
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
                    if action.message:
                        self.handle_feedback(action.message)                    

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

class ClickTarget:
    """Get the target of a mouse click."""
    def __init__(self, game, mouse_pos):
        self.type = None
        self.sprite = None
        self.human_sprite_group = game.game_ui.description_panel.human_sprite_group
        self.zombie_sprite_group = game.game_ui.description_panel.zombie_sprite_group
        self.viewport_group = game.game_ui.viewport.viewport_group
        self.inventory_group = game.game_ui.inventory_panel.inventory_group
        self.player_portrait = game.game_ui.status_panel.player_sprite
        
        self.get(mouse_pos)

    def get(self, mouse_pos):
        """Get the target of a mouse click, saving the sprite and returning the target type."""
        for sprite in self.viewport_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'block'
        for sprite in self.inventory_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite  
                self.type = 'item'
        for sprite in self.zombie_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'zombie'
        for sprite in self.human_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'human'
        if self.player_portrait.rect.collidepoint(mouse_pos):
            self.sprite = self.player_portrait
            self.type = 'self'
        if self.type == None:
            self.type = 'screen'

class MapEventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""
        player = self.game.state.player

        for event in events:
            if event.type == pygame.QUIT:
                Quit(player).execute()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

    def handle_keydown(self, event):
        """Handle key press events."""
        player = self.game.state.player

        key_to_action = {
            pygame.K_PAGEDOWN: ZoomOut,
            pygame.K_PAGEUP: ZoomIn,
            pygame.K_ESCAPE: Back,
        }
        action = key_to_action.get(event.key)
        if action:
            action(player).execute()             


class MenuEventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""
        player = self.game.state.player

        for event in events:
            if event.type == pygame.QUIT:
                Quit(player).execute()

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event)                

    def handle_keydown(self, event):
        """Handle key press events."""

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


    def handle_mousebuttondown(self, event):
        """Handle mouse button down events."""
        if self.game.paused:

            if self.game.newgame_menu:
                # New Game Menu    
                newgame_menu = self.game.menu.newgame_menu
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
                for button in self.game.menu.pause_menu.button_group:
                    button.handle_event(event)

        else:
            for button in self.game.menu.skills_menu.back_button:
                button.handle_event(event)

            for slot in self.game.menu.skills_menu.skill_slots:
                slot.handle_event(event, self.game.menu.skills_menu)

    def handle_mousebuttonup(self, event):
        """Handle mouse button up events."""

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
         

class TitleEventHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events):
        """Handle all game events."""

        for event in events:
            if event.type == pygame.QUIT:
                self.game.quit_game()

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