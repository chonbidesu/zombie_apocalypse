# saveload_menu.py

import os
import pickle
import pygame

from settings import *
from ui import Button

class SaveLoadMenu:
    """Create a save/load menu for the game."""
    def __init__(self, mode):
        self.mode = mode
        self.header = self.create_header()
        self.slots = self.create_slots()
        self.back_button = self._create_back_button()
        self.create_saves_folder()

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
    
    def create_saves_folder(self):
        """Create a folder to store save files."""
        if not os.path.exists("saves"):
            os.makedirs("saves")

    def _create_back_button(self):
        button = Button("menu_back", 116, 51)
        x = SCREEN_WIDTH // 2 - 58
        y = SCREEN_HEIGHT * 5 // 6
        button.update(x, y)   
        group = pygame.sprite.GroupSingle()
        group.add(button)
        return group

    def draw(self, screen):
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
        save_path = f"saves/save_{self.index}.pkl"
        if os.path.exists(save_path):
            with open(save_path, 'rb') as f:
                game_state = pickle.load(f)
                is_human = game_state.player_data["is_human"]
                if is_human:
                    self.player_name = f"{game_state.player_data["first_name"]} {game_state.player_data["last_name"]}"
                else:
                    self.player_name = f"{game_state.player_data["zombie_adjective"]} {game_state.player_data["first_name"]}"                   
        else:
            self.player_name = "<<empty>>"

        # Render the text
        text = font_large.render(f"{slot_label}: {self.player_name}", True, BLACK)
        text_rect = text.get_rect(center=black_border_rect.center)

        # Blit the text
        self.image.blit(text, text_rect)





