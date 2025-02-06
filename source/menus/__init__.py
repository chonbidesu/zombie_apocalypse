# __init__.py

from menus.context_menu import ContextMenu
from menus.pause_menu import PauseMenu
from menus.saveload_menu import SaveLoadMenu

class GameMenu:
    def __init__(self):
        self.pause_menu = PauseMenu()
        self.save_menu = SaveLoadMenu("save")
        self.load_menu = SaveLoadMenu("load")

    def draw_pause_menu(self):
        self.pause_menu.draw()