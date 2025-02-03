# button.py

import pygame

from settings import *

class Button(pygame.sprite.Sprite):
    """A button that changes images on mouse events."""
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.is_pressed = False
        self._image_up = None  # Private attributes for lazy-loaded images
        self._image_down = None
        self.rect = pygame.Rect(0, 0, 100, 49)  # Initial rect size (scale later when image is loaded)

    @property
    def image_up(self):
        """Lazy load the 'up' image when first accessed."""
        if self._image_up is None:
            self._image_up = pygame.image.load(ResourcePath(f"assets/{self.name}_up.png").path).convert_alpha()
            self._image_up = pygame.transform.scale(self._image_up, (100, 49))  # Scale when loading
        return self._image_up

    @property
    def image_down(self):
        """Lazy load the 'down' image when first accessed."""
        if self._image_down is None:
            self._image_down = pygame.image.load(ResourcePath(f"assets/{self.name}_down.png").path).convert_alpha()
            self._image_down = pygame.transform.scale(self._image_down, (100, 49))  # Scale when loading
        return self._image_down

    @property
    def image(self):
        """Return the current image based on button state."""
        if self.is_pressed:
            return self.image_down
        else:
            return self.image_up

    def handle_event(self, event):
        """Handle mouse events to change button state."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.is_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.is_pressed:
                self.is_pressed = False
                if self.rect.collidepoint(event.pos):
                    return self.name  # Return the button name when clicked
                
        return None
    
    def update(self, x, y):
        """Update the button's visual state."""
        # Update image based on button press state
        #self.image = self.image  # This just triggers the lazy loading based on current state
        self.rect.topleft = (x, y)  # Update the button's position


class Cursor(object):
    def __init__(self):
        self.default_image = pygame.image.load(ResourcePath('assets/zombie_hand.png').path).convert_alpha()
        self.attack_image = pygame.image.load(ResourcePath('assets/crosshair.png').path).convert_alpha()
        self.image = self.default_image
        self.rect = self.image.get_rect(center=(0,0))
        pygame.mouse.set_visible(False)
    
    def update(self, game_ui):
        self.image = self.default_image
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.topleft = (mouse_x, mouse_y)        
        for zombie in game_ui.description_panel.zombie_sprite_group:
            if zombie.rect.collidepoint((mouse_x, mouse_y)):
                self.image = self.attack_image
                self.rect.center = (mouse_x, mouse_y)

    def draw(self):
        pygame.display.get_surface().blit(self.image, self.rect)