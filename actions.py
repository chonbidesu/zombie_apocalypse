import pygame
from enum import Enum, auto

from settings import *

class ActionType(Enum):
    # Movement actions
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UPLEFT = auto()
    MOVE_UPRIGHT = auto()
    MOVE_DOWNLEFT = auto()
    MOVE_DOWNRIGHT = auto()

    # Button actions
    BARRICADE = auto()
    SEARCH = auto()
    ENTER = auto()
    LEAVE = auto()

    # Popup menu actions
    EQUIP = auto()
    UNEQUIP = auto()
    USE = auto()
    DROP = auto()
    MOVE_TO = auto()
    ATTACK = auto()

    # System actions
    QUIT = auto()
    RESTART = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()


class ActionHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events, create_context_menu):
        """Handle all game events."""
        for event in events:
            if event.type == pygame.QUIT:
                self.execute_action(ActionType.QUIT)

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event, create_context_menu)

            elif event.type == pygame.MOUSEMOTION:
                self.game.cursor.rect.center = event.pos

            elif event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    self.game.popup_menu = None
                else:
                    self.handle_popup_menu(event.text)

                    #self.game.game_ui.update_viewport()
                    self.game.popup_menu = None                

    def handle_keydown(self, event):
        """Handle key press events."""
        key_to_action = {
            pygame.K_w: ActionType.MOVE_UP,
            pygame.K_s: ActionType.MOVE_DOWN,
            pygame.K_a: ActionType.MOVE_LEFT,
            pygame.K_d: ActionType.MOVE_RIGHT,
            pygame.K_q: ActionType.MOVE_UPLEFT,
            pygame.K_e: ActionType.MOVE_UPRIGHT,
            pygame.K_z: ActionType.MOVE_DOWNLEFT,
            pygame.K_c: ActionType.MOVE_DOWNRIGHT,
            pygame.K_ESCAPE: ActionType.QUIT,
        }
        action = key_to_action.get(event.key)
        if action:
            self.execute_action(action)

    def handle_mousebuttondown(self, event):
        """Handle mouse button down events."""
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            target = self.get_click_target(mouse_pos)
            if target == 'zombie':
                action = ActionType.ATTACK
                if action:
                    self.execute_action(action)

        for button in self.game.game_ui.button_group:
            button.handle_event(event)

    def handle_mousebuttonup(self, event, create_context_menu):
        """Handle mouse button up events."""
        if event.button == 3:  # Right-click for popup menu
            mouse_pos = pygame.mouse.get_pos()
            target = self.get_click_target(mouse_pos)
            context_menu = create_context_menu(target, self.game.player, self.game.mouse_target)
            if context_menu:
                self.game.popup_menu = context_menu['menu']
                if 'target' in context_menu:
                    self.game.mouse_target = context_menu['target']
                if 'dxy' in context_menu:
                    self.game.menu_dxy = context_menu['dxy']
                if self.game.popup_menu:
                    self.game.popup_menu.show()

        elif event.button == 1:
            if self.game.popup_menu:
                menu_rect = self.game.popup_menu.menus[-1].rect
                if not menu_rect.collidepoint(event.pos):
                    self.game.popup_menu.hide()
                    self.game.popup_menu = None

        # Handle button clicks
        for button in self.game.game_ui.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'barricade': ActionType.BARRICADE,
                    'search': ActionType.SEARCH,
                    'enter': ActionType.ENTER,
                    'leave': ActionType.LEAVE,
                }
                action = button_to_action.get(action_name)
                if action:
                    self.execute_action(action)

    def handle_popup_menu(self, action):
        """Handle popup menu actions."""
        menu_to_action = {
            'Equip': ActionType.EQUIP,
            'Unequip': ActionType.UNEQUIP,
            'Use': ActionType.USE,
            'Install': ActionType.USE,
            'Reload': ActionType.USE,
            'Drop': ActionType.DROP,
            'Move': ActionType.MOVE_TO,
            'Barricade': ActionType.BARRICADE,
            'Search': ActionType.SEARCH,
            'Enter': ActionType.ENTER,
            'Leave': ActionType.LEAVE,
            'Attack': ActionType.ATTACK,
        }
        action_type = menu_to_action.get(action)
        if action_type:
            self.execute_action(action_type)

    def execute_action(self, action):
        """Execute the action based on ActionType."""
        if action == ActionType.QUIT:
            self.game.quit_game()

        player = self.game.player
        player.ticker += 1

        # Check buildings for fuel expiry
        for row in player.city.grid:
            for block in row:
                if hasattr(block, 'fuel_expiration') and block.fuel_expiration < player.ticker:
                    if block.lights_on:
                        block.lights_on = False

        # Each zombie gains an action point
        for zombie in self.game.zombies.list:
            zombie.action_points += 1
            zombie.take_action()
        
        # Movement
        if action == ActionType.MOVE_UP:
            player.move(0, -1)
        elif action == ActionType.MOVE_DOWN:
            player.move(0, 1)
        elif action == ActionType.MOVE_LEFT:
            player.move(-1, 0)
        elif action == ActionType.MOVE_RIGHT:
            player.move(1, 0)
        elif action == ActionType.MOVE_UPLEFT:
            player.move(-1, -1)
        elif action == ActionType.MOVE_UPRIGHT:
            player.move(1, -1)
        elif action == ActionType.MOVE_DOWNLEFT:
            player.move(-1, 1)
        elif action == ActionType.MOVE_DOWNRIGHT:
            player.move(1, 1)       
        elif action == ActionType.MOVE_TO:
            dxy = self.game.menu_dxy
            player.move(dxy[0], dxy[1])
            self.game.menu_dxy = None
        
        # Combat
        elif action == ActionType.ATTACK:
            self.game.chat_history.append(player.attack(self.game.mouse_target))

        # Building actions
        elif action == ActionType.BARRICADE:
            self.game.chat_history.append(player.barricade())
        elif action == ActionType.SEARCH:
            self.game.chat_history.append(player.search())
        elif action == ActionType.ENTER:
            self.game.chat_history.append(player.enter())
        elif action == ActionType.LEAVE:
            self.game.chat_history.append(player.leave())

        # Inventory actions
        elif action == ActionType.EQUIP:
            item = self.game.mouse_target
            properties = ITEMS[item.type]
            if properties.item_function == ItemFunction.MELEE or properties.item_function == ItemFunction.FIREARM:
                player.weapon.empty()
                player.weapon.add(item)
                self.game.chat_history.append(f"Equipped {properties.description}.")
            else:
                self.game.chat_history.append(f"You can't equip {properties.description}!")

        elif action == ActionType.UNEQUIP:
            item = self.game.mouse_target
            properties = ITEMS[item.type]
            player.weapon.empty()
            self.game.chat_history.append(f"Unequipped {properties.description}.")

        elif action == ActionType.USE:
            item = self.game.mouse_target
            properties = ITEMS[item.type]

            if item.type == ItemType.FIRST_AID_KIT:
                if player.hp < player.max_hp:
                    player.heal(20)
                    item.kill()
                    self.game.chat_history.append("Used a first aid kit, feeling a bit better.")
                else:
                    self.game.chat_history.append("You already feel healthy.")
        
            elif item.type == ItemType.PORTABLE_GENERATOR:
                if player.inside:
                    result, item_used = player.install_generator()
                    self.game.chat_history.append(result)
                    if item_used:
                        item.kill()
                else:
                    self.game.chat_history.append("Generators must be installed inside buildings.")
       
            elif item.type == ItemType.FUEL_CAN:
                if player.inside:
                    result, item_used = player.fuel_generator()
                    self.game.chat_history.append(result)
                    if item_used:
                        item.kill()
                else:
                    self.game.chat_history.append("There is no generator here.")

            elif item.type == ItemType.TOOLBOX:
                if player.inside:
                    pass
            
            elif item.type == ItemType.PISTOL_CLIP:
                weapon = player.weapon.sprite
                if weapon.type == ItemType.PISTOL:
                    if weapon.loaded_ammo < weapon.max_ammo:
                        self.game.chat_history.append(player.reload())
                        item.kill()
                    else:
                        self.game.chat_history.append("Your weapon is already fully loaded.")
                else:
                    self.game.chat_history.append(f"You can't reload {properties.description}.")

            elif item.type == ItemType.SHOTGUN_SHELL:
                weapon = player.weapon.sprite
                if weapon.type == ItemType.SHOTGUN:
                    if weapon.loaded_ammo < weapon.max_ammo:
                        self.game.chat_history.append(player.reload())
                        item.kill()
                    else:
                        self.game.chat_history.append("Your weapon is already fully loaded.")
                else:
                    self.game.chat_history.append(f"You can't reload {properties.description}.")                
     
        elif action == ActionType.DROP:
            item = self.game.mouse_target
            properties = ITEMS[item.type]
            item.kill()
            self.game.chat_history.append(f"Dropped {properties.description}.")

        self.game.game_ui.update_zombie_sprites()

    # Get the target of the mouse click
    def get_click_target(self, mouse_pos):
        for sprite in self.game.game_ui.viewport_group:
            if sprite.dx == 0 and sprite.dy == 0 and sprite.rect.collidepoint(mouse_pos):
                self.game.mouse_target = sprite
                return 'center block'
            elif sprite.rect.collidepoint(mouse_pos):
                self.game.mouse_target = sprite                
                return 'block'
        for sprite in self.game.player.inventory:
            if sprite.rect.collidepoint(mouse_pos):
                self.game.mouse_target = sprite  
                return 'item'
        for sprite in self.game.game_ui.zombie_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.game.mouse_target = sprite                
                return 'zombie'
        return 'screen'
