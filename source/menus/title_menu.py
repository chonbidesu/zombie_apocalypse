# title_menu.py

import pygame
from settings import *
from ui import Button
from data import Action


class TitleMenu:
    def __init__(self):
        self.buttons = self.create_buttons()
        self.playing_music = False

    def create_buttons(self):
        buttons = pygame.sprite.Group()
        width = 232
        height = 102        
        x = SCREEN_WIDTH // 2 - 116
        y_unit = SCREEN_HEIGHT // 5

        new_game_button = Button('menu_newgame', width, height)
        new_game_button.update(x, y_unit * 2)
        buttons.add(new_game_button)

        load_game_button = Button('menu_load', width, height)
        load_game_button.update(x, y_unit * 3)
        buttons.add(load_game_button)

        exit_button = Button('menu_exit', width, height)
        exit_button.update(x, y_unit * 4)
        buttons.add(exit_button)

        return buttons
    
    def draw(self, screen):
        self.title_music()
        screen.fill(DARK_GREEN)
        title_text = font_xxl.render("Zombie Apocalypse", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))
        screen.blit(title_text, title_rect)        

        self.buttons.draw(screen)

    def title_music(self):
        if self.playing_music:
            return
        else:
            self.playing_music = True
            pygame.mixer.init()
            pygame.mixer.music.load(ResourcePath("assets/music/summoning.mp3").path)
            pygame.mixer.music.play(-1)

class TitleAction:
    """Handles executing actions for the title screen."""
    def __init__(self, game):
        self.game = game

    def execute(self, action):
        """Execute AI and player actions."""
        if action == Action.QUIT:
            return self.game.quit_game()

        elif action == Action.NEW_GAME:
            self.game.start_new_game = True

        elif action == Action.LOAD_MENU:
            self.game.load_menu = True

        elif action == Action.BACK:
            self.game.load_menu = False    