import pygame
from settings import *
from ui.utils import wrap_text

class StatusPanel:
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.hp_bar = pygame.image.load("assets/hp_bar.png").convert_alpha()
        self.player_frame = pygame.image.load("assets/player_frame.png").convert_alpha()

    def draw(self):
        status_x, status_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT * 25 // 32 + 10
        status_width, status_height = SCREEN_WIDTH // 4 - 10, SCREEN_HEIGHT * 31 // 160
        status_panel = pygame.Surface((status_width, status_height), pygame.SRCALPHA)

        # Draw HP bar
        max_hp = self.game.player.max_hp
        current_hp = self.game.player.hp
        hp_ratio = max(current_hp / max_hp, 0)

        pygame.draw.rect(status_panel, (255, 0, 0), (0, status_height - 20, status_width, 20))
        pygame.draw.rect(status_panel, (0, 255, 0), (0, status_height - 20, status_width * hp_ratio, 20))

        # Blit to screen
        self.screen.blit(status_panel, (status_x, status_y))

class ChatPanel:
    def __init__(self, screen):
        self.screen = screen
        self.chat_image = pygame.image.load("assets/chat_panel.png").convert_alpha()

    def draw(self, chat_history):
        chat_x, chat_y = 10, SCREEN_HEIGHT * 13 // 20 + 30
        chat_width, chat_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT * 3 // 10
        self.screen.blit(pygame.transform.scale(self.chat_image, (chat_width, chat_height)), (chat_x, chat_y))

        # Render chat messages
        wrapped_history = []
        for message in chat_history:
            wrapped_history.extend(wrap_text(f">> {message}", font_chat, chat_width - 50))

        y_offset = chat_y + chat_height - 40
        for message in reversed(wrapped_history[-10:]):  # Show last 10 messages
            text = font_chat.render(message, True, WHITE)
            self.screen.blit(text, (chat_x + 30, y_offset))
            y_offset -= font_chat.get_linesize()
