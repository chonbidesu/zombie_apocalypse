import pygame
from enum import Enum, auto

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
    USE = auto()
    DROP = auto()
    MOVE_TO = auto()

    # System actions
    QUIT = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()


class ActionHandler:
    def __init__(self, game):
        self.game = game

    def handle_events(self, events, chat_history, scroll_offset, create_context_menu):
        """Handle all game events."""
        for event in events:
            if event.type == pygame.QUIT:
                self.execute_action(ActionType.QUIT, chat_history, scroll_offset)

            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event, chat_history, scroll_offset)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_mousebuttondown(event, scroll_offset)

            elif event.type == pygame.MOUSEBUTTONUP:
                self.handle_mousebuttonup(event, chat_history, scroll_offset, create_context_menu)

            elif event.type == pygame.MOUSEMOTION:
                self.game.cursor.rect.center = event.pos

            elif event.type == pygame.USEREVENT and event.code == 'MENU':
                if event.name is None:
                    self.game.popup_menu = None
                else:
                    if self.game.menu_target is not None:
                        self.handle_popup_menu(
                            event.text, chat_history, scroll_offset
                        )
                    elif self.game.menu_dxy is not None:
                        self.handle_popup_menu(
                            event.text, chat_history, scroll_offset
                        )
                    else:
                        self.handle_popup_menu(
                            event.text, chat_history, scroll_offset
                        )
                    #self.game.game_ui.update_viewport()
                    self.game.popup_menu = None                

    def handle_keydown(self, event, chat_history, scroll_offset):
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
            self.execute_action(action, chat_history, scroll_offset)

    def handle_mousebuttondown(self, event, scroll_offset):
        """Handle mouse button down events."""
        if event.button == 4:  # Scroll up
            self.execute_action(ActionType.SCROLL_UP, None, scroll_offset=scroll_offset)
        elif event.button == 5:  # Scroll down
            self.execute_action(ActionType.SCROLL_DOWN, None, scroll_offset=scroll_offset)

    def handle_mousebuttonup(self, event, chat_history, scroll_offset, create_context_menu):
        """Handle mouse button up events."""
        if event.button == 3:  # Right-click for popup menu
            mouse_pos = pygame.mouse.get_pos()
            target, sprite = self.get_click_target(mouse_pos)
            context_menu = create_context_menu(target, self.game.player, sprite)
            if context_menu:
                self.game.popup_menu = context_menu['menu']
                if 'target' in context_menu:
                    self.game.menu_target = context_menu['target']
                if 'dxy' in context_menu:
                    self.game.menu_dxy = context_menu['dxy']
                if self.game.popup_menu:
                    self.game.popup_menu.show()

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
                    self.execute_action(action, chat_history, scroll_offset)

    def handle_popup_menu(self, action, chat_history, scroll_offset):
        """Handle popup menu actions."""
        menu_to_action = {
            'Equip': ActionType.EQUIP,
            'Use': ActionType.USE,
            'Drop': ActionType.DROP,
            'Move': ActionType.MOVE_TO,
            'Barricade': ActionType.BARRICADE,
            'Search': ActionType.SEARCH,
            'Enter': ActionType.ENTER,
            'Leave': ActionType.LEAVE,
        }
        action_type = menu_to_action.get(action)
        if action_type:
            self.execute_action(action_type, chat_history, scroll_offset)

    def execute_action(self, action, chat_history, scroll_offset):
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

        # Building actions
        elif action == ActionType.BARRICADE:
            chat_history.append(player.barricade())
        elif action == ActionType.SEARCH:
            chat_history.append(player.search())
        elif action == ActionType.ENTER:
            chat_history.append(player.enter())
        elif action == ActionType.LEAVE:
            chat_history.append(player.leave())

        # Inventory actions
        elif action == ActionType.EQUIP:
            item = self.game.menu_target
            player.weapon.empty()
            player.weapon.add(item)
            chat_history.append(f"Equipped {item.name}.")
            self.game.menu_target = None
        elif action == ActionType.USE:
            item = self.game.menu_target
            chat_history.append(f"Used {item.name}.")
            self.game.menu_target = None

        elif action == ActionType.DROP:
            item = self.game.menu_target
            item.kill()
            chat_history.append(f"Dropped {item.name}.")
            self.game.menu_target = None

        # System actions
        elif action == ActionType.SCROLL_UP:
            scroll_offset -= 1
        elif action == ActionType.SCROLL_DOWN:
            scroll_offset += 1

    # Get the target of the mouse click
    def get_click_target(self, mouse_pos):
        for sprite in self.game.game_ui.viewport_group:
            if sprite.dx == 0 and sprite.dy == 0 and sprite.rect.collidepoint(mouse_pos):
                return 'center block', sprite
            elif sprite.rect.collidepoint(mouse_pos):
                return 'block', sprite
        for sprite in self.game.player.inventory:
            if sprite.rect.collidepoint(mouse_pos):
                return 'item', sprite
        return 'screen', None
