# system.py

from actions import ActionCommand


class Quit(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        self.character.game.quit_game()


class OpenSaveMenu(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        self.character.game.save_menu = True


class SaveGame(ActionCommand):
    def __init__(self, character):
        super().__init__(character)    

    def execute(self, target):
        self.character.game.save_game(target)


class OpenLoadMenu(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        self.character.game.load_menu = True


class LoadGame(ActionCommand):
    def __init__(self, character):
        super().__init__(character)    

    def execute(self, target):
        self.character.game.load_game(target)


class OpenNewgameMenu(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        self.character.game.newgame_menu = True


class StartGame(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):    
        self.character.game.start_game()


class OpenSkillsMenu(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        self.character.game.skills_menu = True


class Back(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        self.character.game.newgame_menu = False
        self.character.game.save_menu = False
        self.character.game.load_menu = False
        self.character.game.skills_menu = False
        self.character.game.reading_map = False


class Pause(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        """Toggle game pause state."""
        if self.character.game.paused:
            self.character.game.paused = False            
        else:
            self.character.game.paused = True
        self.character.game.save_menu = False
        self.character.game.load_menu = False              


class ZoomIn(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        self.character.game.game_ui.map.zoom_in = True


class ZoomOut(ActionCommand):
    def __init__(self, character):
        super().__init__(character) 

    def execute(self):
        self.character.game.game_ui.map.zoom_in = False