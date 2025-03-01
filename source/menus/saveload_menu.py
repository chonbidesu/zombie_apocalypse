# saveload_menu.py

import os
import pickle
import pygame

from core.settings import *
from ui import Button
from data import SaveLoadPath

class SaveLoadMenu:
    """Create a save/load menu for the game."""
    def __init__(self, game, mode):
        self.game = game
        self.mode = mode
        self.header = self.create_header()
        self.slots = self.create_slots()
        self.back_button = self._create_back_button()

    def create_header(self):
        """Create the header for the save/load menu."""
        header_text = "Save Game" if self.mode == "save" else "Load Game"
        header = font_xl.render(header_text, True, WHITE)
        header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
        return header, header_rect
    
    def create_slots(self):
        group = pygame.sprite.Group()
        for i in range(3):
            slot = SaveSlot(i)
            group.add(slot)
        return group
    
    def _create_back_button(self):
        button = Button("menu_back", 116, 51)
        x = SCREEN_WIDTH // 2 - 58
        y = SCREEN_HEIGHT * 5 // 6
        button.update(x, y)   
        group = pygame.sprite.GroupSingle()
        group.add(button)
        return group

    def draw(self, screen):
        if self.game.title_screen:
            panel_width, panel_height = SCREEN_WIDTH - 60, SCREEN_HEIGHT - 60
            panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surface.fill(DARK_GREEN)
            panel_surface.set_alpha(150)
            panel_rect = panel_surface.get_rect(topleft=(30, 30))
            screen.blit(panel_surface, panel_rect)
        else:
            screen.fill(DARK_GREEN)

        screen.blit(*self.header)
        for slot in self.slots:
            slot.update_image()
        self.slots.draw(screen)
        self.back_button.draw(screen)


class SaveSlot(pygame.sprite.Sprite):
    """A save slot sprite for saving/loading saved game states."""
    def __init__(self, index):
        super().__init__()
        self.index = index
        self.image = pygame.Surface((SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self._set_position()
        self.update_image()

    def _set_position(self):
        width = SCREEN_WIDTH * 5 // 6
        height = SCREEN_HEIGHT // 6
        x = (SCREEN_WIDTH // 2) - (width // 2)
        y = ((SCREEN_HEIGHT // 2) - (height * 3 // 2)) + self.index * height
        self.rect.topleft = (x, y)

    def _load_save_metadata(self, save_path):
        """Loads the metadata from save files."""
        try:
            with open(save_path, "rb") as f:
                save_data = pickle.load(f)

                # Check if the save has a version number
                saved_version = save_data.game_version if hasattr(save_data, "game_version") else "Unknown"
                if saved_version != GAME_VERSION:
                    return "<<incompatible save>>"
                
                # Extract player name from save file
                player_data = save_data.player_data
                if player_data.get("is_human"):
                    return f"{player_data.get('first_name', 'Unknown')} {player_data.get('last_name', '')}"
                else:
                    return f"{player_data.get('zombie_adjective', 'Unknown')} {player_data.get('first_name', '')}"

        except (FileNotFoundError, pickle.UnpicklingError, KeyError, AttributeError, ModuleNotFoundError):
            return "<<corrupted save>>"

    def update_image(self):
        # Clear the image
        self.image.fill((0, 0, 0, 0))

        # Draw a white box
        white_box_rect = self.image.get_rect().inflate(-20, -20)
        pygame.draw.rect(self.image, (255, 255, 255), white_box_rect)

        # Draw a black border
        black_border_rect = white_box_rect.inflate (-20, -20)
        pygame.draw.rect(self.image, (0, 0, 0), black_border_rect, 10)

        # Determine the slot label and player name
        slot_label = f"SLOT {chr(65 + self.index)}"
        save_path = SaveLoadPath(f"save_{self.index}.pkl").path

        if os.path.exists(save_path):
            self.player_name = self._load_save_metadata(save_path)

        else:
            self.player_name = "<<empty>>"

        # Render the text
        text = font_large.render(f"{slot_label}: {self.player_name}", True, BLACK)
        text_rect = text.get_rect(center=black_border_rect.center)

        # Blit the text
        self.image.blit(text, text_rect)





