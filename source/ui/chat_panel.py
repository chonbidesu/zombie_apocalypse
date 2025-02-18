# chat_panel.py

from settings import *
from ui.utils import WrapText
from data import ResourcePath


class ChatPanel:
    def __init__(self, screen):
        self.screen = screen
        self.original_image = pygame.image.load(ResourcePath("panels/chat_panel.png").path).convert_alpha()
        self.width, self.height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT * 3 // 10
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))

    def draw(self, chat_history):
        x, y = 10, SCREEN_HEIGHT * 13 // 20 + 30
        self.screen.blit(self.image, (x, y))

        # Render chat messages
        wrapped_history = []
        for message in chat_history:
            wrapped_message = WrapText(f">> {message}", font_chat, self.width - 50)
            wrapped_history.extend(wrapped_message.lines)

        y_offset = y + self.height - 40
        for message in reversed(wrapped_history[-10:]):  # Show last 10 messages
            text = font_chat.render(message, True, WHITE)
            self.screen.blit(text, (x + 30, y_offset))
            y_offset -= font_chat.get_linesize()