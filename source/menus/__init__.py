# __init__.py

from menus.context_menu import ContextMenu
from menus.pause_menu import PauseMenu
from menus.saveload_menu import SaveLoadMenu
from menus.title_menu import TitleMenu, TitleAction
from menus.skills_menu import SkillsMenu

class GameMenu:
    def __init__(self, game):
        self.pause_menu = PauseMenu()
        self.save_menu = SaveLoadMenu("save")
        self.load_menu = SaveLoadMenu("load")
        self.title_menu = TitleMenu()
        self.title_action = TitleAction(game)
        self.skills_menu = SkillsMenu(game)