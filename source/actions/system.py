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
        self.game.open_save_menu()


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
        self.game.open_load_menu()


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
        self.game.open_newgame_menu()


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
        self.game.open_skills_menu()


class Back(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.back()


class Pause(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        """Toggle game pause state."""
        self.game.pause()            


class ZoomIn(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.zoom_in()


class ZoomOut(ActionCommand):
    def __init__(self, game):
        super().__init__(character=None) 
        self.game = game

    def execute(self):
        self.game.zoom_out()