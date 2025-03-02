# effects.py

import pygame
from core.settings import *

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
        steps = int(duration * 60)
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
            self.clock.tick(60)

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

    def start_scene(self, chat_history):
        """Reverse circle wipe to reveal the game after loading/starting new game"""
        max_radius = int((SCREEN_WIDTH ** 2 + SCREEN_HEIGHT ** 2) ** 0.5) # Cover the screen
        duration = 1.0
        steps = int(duration * 60)
        increment = max_radius // steps

        # Create surface for the mask effect
        mask_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Update UI to ensure objects are initialized
        self.update_ui()

        for radius in range(0, max_radius, increment):
            self.draw_ui(chat_history)
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)        

    def flicker_red(self, intensity=120, duration=0.1):
        """Flickers the screen red to indicate damage taken."""
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, intensity))  # Semi-transparent red

        steps = int(duration * 60)  # Convert seconds to frames
        for _ in range(steps):
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)  # 60 FPS flicker effect    

    def dissolve_scene(self, target_function, chat_history, *args, **kwargs):
        """Smoothly dissolve from the current scene to the next state."""
        duration = 0.2
        steps = int(duration * 60)
        alpha_step = 255 // steps

        # Capture the pre-transition scene
        pre_surface = self.screen.copy()

        # Execute the target function
        result = target_function(*args, **kwargs)
        self.update_ui()

        # Dissolve effect
        for alpha in range(0, 256, alpha_step):
            self.draw_ui(chat_history)

            # Draw pre-transition with decreasing opacity
            faded_pre = pre_surface.copy()
            faded_pre.set_alpha(255 - alpha)
            self.screen.blit(faded_pre, (0, 0))

            self.update_ui()
            pygame.display.flip()
            self.clock.tick(60) 


class ParallaxBackground:
    def __init__(self, image_paths, scroll_speeds):
        """Initialize the parallax background."""
        self.layers = [pygame.image.load(img).convert_alpha() for img in image_paths]
        self.speeds = scroll_speeds
        self.x_positions = [0] * len(self.layers)

        # Ensure all images match screen width
        for i in range(len(self.layers)):
            img = self.layers[i]
            aspect_ratio = img.get_width() / img.get_height()
            new_width = int(SCREEN_HEIGHT * aspect_ratio)
            self.layers[i] = pygame.transform.scale(img, (new_width, SCREEN_HEIGHT))

    def update(self):
        """Update the positions of each layer for the parallax effect."""
        for i in range(len(self.layers)):
            self.x_positions[i] -= self.speeds[i]

            # Reset position when fully scrolled
            if self.x_positions[i] <= -self.layers[i].get_width():
                self.x_positions[i] = 0

    def draw(self, screen):
        """Draw the layers onto the screen."""
        for i in range(len(self.layers)):
            layer_width = self.layers[i].get_width()
            screen.blit(self.layers[i], (self.x_positions[i], 0))
            screen.blit(self.layers[i], (self.x_positions[i] + layer_width, 0))  # Loop image