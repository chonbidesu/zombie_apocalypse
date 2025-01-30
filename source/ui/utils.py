
# utils.py

import pygame
from settings import *

class WrapText:
    """Wrap the text to fit inside a given width."""
    def __init__(self, text, font, max_width):
        self.font = font
        self.max_width = max_width
        self.lines = []

        self.wrap_text(text)

    def wrap_text(self, text):
        current_line = ""        
        words = text.split(" ")        
        for word in words:
            # Check if adding the word exceeds the width
            test_line = current_line + (word if current_line == "" else " " + word)
            test_width, _ = self.font.size(test_line)

            if test_width <= self.max_width:
                current_line = test_line  # Add the word to the current line
            else:
                if current_line != "":
                    self.lines.append(current_line)  # Append the current line if it's not empty
                current_line = word  # Start a new line with the current word

        if current_line != "":  # Append the last line if it has any content
            self.lines.append(current_line)


class ActionProgress:
    """Display a 'Searching...' message with incrementing dots, or a similar message."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.active_message = None
        self.start_ticks = 0
        self.duration = 0
        self.target_function = None
        self.clock = pygame.time.Clock()

    def start(self, message, target_function, duration=1.5):
        """Start displaying an action progress message for a set duration."""
        self.active_message = message
        self.start_ticks = pygame.time.get_ticks()
        self.duration = duration * 1000
        self.target_function = target_function

    def draw(self):
        """Draw the action progress message if it's active."""
        if self.active_message:
            elapsed = pygame.time.get_ticks() - self.start_ticks # Time elapsed in ms
            dots = "." * ((elapsed // 500) % 4) # Animated "..." effect every 500ms
            text = font_xl.render(f"{self.active_message}{dots}", True, WHITE)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

            # Stop displaying once duration ends
            if elapsed > self.duration:
                self.active_message = None
                if self.target_function:
                    result, item_used = self.target_function()
                    self.game.chat_history.append(result)
                    if item_used:
                        item_used.kill()
                    self.target_function = None


class SpriteSheet():
    def __init__(self, image):
        self.sheet = image

    def get_image(self, frame, width, height, scale, colour):
        image = pygame.Surface((width, height)).convert_alpha()
        image.blit(self.sheet, (0, 0), ((frame * width), 0, width, height))
        image = pygame.transform.scale(image, (width * scale, height * scale))
        image.set_colorkey(colour)

        return image
    
class DeathScreen():
    """Display a death screen with restart options."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.overlay.set_alpha(150)
        self.overlay.fill(BLACK)
        self.restart = False

        # Render DEATH message and restart option
        # Render "YOU DIED" and "RESTART? Y / N"
        self.text_you_died = font_xxl.render("YOU DIED", True, (255, 0, 0))
        self.text_restart = font_xl.render("RESTART? Y / N", True, WHITE)

        # Get text positions
        self.you_died_rect = self.text_you_died.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
        self.restart_rect = self.text_restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))        
        
    def draw(self):
        """Blit overlay and text onto the screen"""
        self.screen.blit(self.overlay, (0, 0))
        self.screen.blit(self.text_you_died, self.you_died_rect)
        self.screen.blit(self.text_restart, self.restart_rect)

        pygame.display.flip()  # Update display

        # Handle restart or quit actions
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:  # Restart game logic
                        self.restart = True
                    elif event.key == pygame.K_n:  # Quit game
                        pygame.quit()
                        sys.exit()