# events.py

import pygame

from settings import *

class SystemAction(Enum):
    QUIT = auto()
    PAUSE = auto()
    OPTIONS = auto()
    CLOSE_MAP = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    RESTART = auto()

class PlayerAction(Enum):
    # Movement
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UPLEFT = auto()
    MOVE_UPRIGHT = auto()
    MOVE_DOWNLEFT = auto()
    MOVE_DOWNRIGHT = auto()

    # Right-click menu actions
    EQUIP = auto()
    UNEQUIP = auto()
    USE = auto()
    DROP = auto()    

    # Button actions
    BARRICADE = auto()
    SEARCH = auto()
    ENTER = auto()
    LEAVE = auto()


class EventHandler:
    def __init__(self, game):
        self.game = game
        self.state = self.game.player.state
        self.actions = self.game.player.actions
        self.mouse_sprite = None

    def handle_events(self, events, ContextMenu):
        """Handle all game events."""
        for event in events:
            if event.type == pygame.QUIT:
                self.act(SystemAction.QUIT)

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event, ContextMenu)

            elif event.type == pygame.MOUSEMOTION:
                self.game.cursor.rect.center = event.pos

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
                pygame.K_ESCAPE: SystemAction.CLOSE_MAP,
                pygame.K_PAGEDOWN: SystemAction.ZOOM_OUT,
                pygame.K_PAGEUP: SystemAction.ZOOM_IN,
            }
        else:
            key_to_action = {
                pygame.K_w: PlayerAction.MOVE_UP,
                pygame.K_s: PlayerAction.MOVE_DOWN,
                pygame.K_a: PlayerAction.MOVE_LEFT,
                pygame.K_d: PlayerAction.MOVE_RIGHT,
                pygame.K_q: PlayerAction.MOVE_UPLEFT,
                pygame.K_e: PlayerAction.MOVE_UPRIGHT,
                pygame.K_z: PlayerAction.MOVE_DOWNLEFT,
                pygame.K_c: PlayerAction.MOVE_DOWNRIGHT,
                pygame.K_ESCAPE: SystemAction.PAUSE,
            }
        action = key_to_action.get(event.key)
        if action:
            self.act(action)

    def handle_mousebuttondown(self, event):
        """Handle mouse button down events."""
        if event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            target = self.get_click_target(mouse_pos)
            if target == 'npc':
                action = self.state.Action.ATTACK
                self.act(action)
            elif target == 'block' and not self.game.popup_menu:
                action = self.state.Action.MOVE
                self.act(action)             

        for button in self.game.game_ui.actions_panel.button_group:
            button.handle_event(event)

        for button in self.game.pause_menu.button_group:
            button.handle_event(event)

    def handle_mousebuttonup(self, event, ContextMenu):
        """Handle mouse button up events."""
        if event.button == 3:  # Right-click for popup menu
            mouse_pos = pygame.mouse.get_pos()
            target = self.get_click_target(mouse_pos)
            self.context_menu = ContextMenu(target, self.game.player, self.mouse_sprite)
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

        # Handle button clicks
        for button in self.game.game_ui.actions_panel.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'barricade': PlayerAction.BARRICADE,
                    'search': PlayerAction.SEARCH,
                    'enter': PlayerAction.ENTER,
                    'leave': PlayerAction.LEAVE,
                }
                action = button_to_action.get(action_name)
                if action:
                    self.act(action)

        for button in self.game.pause_menu.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'play': SystemAction.PAUSE,
                    'options': SystemAction.OPTIONS,
                    'exit': SystemAction.QUIT,
                }
                action = button_to_action.get(action_name)
                if action:
                    self.act(action)

    def handle_popup_menu(self, action):
        """Handle popup menu actions."""
        menu_to_action = {
            'Equip': PlayerAction.EQUIP,
            'Unequip': PlayerAction.UNEQUIP,
            'Use': PlayerAction.USE,
            'Install': PlayerAction.USE,
            'Reload': PlayerAction.USE,
            'Drop': PlayerAction.DROP,
            'Barricade': PlayerAction.BARRICADE,
            'Search': PlayerAction.SEARCH,
            'Enter': PlayerAction.ENTER,
            'Leave': PlayerAction.LEAVE,
        }
        action_type = menu_to_action.get(action)
        if action_type:
            self.act(action_type)

    def get_click_target(self, mouse_pos):
        """Get the target of a mouse click, saving the sprite and returning the target type."""
        for sprite in self.game.game_ui.viewport.viewport_group:
            if sprite.dx == 0 and sprite.dy == 0 and sprite.rect.collidepoint(mouse_pos):
                self.mouse_sprite = sprite
                return 'center block'
            elif sprite.rect.collidepoint(mouse_pos):
                self.mouse_sprite = sprite                
                return 'block'
        for sprite in self.game.player.inventory:
            if sprite.rect.collidepoint(mouse_pos):
                self.mouse_sprite = sprite  
                return 'item'
        for sprite in self.game.game_ui.description_panel.zombie_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.mouse_sprite = sprite                
                return 'zombie'
        for sprite in self.game.game_ui.description_panel.human_sprite_group:
            if sprite.rect.collidepoint(mouse_pos):
                self.mouse_sprite = sprite                
                return 'human'
        return 'screen'

    def act(self, action):
        """Execute the action based on action type."""
        if action == SystemAction.QUIT:
            self.game.quit_game()

        elif action == SystemAction.PAUSE:
            # Toggle game pause
            self.game.pause_game()
            return
        elif action == SystemAction.OPTIONS:
            pass

        elif action == SystemAction.CLOSE_MAP:
            self.game.reading_map = False

        elif action == SystemAction.ZOOM_IN:
            self.game.game_ui.map.zoom_in = True

        elif action == SystemAction.ZOOM_OUT:
            self.game.game_ui.map.zoom_in = False

        self.game.ticker += 1

        # Check buildings for fuel expiry
        for row in self.game.city.grid:
            for block in row:
                if hasattr(block, 'fuel_expiration') and block.fuel_expiration < self.game.ticker:
                    if block.lights_on:
                        block.lights_on = False

        # Each character gains an action point
        for zombie in self.game.characters.list:              
            zombie.action_points += 1
            zombie.take_action()
        
        # Movement
        if action == PlayerAction.MOVE_UP:
            self.game.player.action.move(0, -1)
        elif action == PlayerAction.MOVE_DOWN:
            self.game.player.action.move(0, 1)
        elif action == PlayerAction.MOVE_LEFT:
            self.game.player.action.move(-1, 0)
        elif action == PlayerAction.MOVE_RIGHT:
            self.game.player.action.move(1, 0)
        elif action == PlayerAction.MOVE_UPLEFT:
            self.game.player.action.move(-1, -1)
        elif action == PlayerAction.MOVE_UPRIGHT:
            self.game.player.action.move(1, -1)
        elif action == PlayerAction.MOVE_DOWNLEFT:
            self.game.player.action.move(-1, 1)
        elif action == PlayerAction.MOVE_DOWNRIGHT:
            self.game.player.action.move(1, 1)       
        elif action == self.state.Action.MOVE:
            dx, dy = self.mouse_sprite.dx, self.mouse_sprite.dy
            self.game.player.action.move(dx, dy)
        
        # Combat
        elif action == self.state.Action.ATTACK:
            self.game.chat_history.append(self.game.player.action.attack(self.mouse_sprite))

        # Building actions
        elif action == PlayerAction.BARRICADE:
            self.game.game_ui.action_progress.start('Barricading', self.game.player.action.barricade)
        elif action == PlayerAction.SEARCH:
            self.game.game_ui.action_progress.start('Searching', self.game.player.action.search)
        elif action == PlayerAction.ENTER:
            current_block = self.game.player.city.block(self.game.player.location[0], self.game.player.location[1])
            properties = BLOCKS[current_block.type]
            if properties.is_building:
                result = self.game.game_ui.screen_transition.circle_wipe(self.game.player.action.enter, self.game.chat_history)
                self.game.chat_history.append(result)
            else:
                self.game.chat_history.append(self.game.player.action.enter())
        elif action == PlayerAction.LEAVE:
            result = self.game.game_ui.screen_transition.circle_wipe(self.game.player.action.leave, self.game.chat_history)
            self.game.chat_history.append(result)

        # Inventory actions
        elif action == PlayerAction.EQUIP:
            item = self.mouse_sprite
            properties = ITEMS[item.type]
            if properties.item_function == ItemFunction.MELEE or properties.item_function == ItemFunction.FIREARM:
                player.weapon.empty()
                player.weapon.add(item)
                self.game.chat_history.append(f"Equipped {properties.description}.")
            else:
                self.game.chat_history.append(f"You can't equip {properties.description}!")

        elif action == PlayerAction.UNEQUIP:
            item = self.mouse_sprite
            properties = ITEMS[item.type]
            player.weapon.empty()
            self.game.chat_history.append(f"Unequipped {properties.description}.")

        elif action == PlayerAction.USE:
            item = self.mouse_sprite
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
                    self.game.game_ui.action_progress.start('Installing generator', player.install_generator)
                    result, item_used = player.install_generator()
                    self.game.chat_history.append(result)
                    if item_used:
                        item.kill()
                else:
                    self.game.chat_history.append("Generators must be installed inside buildings.")
       
            elif item.type == ItemType.FUEL_CAN:
                if player.inside:
                    self.game.game_ui.action_progress.start('Fuelling generator')
                    result, item_used = player.fuel_generator()
                    self.game.chat_history.append(result)
                    if item_used:
                        item.kill()
                else:
                    self.game.chat_history.append("There is no generator here.")

            elif item.type == ItemType.TOOLBOX:
                if player.inside:
                    self.game.game_ui.action_progress.start('Repairing building')
                    self.game.chat_history.append(player.repair_building())
                else:
                    self.game.chat_history.append("You have to be inside a building to use this.")

            elif item.type == ItemType.MAP:
                self.game.reading_map = True
            
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
     
        elif action == PlayerAction.DROP:
            item = self.mouse_sprite
            properties = ITEMS[item.type]
            item.kill()
            self.game.chat_history.append(f"Dropped {properties.description}.")

        # Update zombie sprites after taking action
        self.game.game_ui.update()


