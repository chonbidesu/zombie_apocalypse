# button.py

import pygame
import time

from settings import *
from data import ResourcePath, ItemType

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
            self._image = pygame.image.load(ResourcePath(f"buttons/{self.name}.png").path).convert_alpha()
            self._image = pygame.transform.scale(self._image, (width, height))  # Scale when loading

    @property
    def image_up(self):
        """Lazy load the 'up' image when first accessed."""
        if self._image_up is None:
            self._image_up = pygame.image.load(ResourcePath(f"buttons/{self.name}_up.png").path).convert_alpha()
            self._image_up = pygame.transform.scale(self._image_up, (self.width, self.height))  # Scale when loading
        return self._image_up

    @property
    def image_down(self):
        """Lazy load the 'down' image when first accessed."""
        if self._image_down is None:
            self._image_down = pygame.image.load(ResourcePath(f"buttons/{self.name}_down.png").path).convert_alpha()
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
    def __init__(self, game):
        self.game = game

        # Create the cursors
        self.default_cursor = self._create_cursor(ResourcePath("cursor/zombie_hand.png").path)
        self.punch_cursor = self._create_cursor(ResourcePath("cursor/zombie_fist.png").path)
        self.attack_cursor = self._create_cursor(ResourcePath("cursor/crosshair.png").path)
        self.speak_cursor = self._create_cursor(ResourcePath("cursor/mouth.png").path)
        self.heal_cursor = self._create_cursor(ResourcePath("items/first_aid_kit.png").path)
        self.extract_cursor = self._create_cursor(ResourcePath("items/dna_extractor.png").path)
        self.revivify_cursor = self._create_cursor(ResourcePath("items/syringe.png").path)

        self.set_default()

    def _create_cursor(self, image_path):
        image = pygame.image.load(image_path).convert_alpha()
        image = pygame.transform.scale(image, (32, 32))
        cursor = pygame.cursors.Cursor((0, 0), image)
        return cursor

    def update(self):
        game_ui = self.game.game_ui
        player = self.game.state.player
        player_sprite = self.game.game_ui.status_panel.player_sprite
        mouse_x, mouse_y = pygame.mouse.get_pos()

        cursor_changed = False    

        # Check collisions with zombie sprites
        for zombie in game_ui.description_panel.zombie_sprite_group:
            if zombie.rect.collidepoint((mouse_x, mouse_y)):
                if player.weapon:
                    if player.weapon.type == ItemType.DNA_EXTRACTOR:
                        self.set_extract()
                        cursor_changed = True
                        break
                    elif player.weapon.type == ItemType.SYRINGE:
                        self.set_revivify()
                        cursor_changed = True
                        break
                self.set_attack()
                cursor_changed = True
                break

        for human in game_ui.description_panel.human_sprite_group:
            if human.rect.collidepoint((mouse_x, mouse_y)):
                if player.weapon:
                    if player.weapon.type == ItemType.FIRST_AID_KIT:
                        self.set_heal()
                        cursor_changed = True
                        break

        if player_sprite.rect.collidepoint((mouse_x, mouse_y)):
            if player.weapon:
                if player.weapon.type == ItemType.FIRST_AID_KIT:
                    self.set_heal()
                    cursor_changed = True

        if not cursor_changed:
            self.set_default()

    def set_default(self):
        pygame.mouse.set_cursor(self.default_cursor)

    def set_attack(self):
        pygame.mouse.set_cursor(self.attack_cursor)

    def set_extract(self):
        pygame.mouse.set_cursor(self.extract_cursor)

    def set_revivify(self):
        pygame.mouse.set_cursor(self.revivify_cursor)

    def set_heal(self):
        pygame.mouse.set_cursor(self.heal_cursor)

class ClockHUD:
    """Displays and updates the in-game clock."""
    def __init__(self, game, start_time=480): # Default start time 8:00 AM (8 * 60 minutes)
        self.game = game
        self.time_in_minutes = start_time
        self.last_update = time.time()

    def update(self):
        """Update the clock every second in real time."""
        current_time = time.time()
        if current_time - self.last_update >= 3.125:  # 3.125 seconds = 10 in-game minute = full day cycle in 5 minutes
            self.time_in_minutes += 10
            self.last_update = current_time

        # If it's 12:00 PM, start the night cycle
        if self.time_in_minutes >= 24 * 60:  # 24 * 60 = 1440 minutes = 12:00 PM
            self.game.game_ui.day_cycle.start_night()

    def draw(self, screen, x, y):
        """Draw the clock on screen."""
        hours = (self.time_in_minutes // 60) % 24  # Convert minutes to hours
        minutes = self.time_in_minutes % 60
        am_pm = "AM" if hours < 12 else "PM"
        display_hours = hours if hours <= 12 else hours - 12  # Convert to 12-hour format

        time_str = f"{display_hours:02}:{minutes:02} {am_pm}"
        
        # Change colour to red if night is approaching
        colour = (255, 0, 0) if self.time_in_minutes >= 21 * 60 else (255, 255, 255)

        time_surface = font_xl.render(time_str, True, colour)
        time_shadow = font_xl.render(time_str, True, BLACK)
        screen.blit(time_shadow, (x + 1, y + 1))  # Drop shadow
        screen.blit(time_surface, (x, y))  # Display in centre of setting image
