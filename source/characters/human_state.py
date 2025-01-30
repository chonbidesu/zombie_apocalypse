# human_state.py

import random
from enum import Enum, auto

from settings import *

class HumanAction(Enum):
    # NPC actions
    GIVE_QUEST = auto()             # Provide a quest to the player
    FIND_TARGET = auto()            # Find a nearby location to move
    PURSUE = auto()       # Pursue an enemy character based on last known location
    WANDER = auto()                 # Move randomly
    RELOCATE = auto()               # Push character to an adjacent block due to overcrowding

    # Gameplay actions
    MOVE = auto()                   # Move to the target
    ATTACK = auto()                 # Attack a target enemy
    EXTRACT_DNA = auto()            # Extract DNA from a zombie
    REVIVIFY = auto()               # Revive a zombie to human form
    BARRICADE = auto()              # Reinforce the barricades
    SEARCH = auto()                 # Search for an item
    REPAIR = auto()                 # Repair damaged buildings
    ENTER = auto()                  # Enter a building
    LEAVE = auto()                  # Leave a building
    STAND_UP = auto()               # Stand up after death or revivification

    # Inventory actions
    EQUIP = auto()
    UNEQUIP = auto()
    USE = auto()
    DROP = auto()

class HumanSkill(Enum):
    BODY_BUILDING = auto()
    FREE_RUNNING = auto()
    CONSTRUCTION = auto()
    FIRST_AID = auto()
    FIREARMS_TRAINING = auto()

class Human:
    """Represents the human state."""
    def __init__(self, character, type=None):
        self.character = character
        self.hostile = self.is_hostile()
        self.type = type

    def act(self, action_points):
        """Execute AI behaviour."""
        # Only act if action points are available
        if action_points < 1:
            return False
        
        # Get block object at current location
        current_block = self.game.city.block(self.character.location[0], self.character.location[1])

        # Determine behaviour
        action = self.determine_behaviour(current_block)

        # Call action function
        if action == HumanAction.RELOCATE:
            self.relocate_npc(current_block)
            return  # Skip action after relocation

        elif action == HumanAction.ATTACK:
            self.game.chat_history.append(self.attack())
            return
        
        elif action == HumanAction.PURSUE:
            self.follow(current_block)

        elif action == HumanAction.BARRICADE:
            self.handle_barricades(current_block)
            return

        elif action == HumanAction.MOVE:
            target_dx, target_dy = self.find_target_dxy()
            if target_dx is not None and self.action_points >= 2:
                self.move_towards(target_dx, target_dy)
                return

        elif action == HumanAction.ENTER:
            self.enter()
            return
        
        elif action == HumanAction.WANDER:
            self.move()
            return

        elif action == HumanAction.STAND_UP:
            self.stand_up()
            return

        return False  # No action taken        


