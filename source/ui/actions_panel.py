# actions_panel.py

import pygame

from settings import *
from ui.widgets import Button
from data import BLOCKS, SKILLS, SkillType


class ActionsPanel:
    """Draw the actions panel and buttons."""
    def __init__(self, game, screen):
        self.screen = screen
        self.game = game
        self.width = SCREEN_HEIGHT // 2
        self.height = SCREEN_HEIGHT * 3 // 20 - 10
        self.button_group = self._create_button_group()

    def draw(self):
        x, y = 10, (SCREEN_HEIGHT // 2) + 40     
        # Draw the panel background and border
        pygame.draw.rect(self.screen, WHITE, (x, y, self.width, self.height))
        pygame.draw.rect(self.screen, BLACK, (x, y, self.width, self.height), 2)

        # Render the title
        title_text = font_large.render("Available Actions", True, BLACK)
        title_rect = title_text.get_rect(center=(x + self.width // 2, y + 15))
        self.screen.blit(title_text, title_rect)
        self.button_group.draw(self.screen)        

    # Set up action button group
    def _create_button_group(self):
        button_group = pygame.sprite.Group()

        width = 100
        height = 49

        self.barricade_button = Button('barricade', width, height, is_pressable=True)
        self.close_doors_button = Button('close_doors', width, height, is_pressable=True)
        self.open_doors_button = Button('open_doors', width, height, is_pressable=True)
        self.search_button = Button('search', width, height, is_pressable=True)
        self.enter_button = Button('enter', width, height, is_pressable=True)
        self.leave_button = Button('leave', width, height, is_pressable=True)
        self.dump_button = Button('dump', width, height, is_pressable=True)
        self.ransack_button = Button('ransack', width, height, is_pressable=True)
        self.break_cades_button = Button('break_cades', width, height, is_pressable=True)
        self.stand_button = Button('stand', width, height, is_pressable=True) 

        return button_group        

    # Update action buttons according to player status
    def update(self):
        self.button_group.empty() # Clear existing buttons

        player = self.game.state.player
        x, y = player.location[0], player.location[1]
        block = self.game.state.city.block(x, y)
        properties = BLOCKS[block.type]
        block_npcs = player.state.filter_characters_at_location(x, y, player.inside, include_player=False)
        buttons = []

        if player.is_dead:
            buttons.append(self.stand_button)
        else:
            if player.inside:
                if player.has_skill(SkillType.CONSTRUCTION):
                    buttons.append(self.barricade_button)

                buttons.append(self.search_button)

                if block.barricade.level == 0:
                    if player.is_human:
                        if block.doors_closed:
                            buttons.append(self.open_doors_button)
                        else:
                            buttons.append(self.close_doors_button)  

                buttons.append(self.leave_button)   

                if player.is_human:
                    if len(block_npcs.dead_bodies) > 0:
                        buttons.append(self.dump_button)             
                else:
                    if player.has_skill(SkillType.RANSACK):
                        buttons.append(self.ransack_button)
                        
            else:
                if properties.is_building:
                    buttons.append(self.enter_button)

            if properties.is_building and block.barricade.level > 0:
                buttons.append(self.break_cades_button)

        # Calculate button positions
        max_buttons_per_row = 3
        width = 120
        height = 40
        start_x = 40
        start_y = SCREEN_HEIGHT // 2 + 60

        for row in range((len(buttons) + max_buttons_per_row - 1) // max_buttons_per_row):
            row_buttons = buttons[row * max_buttons_per_row:(row + 1) * max_buttons_per_row]
            total_row_width = len(row_buttons) * width
            start_x = (self.width - total_row_width) // 2 + 10  # Center the row

            for col, button in enumerate(row_buttons):
                x = start_x + col * width
                y = start_y + row * height
                button.update(x, y)
                self.button_group.add(button)
