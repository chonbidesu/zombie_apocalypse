# action_data.py

from enum import Enum, auto
from dataclasses import dataclass

@dataclass
class ActionResult:
    success: bool
    message: str = ""
    witness: str = ""
    attacked: str = ""
    sfx: str = ""

class Action(Enum):
    # NPC actions
    GIVE_QUEST = auto()             # Provide a quest to the player

    # Combat Actions
    ATTACK = auto()                 # Attack a target enemy
    HEAL = auto()                   # Heal a friendly NPC
    SPEAK = auto()                  # Speak to a friendly NPC
    EXTRACT_DNA = auto()            # Extract DNA from a zombie
    REVIVIFY = auto()               # Revive a zombie to human form

    # Environment Actions
    CLOSE_DOORS = auto()            # Close the doors of a building
    OPEN_DOORS = auto()             # Open the doors of a building
    BARRICADE = auto()              # Reinforce the barricades
    DECADE = auto()                 # Tear down the barricades
    SEARCH = auto()                 # Search for an item
    REPAIR_BUILDING = auto()        # Repair a building    
    RANSACK = auto()                # Ransack a building 
    DUMP = auto()                   # Dump a dead body outside

    # Player Movement
    MOVE = auto()                   # Move to the target
    MOVE_UP = auto()
    MOVE_DOWN = auto()
    MOVE_LEFT = auto()
    MOVE_RIGHT = auto()
    MOVE_UPLEFT = auto()
    MOVE_UPRIGHT = auto()
    MOVE_DOWNLEFT = auto()
    MOVE_DOWNRIGHT = auto()
    ENTER = auto()                  # Enter a building
    LEAVE = auto()                  # Leave a building
    STAND = auto()                  # Stand up after death or revivification
    PURSUE = auto()                 # Pursue an enemy character based on last known location
    WANDER = auto()                 # Move randomly    

    # Inventory actions
    EQUIP = auto()
    UNEQUIP = auto()
    USE = auto()
    DROP = auto()

    # System actions
    QUIT = auto()
    PAUSE = auto()
    OPTIONS = auto()
    NEW_GAME = auto()
    NEWGAME_MENU = auto()
    SAVE = auto()
    SAVE_MENU = auto()
    LOAD = auto()
    LOAD_MENU = auto()
    SKILLS_MENU = auto()
    BACK = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    RESTART = auto()