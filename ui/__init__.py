from settings import *
from ui.panels import StatusPanel, ChatPanel, ActionsPanel, InventoryPanel, DescriptionPanel
from ui.viewport import Viewport
from ui.utils import ActionProgress

class DrawUI:
    """Manages all UI elements and delegates rendering to subcomponents."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.viewport = Viewport(game, screen)
        self.actions_panel = ActionsPanel(game, screen)
        self.status_panel = StatusPanel(game, screen)
        self.chat_panel = ChatPanel(screen)
        self.inventory_panel = InventoryPanel(game, screen)
        self.description_panel = DescriptionPanel(game, screen)
        self.action_progress = ActionProgress(screen)

    def draw(self, chat_history):
        self.viewport.update()
        self.viewport.draw()
        self.actions_panel.update()
        self.actions_panel.draw()
        self.status_panel.draw()
        self.chat_panel.draw(chat_history)
        self.inventory_panel.draw()
        self.description_panel.draw()
        self.action_progress.draw()