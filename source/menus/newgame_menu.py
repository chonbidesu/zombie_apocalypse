# newgame_menu.py

import pygame

from settings import *
from data import Action, SKILLS, SkillType, SkillCategory, OCCUPATIONS, Occupation, OccupationCategory
from ui import Button, WrapText
from characters import CharacterName, Character


class NewGameMenu:
    """A menu for creating a character and starting a new game."""
    def __init__(self, game):
        self.game = game
        self.occupation_spacing = 50
        self.margin = 75
        self.selected_portrait = None
        self.selected_occupation = None

        # Define columns
        self.column_width = SCREEN_WIDTH // 3
        self.column_x_positions = [self.margin, self.column_width + self.margin, 2 * self.column_width + self.margin]        
        self.category_columns = {
            OccupationCategory.CIVILIAN: 0,
            OccupationCategory.MILITARY: 1,
            OccupationCategory.SCIENCE: 2,
            OccupationCategory.ZOMBIE: 1,
        } 

        self.buttons = self._create_buttons()
        self.text_inputs = self._create_text_inputs()
        self.occupation_slots = self._create_occupation_slots()
        self.portrait_sprites = self._create_portrait_options()               

    def _create_buttons(self):
        """Create Start and Back buttons."""
        start_button = Button('menu_start', 150, 50)
        back_button = Button('menu_back', 150, 50)

        start_button.update(SCREEN_WIDTH - 380, SCREEN_HEIGHT - 100)
        back_button.update(SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100)

        button_group = pygame.sprite.Group()
        button_group.add(start_button)
        button_group.add(back_button)
        return button_group
    
    def _create_text_inputs(self):
        """Create text input fields."""
        x_offset = SCREEN_WIDTH // 2 - 350
        y = 300
        width, height = 200, 30
        return {
            "first_name": TextInputBox(x_offset, y, width, height, "First Name"),
            "last_name": TextInputBox(x_offset + 250, y, width, height, "Last Name"),
            "dead_word": TextInputBox(x_offset + 500, y, width, height, "Dead Word")            
        }
    
    def _create_occupation_slots(self):
        """Create selectable occupation slots."""
        occupation_slots = pygame.sprite.Group()
        base_y = SCREEN_HEIGHT // 2 + 30
        width = self.column_width - 120

        for category in OccupationCategory:
            column = self.category_columns.get(category, 0)
            x_pos = self.column_x_positions[column]
            y_offset = base_y

            # Handle Zombie occupation separately to center it in middle column
            if category == OccupationCategory.ZOMBIE:
                y_offset += SCREEN_HEIGHT // 4

            for occupation in OCCUPATIONS:
                properties = OCCUPATIONS[occupation]

                if properties.occupation_category == category:
                    occupation_slot = OccupationSlot(occupation, x_pos, y_offset, width)
                    occupation_slots.add(occupation_slot)
                    y_offset += self.occupation_spacing
        return occupation_slots
    
    def _create_portrait_options(self):
        """Create selectable portrait areas."""
        portraits = pygame.sprite.Group()
        portrait_paths = [
        ResourcePath("assets/female1_sprite_sheet.png").path,
        ResourcePath("assets/male1_sprite_sheet.png").path
    ]

        for i, path in enumerate(portrait_paths):
            portrait = PortraitSprite(path, SCREEN_WIDTH // 2 - 200 + (i * 200), 150)
            portraits.add(portrait)

        return portraits
    
    def draw(self, screen):
        """Draw the new game menu."""
        screen.fill(DARK_GREEN)
        
        # Draw header
        title_text = font_xl.render("Create Character", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 75))
        screen.blit(title_text, title_rect)
        
        # Draw portraits
        self.portrait_sprites.draw(screen)
        for i, rect in enumerate(self.portrait_sprites):
            pygame.draw.rect(screen, BLACK, rect, 4 if self.selected_portrait == i else 1)
        
        # Draw text inputs
        dead_word_description = "Describe your corpse"
        dead_word_text = font_large.render(dead_word_description, True, WHITE)
        dead_word_rect = dead_word_text.get_rect(topleft=(SCREEN_WIDTH // 2 + 150, 330))
        screen.blit(dead_word_text, dead_word_rect)
        for input_box in self.text_inputs.values():
            input_box.draw(screen)
        
        # Initialize y-offset for each column
        base_y = SCREEN_HEIGHT // 2

        # Draw occupation categories
        for category in OccupationCategory:

            column = self.category_columns.get(category, 0)  # Default to column 0 if not found
            x_pos = self.column_x_positions[column]
            y_offset = base_y
            
            # Handle Zombie occupation separately to center it in the middle column
            if category == OccupationCategory.ZOMBIE:
                y_offset += SCREEN_HEIGHT // 4  # Move to second row of middle column

            # Draw category title
            category_text = font_large.render(category.name, True, (200, 200, 0))
            screen.blit(category_text, (x_pos, y_offset))        

        # Draw occupation slots
        self.occupation_slots.update(self.selected_occupation)
        self.occupation_slots.draw(screen)
        
        # Draw buttons
        self.buttons.draw(screen)

        # Draw info panel if occupation is selected
        if self.selected_occupation:
            self._draw_info_panel(screen)

        # Draw warning message (if active)
        if hasattr(self, "warning_lines") and pygame.time.get_ticks() < self.warning_timer:
            y_position = SCREEN_HEIGHT * 3 // 4  # Start position for warning text
            for line in self.warning_lines:
                warning_text = font_large.render(line, True, RED)
                screen.blit(warning_text, (SCREEN_WIDTH * 2 // 3, y_position))
                y_position += font_large.get_height()  # Move to next line            

    def _draw_info_panel(self, screen):
        """Draws the information panel for the selected skill."""
        x, y = 50, SCREEN_HEIGHT * 3 // 4
        width, height = SCREEN_WIDTH // 3, SCREEN_HEIGHT // 4 - 40

        # Draw border
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)

        # Draw skill name
        properties = OCCUPATIONS[self.selected_occupation]
        occupation_name = font_large.render(properties.occupation, True, WHITE)
        occupation_name_width = occupation_name.get_width()
        screen.blit(occupation_name, (x + width // 2 - occupation_name_width // 2, y + 10))

        # Draw skill description
        wrapped_description = WrapText(properties.description, font_large, width - 20)
        y_offset = y + 50
        for line in wrapped_description.lines:
            text_surface = font_large.render(line, True, WHITE)
            screen.blit(text_surface, (x + 10, y_offset))
            y_offset += 20

    def cycle_text_input(self):
        """Cycle to the next text input box."""
        keys = list(self.text_inputs.keys())  # Get the keys in order
        active_index = None

        # Find the currently active text input
        for i, key in enumerate(keys):
            if self.text_inputs[key].active:
                active_index = i
                break

        # Deactivate current and activate the next input
        if active_index is not None:
            self.text_inputs[keys[active_index]].active = False  # Deactivate current
            next_index = (active_index + 1) % len(keys)  # Get the next index (loops back)
            self.text_inputs[keys[next_index]].active = True  # Activate next            

    def display_warning(self, message, duration=3):
        """Display a temporary warning message for validation errors."""
        wrapped_text = WrapText(message, font_large, 300).lines
        self.warning_lines = wrapped_text
        self.warning_timer = pygame.time.get_ticks() + (duration * 1000)  # Expiration time

    def start_game(self):
        """Start the game with the chosen settings."""
        first_name = self.text_inputs["first_name"].text
        last_name = self.text_inputs["last_name"].text
        dead_word = self.text_inputs["dead_word"].text
        portrait_index = self.selected_portrait
        occupation = self.selected_occupation

        # Validate user input
        if not first_name or not last_name or not dead_word:
            self.display_warning("Please enter a first and last name, and an adjective that describes your corpse.")
            return  
        if occupation is None:
            self.display_warning("Please select an occupation.")
            return
        if portrait_index is None:
            self.display_warning("Please select a player portrait.")
            return
        
        portrait = list(self.portrait_sprites)[portrait_index]
        character_name = CharacterName(first_name, last_name, dead_word)
        is_human = False if occupation == Occupation.CORPSE else True

        player = Character(self.game, character_name, occupation, 50, 50, is_human)
        
        # Disable menus and initialize game
        self.game.title_screen = False
        self.game.newgame_menu = False
        self.game.initialize_game(player, portrait.portrait_path)

class PortraitSprite(pygame.sprite.Sprite):
    """A selectable portrait sprite."""
    def __init__(self, image_path, x, y):
        super().__init__()
        self.portrait_path = image_path
        self.sprite_sheet = pygame.image.load(image_path).convert_alpha()

        # Extract first frame (assuming sprite sheet is horizontal)
        frame_width, frame_height = 66, 66
        original_image = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        original_image.blit(self.sprite_sheet, (0, 0), (0, 0, frame_width, frame_height))

        self.image = pygame.transform.scale(original_image, (frame_width * 2, frame_height * 2))

        # Create a rect for positioning
        self.rect = self.image.get_rect(topleft=(x, y))
        self.selected = False

    def update(self, selected):
        """Update the border to indicate selection."""
        self.selected = selected

    def draw(self, screen):
        """Draw the portrait with a selection border."""
        screen.blit(self.image, self.rect.topleft)
        if self.selected:
            pygame.draw.rect(screen, RED, self.rect.inflate(4, 4), 2)  # Red border when selected


class TextInputBox:
    """A text input box for entering character details."""
    def __init__(self, x, y, width, height, placeholder):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.active = False
        self.max_length = 10

    def draw(self, screen):
        """Draw the text box with text."""
        colour = WHITE if self.active else MED_GRAY
        pygame.draw.rect(screen, colour, self.rect, 2)
        
        text_surface = font_large.render(self.text if self.text else self.placeholder, True, WHITE)
        screen.blit(text_surface, (self.rect.x + 10, self.rect.y + 5))

class OccupationSlot(pygame.sprite.Sprite):
    """A selectable occupation slot."""
    def __init__(self, occupation, x, y, width):
        super().__init__()
        self.occupation = occupation
        self.width = width
        self.height = 40
        self.rect = pygame.Rect(x, y, width, self.height)
        self.image = pygame.Surface((width, self.height), pygame.SRCALPHA)
        self.selected = False

    def update(self, selected_occupation):
        """Update appearance based on selection."""
        self.selected = self.occupation == selected_occupation
        self.image.fill((0, 0, 0, 0))
        border_colour = WHITE if self.selected else DARK_GREEN

        pygame.draw.rect(self.image, border_colour, (0, 0, self.width, self.height), 2)
        text = font_large.render(OCCUPATIONS[self.occupation].occupation, True, WHITE)
        self.image.blit(text, (10, 10))
