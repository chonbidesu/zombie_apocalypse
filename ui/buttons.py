import pygame
from button import Button

class ButtonManager:
    def __init__(self):
        self.button_group = pygame.sprite.Group()
        self.enter_button = Button('enter', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
        self.leave_button = Button('leave', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)

        buttons = ['barricade', 'search', 'enter']
        for i, button_name in enumerate(buttons):
            button = Button(button_name, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
            self.button_group.add(button)

    def update(self, player):
        """Swap enter/leave buttons dynamically."""
        if player.inside:
            for button in self.button_group:
                if button.name == 'enter':
                    self.button_group.remove(button)
                    self.button_group.add(self.leave_button)
        else:
            for button in self.button_group:
                if button.name == 'leave':
                    self.button_group.remove(button)
                    self.button_group.add(self.enter_button)
