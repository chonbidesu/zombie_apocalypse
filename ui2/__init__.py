from settings import *
from ui.panels import StatusPanel, ChatPanel
from ui.viewport import Viewport
from ui.buttons import ButtonManager

class DrawUI:
    """Manages all UI elements and delegates rendering to subcomponents."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.viewport = Viewport(game, screen)
        self.status_panel = StatusPanel(game, screen)
        self.chat_panel = ChatPanel(screen)
        self.button_manager = ButtonManager()

    def draw(self, chat_history):
        self.viewport.draw()
        self.status_panel.draw()
        self.chat_panel.draw(chat_history)
        self.button_manager.button_group.draw(self.screen)