# mousebutton_down_handler.py

import pygame

from actions import Move, ExtractDNA, Inject, Heal, Attack
from data import ItemType
from events.click_target import ClickTarget


class MouseButtonDownHandler:
    """Handles mouse clicks based on game state."""

    def __init__(self, game):
        self.game = game

    def handle(self, event):
        """Processes mouse clicks based on game state."""
        if self.game.title_screen:
            self.handle_title(event)
        elif self.game.paused or self.game.skills_menu:
            self.handle_menu(event)
        else:
            self.handle_game(event)

    def handle_title(self, event):
        """Handles mouse clicks on the title screen."""
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
                    newgame_menu.update_portrait_state()

            for text_input in newgame_menu.text_inputs.values():
                text_input.active = text_input.rect.collidepoint(event.pos)  

        else:
            for button in title_menu.buttons:
                button.handle_event(event) 

    def handle_menu(self, event):
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

    def handle_game(self, event):
        """Handles mouse clicks during gameplay."""
        player = self.game.state.player
        action = None

        if event.button == 1 and not player.is_dead:
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
                if action.sfx:
                    action.play_sound()

            elif target.type == 'block' and not self.game.popup_menu:
                action = Move(player)
                action.execute(target.sprite)  
                if action.sfx:
                    action.play_sound()
            
            elif player.is_human and target.type == 'human':
                if player.equipped:
                    if player.equipped.type == ItemType.FIRST_AID_KIT:
                        action = Heal(player)
                        action.execute(target.sprite.npc)
                        if action.sfx:
                            action.play_sound()

                else:
                    #action = Speak(player)
                    #action.execute(target.sprite.npc)  
                    pass     
            
            elif player.is_human and target.type == 'self':
                if player.equipped:
                    if player.equipped.type == ItemType.FIRST_AID_KIT:
                        action = Heal(player)
                        action.execute(player)
                        if action.sfx:
                            action.play_sound()

            else:
                skills_button = self.game.game_ui.status_panel.button_group.sprite
                skills_button.handle_event(event)

            if action and action.message:
                self.handle_feedback(action.message)

        # Handle graphical changes for button clicks
        for button in self.game.game_ui.actions_panel.button_group:
            button.handle_event(event)


    def handle_feedback(self, message):
        """Handle feedback messages from actions."""
        self.game.chat_history.append(message)            
              
