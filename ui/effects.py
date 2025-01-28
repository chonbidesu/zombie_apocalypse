# effects.py

import pygame
from settings import *

class ScreenTransition:
    """Handles screen transition effects."""
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

    def circle_wipe(self, duration=1.0):
        """Perform a circle wipe transition effect and call the target_function to change game state."""
        max_radius = int((SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2) ** 0.5) # Cover the screen
        steps = int(duration * 30)
        increment = max_radius // steps

        # Create surface for the mask effect
        mask_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Circle wipe to black
        for radius in range(max_radius, 0, -increment):
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(30)

        # Execute the target function
        #result = target_function()
        #self.update_npc_sprites()

        # Reverse circle wipe to reveal new state
        for radius in range(0, max_radius, increment):
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)