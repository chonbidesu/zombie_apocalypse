# pause_menu.py

from settings import *
from ui.widgets import Button


class PauseMenu:
    """Create a pause menu."""
    def __init__(self):
        self.button_group = self.create_menu_button_group()

    def create_menu_button_group(self):
        button_group = pygame.sprite.Group()

        col_1 = SCREEN_WIDTH // 4 - 58
        col_2 = SCREEN_WIDTH // 2 - 58
        col_3 = SCREEN_WIDTH * 3 // 4 - 58
        row_1 = SCREEN_HEIGHT // 3
        row_2 = SCREEN_HEIGHT // 3 + 100

        newgame_button = self._create_button('menu_newgame', col_1, row_1)
        button_group.add(newgame_button)

        save_button = self._create_button('menu_save', col_2, row_1)
        button_group.add(save_button)

        load_button = self._create_button('menu_load', col_2, row_2)
        button_group.add(load_button)

        play_button = self._create_button('menu_play', col_3, row_1)
        button_group.add(play_button)

        exit_button = self._create_button('menu_exit', col_3, row_2)
        button_group.add(exit_button)

        return button_group   
    
    def _create_button(self, name, x, y):
        """Create a button."""
        width = 116
        height = 51
        button = Button(name, width, height, is_pressable=False)
        button.update(x, y)
        return button

    def draw(self, screen):
        # Create a dark green background
        screen.fill(DARK_GREEN)
        
        title_text = font_xxl.render("Paused", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        screen.blit(title_text, title_rect)
        self.button_group.draw(screen)