# __init__.py

from menus.context_menu import ContextMenu
from menus.pause_menu import PauseMenu

class GameMenu:
    def __init__(self):
        self.pause_menu = PauseMenu()

    def draw_pause_menu(self):
        self.pause_menu.draw()