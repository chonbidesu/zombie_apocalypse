# events.py

import pygame

from settings import *
from data import Action, BLOCKS, ITEMS, ItemType, ItemFunction


class EventHandler:
    def __init__(self, game):
        self.game = game
        self.state = self.game.player.state
        self.actions = self.game.player.actions

    def handle_events(self, events, ContextMenu):
        """Handle all game events."""
        for event in events:
            if event.type == pygame.QUIT:
                self.act(Action.QUIT)

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event, ContextMenu)

            elif event.type == pygame.MOUSEMOTION:
                self.handle_mousemotion(event)

            elif event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    self.game.popup_menu = None # Close menu if no option selected
                else:
                    self.handle_popup_menu(event.text)
                    self.game.popup_menu = None # Close menu after selection

    def handle_keydown(self, event):
        """Handle key press events."""
        if self.game.reading_map:
            key_to_action = {
                pygame.K_ESCAPE: Action.CLOSE_MAP,
                pygame.K_PAGEDOWN: Action.ZOOM_OUT,
                pygame.K_PAGEUP: Action.ZOOM_IN,
            }
        else:
            key_to_action = {
                pygame.K_w: Action.MOVE_UP,
                pygame.K_s: Action.MOVE_DOWN,
                pygame.K_a: Action.MOVE_LEFT,
                pygame.K_d: Action.MOVE_RIGHT,
                pygame.K_q: Action.MOVE_UPLEFT,
                pygame.K_e: Action.MOVE_UPRIGHT,
                pygame.K_z: Action.MOVE_DOWNLEFT,
                pygame.K_c: Action.MOVE_DOWNRIGHT,
                pygame.K_ESCAPE: Action.PAUSE,
            }
        action = key_to_action.get(event.key)
        if action:
            self.act(action)

    def handle_mousebuttondown(self, event):
        """Handle mouse button down events."""
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            target = ClickTarget(self.game, mouse_pos)
            if target.type == 'npc':
                action = Action.ATTACK
                self.act(action, target)
            elif target.type == 'block' and not self.game.popup_menu:
                action = Action.MOVE
                self.act(action, target)             

        # Handle graphical changes for button clicks
        for button in self.game.game_ui.actions_panel.button_group:
            button.handle_event(event)

        for button in self.game.pause_menu.button_group:
            button.handle_event(event)

    def handle_mousebuttonup(self, event, ContextMenu):
        """Handle mouse button up events."""
        if event.button == 3:  # Right-click for popup menu
            mouse_pos = pygame.mouse.get_pos()
            target = ClickTarget(self.game, mouse_pos)
            self.context_menu = ContextMenu(target, self.game.player)
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

        # Handle actions for button clicks
        for button in self.game.game_ui.actions_panel.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'barricade': Action.BARRICADE,
                    'search': Action.SEARCH,
                    'enter': Action.ENTER,
                    'leave': Action.LEAVE,
                }
                action = button_to_action.get(action_name)
                if action:
                    self.act(action)

        for button in self.game.pause_menu.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'play': Action.PAUSE,
                    'options': Action.OPTIONS,
                    'exit': Action.QUIT,
                }
                action = button_to_action.get(action_name)
                if action:
                    self.act(action)

    def handle_mousemotion(self, event):
        """Update cursor position on mouse motion."""
        self.game.cursor.rect.center = event.pos

    def handle_popup_menu(self, action):
        """Handle popup menu actions."""
        menu_to_action = {
            'Equip': Action.EQUIP,
            'Unequip': Action.UNEQUIP,
            'Use': Action.USE,
            'Install': Action.USE,
            'Reload': Action.USE,
            'Drop': Action.DROP,
            'Barricade': Action.BARRICADE,
            'Search': Action.SEARCH,
            'Enter': Action.ENTER,
            'Leave': Action.LEAVE,
        }
        action_type = menu_to_action.get(action)
        if action_type:
            self.act(action_type)


    def act(self, action, target=None):
        """Evoke the Action Executor to handle actions."""
        player = self.game.player
        player.action.execute(action, target)
      

class ClickTarget:
    """Get the target of a mouse click."""
    def __init__(self, game, mouse_pos):
        self.type = None
        self.sprite = None
        self.player = game.player
        self.human_sprite_group = game.game_ui.description_panel.human_sprite_group
        self.zombie_sprite_group = game.game_ui.description_panel.zombie_sprite_group
        self.viewport_group = game.game_ui.viewport.viewport_group
        
        self.get(mouse_pos)

    def get(self, mouse_pos):
        """Get the target of a mouse click, saving the sprite and returning the target type."""
        for sprite in self.viewport_group:
            if sprite.dx == 0 and sprite.dy == 0 and sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite
                self.type = 'center block'
            elif sprite.rect.collidepoint(mouse_pos):
                self.sprite = sprite                
                self.type = 'block'
        for sprite in self.player.inventory:
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
        self.type = 'screen'
