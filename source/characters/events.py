# events.py

import pygame

from settings import *

class ActionHandler:
    def __init__(self, game):
        self.game = game
        self.mouse_sprite = None

    def handle_events(self, events, ContextMenu):
        """Handle all game events."""
        for event in events:
            if event.type == pygame.QUIT:
                self.execute_action(ActionType.QUIT)

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
                    self.game.popup_menu = None
                else:
                    self.handle_popup_menu(event.text)

                    #self.game.game_ui.update_viewport()
                    self.game.popup_menu = None                

    def handle_keydown(self, event):
        """Handle key press events."""
        if self.game.reading_map:
            key_to_action = {
                pygame.K_ESCAPE: ActionType.CLOSE_MAP,
                pygame.K_PAGEDOWN: ActionType.ZOOM_OUT,
                pygame.K_PAGEUP: ActionType.ZOOM_IN,
            }
        else:
            key_to_action = {
                pygame.K_w: ActionType.MOVE_UP,
                pygame.K_s: ActionType.MOVE_DOWN,
                pygame.K_a: ActionType.MOVE_LEFT,
                pygame.K_d: ActionType.MOVE_RIGHT,
                pygame.K_q: ActionType.MOVE_UPLEFT,
                pygame.K_e: ActionType.MOVE_UPRIGHT,
                pygame.K_z: ActionType.MOVE_DOWNLEFT,
                pygame.K_c: ActionType.MOVE_DOWNRIGHT,
                pygame.K_ESCAPE: ActionType.PAUSE,
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
                self.execute_action(action)
            elif target == 'block' and not self.game.popup_menu:
                action = ActionType.MOVE_TO
                self.execute_action(action)                

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
                    'barricade': ActionType.BARRICADE,
                    'search': ActionType.SEARCH,
                    'enter': ActionType.ENTER,
                    'leave': ActionType.LEAVE,
                }
                action = button_to_action.get(action_name)
                if action:
                    self.execute_action(action)

        for button in self.game.pause_menu.button_group:
            action_name = button.handle_event(event)
            if action_name:
                button_to_action = {
                    'play': ActionType.PAUSE,
                    'options': ActionType.OPTIONS,
                    'exit': ActionType.QUIT,
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
            'Barricade': ActionType.BARRICADE,
            'Search': ActionType.SEARCH,
            'Enter': ActionType.ENTER,
            'Leave': ActionType.LEAVE,
        }
        action_type = menu_to_action.get(action)
        if action_type:
            self.execute_action(action_type)

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
        return 'screen'

    def execute_action(self, action):
        """Execute the action based on ActionType."""
        if action == ActionType.QUIT:
            self.game.quit_game()

        elif action == ActionType.PAUSE:
            # Toggle game pause
            self.game.pause_game()
            return
        elif action == ActionType.OPTIONS:
            pass

        elif action == ActionType.CLOSE_MAP:
            self.game.reading_map = False

        elif action == ActionType.ZOOM_IN:
            self.game.game_ui.map.zoom_in = True

        elif action == ActionType.ZOOM_OUT:
            self.game.game_ui.map.zoom_in = False

        player = self.game.player
        player.ticker += 1

        # Check buildings for fuel expiry
        for row in player.city.grid:
            for block in row:
                if hasattr(block, 'fuel_expiration') and block.fuel_expiration < player.ticker:
                    if block.lights_on:
                        block.lights_on = False

        # Each zombie gains an action point
        pursued_by_zombies = 0
        for zombie in self.game.zombies.list:
            if zombie.pursuing_player:
                pursued_by_zombies += 1
                print(f"Action points lost: {zombie.action_points_lost}")                
            zombie.action_points += 1
            zombie.take_action()
        print(f"Pursued by {pursued_by_zombies} zombies.")
        
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
            dx, dy = self.mouse_sprite.dx, self.mouse_sprite.dy
            player.move(dx, dy)
        
        # Combat
        elif action == ActionType.ATTACK:
            self.game.chat_history.append(player.attack(self.mouse_sprite))

        # Building actions
        elif action == ActionType.BARRICADE:
            self.game.game_ui.action_progress.start('Barricading', player.barricade)
        elif action == ActionType.SEARCH:
            self.game.game_ui.action_progress.start('Searching', player.search)
        elif action == ActionType.ENTER:
            current_block = player.city.block(player.location[0], player.location[1])
            properties = BLOCKS[current_block.type]
            if properties.is_building:
                result = self.game.game_ui.screen_transition.circle_wipe(player.enter, self.game.chat_history)
                self.game.chat_history.append(result)
            else:
                self.game.chat_history.append(player.enter())
        elif action == ActionType.LEAVE:
            result = self.game.game_ui.screen_transition.circle_wipe(player.leave, self.game.chat_history)
            self.game.chat_history.append(result)

        # Inventory actions
        elif action == ActionType.EQUIP:
            item = self.mouse_sprite
            properties = ITEMS[item.type]
            if properties.item_function == ItemFunction.MELEE or properties.item_function == ItemFunction.FIREARM:
                player.weapon.empty()
                player.weapon.add(item)
                self.game.chat_history.append(f"Equipped {properties.description}.")
            else:
                self.game.chat_history.append(f"You can't equip {properties.description}!")

        elif action == ActionType.UNEQUIP:
            item = self.mouse_sprite
            properties = ITEMS[item.type]
            player.weapon.empty()
            self.game.chat_history.append(f"Unequipped {properties.description}.")

        elif action == ActionType.USE:
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
     
        elif action == ActionType.DROP:
            item = self.mouse_sprite
            properties = ITEMS[item.type]
            item.kill()
            self.game.chat_history.append(f"Dropped {properties.description}.")

        # Update zombie sprites after taking action
        self.game.game_ui.update()


