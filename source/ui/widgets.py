# button.py

import pygame

from settings import *

class Button(pygame.sprite.Sprite):
    """A button that changes images on mouse events."""
    def __init__(self, name, width, height, is_pressable=False):
        super().__init__()
        self.name = name
        self.width = width
        self.height = height
        self.is_pressable = is_pressable
        self.is_pressed = False
        self._image_up = None  # Private attributes for lazy-loaded images
        self._image_down = None
        self.rect = pygame.Rect(0, 0, width, height)  # Initial rect size (scale later when image is loaded)

        if not is_pressable:
            self._image = pygame.image.load(ResourcePath(f"assets/buttons/{self.name}.png").path).convert_alpha()
            self._image = pygame.transform.scale(self._image, (width, height))  # Scale when loading

    @property
    def image_up(self):
        """Lazy load the 'up' image when first accessed."""
        if self._image_up is None:
            self._image_up = pygame.image.load(ResourcePath(f"assets/buttons/{self.name}_up.png").path).convert_alpha()
            self._image_up = pygame.transform.scale(self._image_up, (self.width, self.height))  # Scale when loading
        return self._image_up

    @property
    def image_down(self):
        """Lazy load the 'down' image when first accessed."""
        if self._image_down is None:
            self._image_down = pygame.image.load(ResourcePath(f"assets/buttons/{self.name}_down.png").path).convert_alpha()
            self._image_down = pygame.transform.scale(self._image_down, (self.width, self.height))  # Scale when loading
        return self._image_down

    @property
    def image(self):
        """Return the current image based on button state."""
        if self.is_pressable:
            return self.image_down if self.is_pressed else self.image_up
        else:
            return self._image

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
        # Create the cursors
        self.default_cursor = self._create_cursor(ResourcePath("assets/zombie_hand.png").path)
        self.attack_cursor = self._create_cursor(ResourcePath("assets/crosshair.png").path)

        pygame.mouse.set_cursor(self.default_cursor)

    def _create_cursor(self, image_path):
        image = pygame.image.load(image_path).convert_alpha()
        cursor = pygame.cursors.Cursor((0, 0), image)
        return cursor

    def update(self, game_ui):
        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Check collisions with zombie sprites
        cursor_changed = False    
        for zombie in game_ui.description_panel.zombie_sprite_group:
            if zombie.rect.collidepoint((mouse_x, mouse_y)):
                pygame.mouse.set_cursor(self.attack_cursor)
                cursor_changed = True
                break

        if not cursor_changed:
            pygame.mouse.set_cursor(self.default_cursor)