# effects.py

import pygame
from settings import *

class ScreenTransition:
    """Handles screen transition effects."""
    def __init__(self, screen, draw_ui, update_ui):
        self.screen = screen
        self.draw_ui = draw_ui
        self.update_ui = update_ui

        self.clock = pygame.time.Clock()

    def circle_wipe(self, target_function, chat_history, *args, **kwargs):
        """Perform a circle wipe transition effect and call the target_function to change game state."""
        max_radius = int((SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2) ** 0.5) # Cover the screen
        duration = 1.0
        steps = int(duration * 30)
        increment = max_radius // steps

        # Create surface for the mask effect
        mask_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Circle wipe to black
        for radius in range(max_radius, 0, -increment):
            self.draw_ui(chat_history)
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)

        # Execute the target function
        result = target_function(*args, **kwargs)
        self.update_ui()


        # Reverse circle wipe to reveal new state
        for radius in range(0, max_radius, increment):
            self.draw_ui(chat_history)
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

        return result
    
    def flicker_red(self, intensity=120, duration=0.3):
        """Flickers the screen red to indicate damage taken."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, intensity))  # Semi-transparent red

        steps = int(duration * 30)  # Convert seconds to frames
        for _ in range(steps):
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS flicker effect    