# system.py

class SystemHandler:

    @staticmethod
    def quit(executor, target):
        executor.game.quit_game()

    @staticmethod
    def options(executor, target):
        pass # NEED TO SET THIS UP

    @staticmethod
    def save_menu(executor, target):
        executor.game.save_menu = True

    @staticmethod
    def save(executor, target):
        executor.game.save_game(target)

    @staticmethod
    def load_menu(executor, target):
        executor.game.load_menu = True

    @staticmethod
    def load(executor, target):
        executor.game.load_game(target)

    @staticmethod
    def newgame_menu(executor, target):
        executor.game.newgame_menu = True

    @staticmethod
    def start_game(executor, target):
        executor.game.start_game()

    @staticmethod
    def skills_menu(executor, target):
        executor.game.skills_menu = True

    @staticmethod
    def back(executor, target):
        executor.game.newgame_menu = False
        executor.game.save_menu = False
        executor.game.load_menu = False
        executor.game.skills_menu = False
        executor.game.reading_map = False

    @staticmethod
    def pause(executor, target):
        """Toggle game pause state."""
        if executor.game.paused:
            executor.game.paused = False            
        else:
            executor.game.paused = True
        executor.game.save_menu = False
        executor.game.load_menu = False              

    @staticmethod
    def zoom_in(executor, target):
        executor.game.game_ui.map.zoom_in = True

    @staticmethod
    def zoom_out(executor, target):
        executor.game.game_ui.map.zoom_in = False       