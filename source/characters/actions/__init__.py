# actions.py

from characters.actions.system import SystemHandler
from characters.actions.movement import MovementHandler
from characters.actions.combat import CombatHandler
from characters.actions.item import ItemHandler
from characters.actions.environment import EnvironmentHandler

from settings import *
from data import Action


class ActionExecutor:
    """Handles executing actions for both player and AI characters."""
    def __init__(self, game, actor):
        self.game = game
        self.actor = actor  # Define the acting character
        self.handlers = {
            Action.QUIT: SystemHandler.quit,
            Action.PAUSE: SystemHandler.pause,
            Action.OPTIONS: SystemHandler.options,
            Action.START_GAME: SystemHandler.start_game,
            Action.NEWGAME_MENU: SystemHandler.newgame_menu,
            Action.SAVE: SystemHandler.save,
            Action.SAVE_MENU: SystemHandler.save_menu,
            Action.LOAD: SystemHandler.load,
            Action.LOAD_MENU: SystemHandler.load_menu,
            Action.SKILLS_MENU: SystemHandler.skills_menu,
            Action.BACK: SystemHandler.back,
            Action.ZOOM_IN: SystemHandler.zoom_in,
            Action.ZOOM_OUT: SystemHandler.zoom_out,

            Action.ENTER: MovementHandler.enter,
            Action.LEAVE: MovementHandler.leave,
            Action.MOVE: MovementHandler.move,
            Action.MOVE_UP: MovementHandler.move_up,
            Action.MOVE_DOWN: MovementHandler.move_down,
            Action.MOVE_LEFT: MovementHandler.move_left,
            Action.MOVE_RIGHT: MovementHandler.move_right,
            Action.MOVE_UPLEFT: MovementHandler.move_upleft,
            Action.MOVE_UPRIGHT: MovementHandler.move_upright,
            Action.MOVE_DOWNLEFT: MovementHandler.move_downleft,
            Action.MOVE_DOWNRIGHT: MovementHandler.move_downright,
            Action.STAND: MovementHandler.stand,
            Action.WANDER: MovementHandler.wander,

            Action.ATTACK: CombatHandler.attack,
            Action.HEAL: CombatHandler.heal,
            Action.SPEAK: CombatHandler.speak,
            Action.EXTRACT_DNA: CombatHandler.extract_dna,
            Action.INJECT: CombatHandler.inject,

            Action.USE: ItemHandler.use,
            Action.DROP: ItemHandler.drop,
            Action.EQUIP: ItemHandler.equip,
            Action.UNEQUIP: ItemHandler.unequip,

            Action.BARRICADE: EnvironmentHandler.barricade,
            Action.DECADE: EnvironmentHandler.decade,
            Action.OPEN_DOORS: EnvironmentHandler.open_doors,
            Action.CLOSE_DOORS: EnvironmentHandler.close_doors,
            Action.SEARCH: EnvironmentHandler.search,
            Action.REPAIR_BUILDING: EnvironmentHandler.repair_building,
            Action.RANSACK: EnvironmentHandler.ransack,
            Action.DUMP: EnvironmentHandler.dump,
        }

    def execute(self, action, target=None):
        """Execute AI and player actions."""
        # Fetch block at the actor's location
        x, y = self.actor.location
        self.block = self.game.state.city.block(x, y)

        self.weapon = self.actor.weapon
        self.player = self.game.state.player 
        self.screen_transition = self.game.game_ui.screen_transition
        self.action_progress = self.game.game_ui.action_progress

        if self.actor == self.player:
            self.is_player = True
        else:
            self.is_player = False

        if action in self.handlers:
            return self.handlers[action](self, target)
        print(f"Unknown action: {action}  Target: {target}")

    
    


