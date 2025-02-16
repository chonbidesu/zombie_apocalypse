
# utils.py

import pygame
import sys

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

    def start(self, message, target_function, *args, duration=750, **kwargs):
        """Start displaying an action progress message for a set duration."""
        self.active_message = message
        self.start_ticks = pygame.time.get_ticks()
        self.duration = duration
        self.target_function = target_function
        self.args = args
        self.kwargs = kwargs

    def draw(self):
        """Draw the action progress message if it's active."""
        if self.active_message:
            elapsed = pygame.time.get_ticks() - self.start_ticks # Time elapsed in ms
            dots = "." * ((elapsed // 250) % 4) # Animated "..." effect every 500ms
            text = font_xl.render(f"{self.active_message}{dots}", True, WHITE)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text, text_rect)

            # Stop displaying once duration ends
            if elapsed > self.duration:
                self.active_message = None
                if self.target_function:
                    result = self.target_function(*self.args, **self.kwargs)
                    if result:
                        self.game.event_handler.handle_feedback(result.message)
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
    

class DayCycleManager:
    """Manages the transition from daytime to nighttime."""
    def __init__(self, game):
        self.game = game
        self.night_overlay_alpha = 0 # Start the day with a transparent overlay
        self.is_night = False

        pygame.mixer.init() # Initialize the sound mixer
        pygame.mixer.music.load(ResourcePath("assets/music/road_runner.mp3").path)

    def update(self):
        """Updates the environment based on the time of day."""
        current_time = self.game.game_ui.description_panel.clock.time_in_minutes
        # Transition from day to night (9:00 AM → Midnight)
        if 1260 <= current_time < 1440:
            self.apply_night_overlay(current_time)
        
        # Trigger night cycle when midnight hits
        if current_time == 0 and not self.is_night:
            self.is_night = True
            self.start_night()

    def apply_night_overlay(self, current_time):
        """
        Gradually darkens the setting as night approaches.
        The overlay becomes fully dark blue by midnight.
        """
        start_time = 1260   # Start of dusk
        end_time = 1440    # Full night
        max_alpha = 115  # Maximum transparency value for night effect

        # Calculate transition progress (0.0 → 1.0)
        progress = min(1, max(0, (current_time - start_time) / (end_time - start_time)))

        # Set overlay transparency
        self.night_overlay_alpha = int(progress * max_alpha)

    def draw(self):
        """Draws the transparent night overlay onto the screen."""
        overlay = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
        night_colour = (0, 0, 139, self.night_overlay_alpha)  # Dark blue with transparency
        overlay.fill(night_colour)
        self.game.screen.blit(overlay, (0, 0))

    def start_night(self):
        """Trigger night transition when 12:00 PM hits."""
        self.game.game_ui.screen_transition.circle_wipe(self.process_night_cycle, self.game.chat_history)

    def process_night_cycle(self):
        """Process 8 hours of NPC actions."""
        for _ in range(8 * 60 * 1000 // ACTION_INTERVAL): # Calculate number of NPC actions in 8 hours
            self.game.state.npcs.gain_ap()
            self.game.state.npcs.take_action()
            self.game.ticker += 1  # Track time progression

        self.start_new_day()
        self.game.game_ui.description_panel.clock.time_in_minutes = 8 * 60  # Reset to 8:00 AM

    def start_new_day(self):
        """End the night cycle and start a new day."""
        self.night_overlay_alpha = 0 # Make night overlay transparent
        pygame.mixer.music.play(-1)
        print("You wake up at dawn...")


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

    def handle_events(self, events):
        """Handle restart or quit actions"""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:  # Restart game logic
                    self.restart = True
                elif event.key == pygame.K_n:  # Quit game
                    pygame.quit()
                    sys.exit()