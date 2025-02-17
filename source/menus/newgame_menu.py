# newgame_menu.py

import pygame

from settings import *
from data import Action, SKILLS, SkillType, SkillCategory, OCCUPATIONS, OccupationCategory
from ui import Button, WrapText


class NewGameMenu:
    """A menu for creating a character and starting a new game."""
    def __init__(self, game):
        self.game = game
        self.occupation_spacing = 35
        self.margin = 75
        self.selected_portrait = None
        self.selected_occupation = None

        self.buttons = self._create_buttons()
        self.text_inputs = self._create_text_inputs()
        self.occupation_slots = self._create_occupation_slots()
        self.portrait_sprites = self._create_portrait_options()

        # Define columns
        self.column_width = SCREEN_WIDTH // 3
        self.column_x_positions = [self.margin, self.column_width + self.margin, 2 * self.column_width + self.margin]        
        self.category_columns = {
            OccupationCategory.CIVILIAN: 0,
            OccupationCategory.MILITARY: 1,
            OccupationCategory.SCIENCE: 2,
            OccupationCategory.ZOMBIE: 1,
        }                

    def _create_buttons(self):
        """Create Start and Back buttons."""
        start_button = Button('menu_start', 150, 50)
        back_button = Button('menu_back', 150, 50)

        start_button.update(SCREEN_WIDTH - 330, SCREEN_HEIGHT - 100)
        back_button.update(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 100)

        button_group = pygame.sprite.Group()
        button_group.add(start_button)
        button_group.add(back_button)
        return button_group
    
    def _create_text_inputs(self):
        """Create text input fields."""
        return {
            "first_name": TextInputBox(100, 200, 200, 30, "First Name"),
            "last_name": TextInputBox(100, 250, 200, 30, "Last Name"),
            "dead_word": TextInputBox(100, 300, 200, 30, "Dead Word")            
        }
    
    def _create_occupation_slots(self):
        """Create selectable occupation slots."""
        occupation_slots = pygame.sprite.Group()
        y_offset = SCREEN_HEIGHT // 2
        for occupation in OCCUPATIONS:
            occupation_slot = OccupationSlot(occupation, 100, y_offset, 300)
            occupation_slots.add(occupation_slot)
            y_offset += 50
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
        for input_box in self.text_inputs.values():
            input_box.draw(screen)
        
        # Draw occupation slots
        self.occupation_slots.draw(screen)
        
        # Draw buttons
        self.buttons.draw(screen)
    
    def start_game(self):
        """Start the game with the chosen settings."""
        first_name = self.text_inputs["first_name"].text
        last_name = self.text_inputs["last_name"].text
        dead_word = self.text_inputs["dead_word"].text
        occupation = self.selected_occupation
        
        self.game.initialize_new_character(first_name, last_name, dead_word, occupation)
        self.game.act(Action.NEW_GAME)


class PortraitSprite(pygame.sprite.Sprite):
    """A selectable portrait sprite."""
    def __init__(self, image_path, x, y):
        super().__init__()
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

    def draw(self, screen):
        """Draw the text box with text."""
        colour = WHITE if self.active else LIGHT_GRAY
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
        border_color = WHITE if self.selected else (50, 50, 50)

        pygame.draw.rect(self.image, border_color, (0, 0, self.width, self.height), 2)
        text = font_large.render(OCCUPATIONS[self.occupation].occupation, True, WHITE)
        self.image.blit(text, (10, 10))
