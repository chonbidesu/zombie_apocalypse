from settings import *
from ui.status_panel import StatusPanel
from ui.chat_panel import ChatPanel
from ui.actions_panel import ActionsPanel 
from ui.inventory_panel import InventoryPanel
from ui.description_panel import DescriptionPanel
from ui.viewport import Viewport
from ui.utils import ActionProgress, DayCycleManager, DeathScreen, WrapText
from ui.effects import ScreenTransition
from ui.widgets import Cursor, Button
from ui.map import Map


class DrawUI:
    """Manages all UI elements and delegates rendering to subcomponents."""
    def __init__(self, game, screen, portrait):
        self.screen = screen
        self.viewport = Viewport(game, screen)
        self.actions_panel = ActionsPanel(game, screen)
        self.status_panel = StatusPanel(game, screen, portrait)
        self.chat_panel = ChatPanel(screen)
        self.inventory_panel = InventoryPanel(game, screen)
        self.description_panel = DescriptionPanel(game, screen)
        self.action_progress = ActionProgress(game, screen)
        self.screen_transition = ScreenTransition(screen, self.draw, self.update)
        self.day_cycle = DayCycleManager(game)        
        self.map = Map(game, screen)
        self.death_screen = DeathScreen(game, screen)

    def draw(self, chat_history):
        self.screen.fill(DARK_GREEN)
        self.viewport.draw()
        self.actions_panel.draw()
        self.status_panel.draw()
        self.chat_panel.draw(chat_history)
        self.inventory_panel.draw()
        self.description_panel.draw()
        self.action_progress.draw()
        self.day_cycle.draw()

    def update(self):
        self.viewport.update()
        self.actions_panel.update()
        self.description_panel.update()
        self.day_cycle.update()
