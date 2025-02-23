# system.py

from actions.base_command import ActionCommand


class Quit(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None)
        self.game = game

    def execute(self):
        self.game.quit_game()


class OpenSaveMenu(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None)
        self.game = game

    def execute(self):
        self.game.save_menu = True


class SaveGame(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game   

    def execute(self, target):
        self.game.save_game(target)


class OpenLoadMenu(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.load_menu = True


class LoadGame(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None)  
        self.game = game  

    def execute(self, target):
        self.game.load_game(target)


class OpenNewgameMenu(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.newgame_menu = True


class StartGame(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):    
        self.game.start_game()


class OpenSkillsMenu(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.skills_menu = True


class Back(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.newgame_menu = False
        self.game.save_menu = False
        self.game.load_menu = False
        self.game.skills_menu = False
        self.game.reading_map = False


class Pause(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        """Toggle game pause state."""
        if self.game.paused:
            self.game.paused = False            
        else:
            self.game.paused = True
        self.game.save_menu = False
        self.game.load_menu = False              


class ZoomIn(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.game_ui.map.zoom_in = True


class ZoomOut(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.game_ui.map.zoom_in = False