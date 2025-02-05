# pause_menu.py

from settings import *
from ui.widgets import Button


class PauseMenu:
    """Create a pause menu."""
    def __init__(self):
        self.button_group = self.create_menu_button_group()

    def create_menu_button_group(self):
        button_group = pygame.sprite.Group()

        self.play_button = Button('play')
        self.play_button.update(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 - 100)
        button_group.add(self.play_button)

        self.options_button = Button('options')
        self.options_button.update(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2)
        button_group.add(self.options_button)

        self.exit_button = Button('exit')
        self.exit_button.update(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 100)
        button_group.add(self.exit_button)

        return button_group   
    
    def draw(self, screen):
        # Create a dark green background
        screen.fill(DARK_GREEN)
        
        title_text = font_xxl.render("Paused", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))

        screen.blit(title_text, title_rect)
        self.button_group.draw(screen)