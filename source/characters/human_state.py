# human_state.py

from enum import Enum, auto

from settings import *
from characters.actions import ActionExecutor

class Action(Enum):
    # NPC actions
    GIVE_QUEST = auto()             # Provide a quest to the player
    FIND_TARGET = auto()            # Find a nearby location to move
    PURSUE = auto()                 # Pursue an enemy character based on last known location
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
    STAND = auto()                  # Stand up after death or revivification

    # Inventory actions
    EQUIP = auto()
    UNEQUIP = auto()
    USE = auto()
    DROP = auto()


"""
class HumanSkill(Enum):
    BODY_BUILDING = auto()
    FREE_RUNNING = auto()
    CONSTRUCTION = auto()
    FIRST_AID = auto()
    FIREARMS_TRAINING = auto()
"""
    

class Human:
    """Represents the human state."""
    def __init__(self, game, character, type=None):
        self.character = character
        self.type = type

    def act(self, action_points):
        """Execute AI behaviour."""
        # Only act if action points are available
        if action_points < 1:
            return False
        
        # Get block object at current location
        current_block = self.game.city.block(self.character.location[0], self.character.location[1])

        # Determine behaviour
        action, target = self.determine_behaviour(current_block)

        # Call action function
        if action == HumanAction.RELOCATE:
            self.actions.relocate(current_block)

        elif action == HumanAction.ATTACK:
            self.actions.attack(target)
        
        elif action == HumanAction.FIND_TARGET:
            self.actions.find_target()
        
        elif action == HumanAction.PURSUE:
            self.actions.pursue(target, current_block)

        elif action == HumanAction.BARRICADE:
            self.actions.barricade(current_block)

        elif action == HumanAction.MOVE:
            target_dx, target_dy = self.actions.find_target_dxy(target)
            if target_dx is not None and self.action_points >= 1:
                self.actions.move(target_dx, target_dy)

        elif action == HumanAction.ENTER:
            self.actions.enter()
        
        elif action == HumanAction.WANDER:
            self.actions.wander()

        elif action == HumanAction.STAND:
            self.actions.stand()

    def determine_human_behaviour(self, current_block):
        """Determine the priority for the NPC."""
        properties = BLOCKS[current_block.type]
        # Stand up if dead and have enough action points
        if self.is_dead:
            return HumanAction.STAND if self.action_points >= STAND_AP else False

        # Relocate if the block is overcrowded
        if current_block.current_humans > HUMAN_CAPACITY:
            return HumanAction.RELOCATE
        
        elif self.type == NPCType.SURVIVOR:
            if current_block.current_zombies > 0:
                return HumanAction.FIND_TARGET # Flee to another building
            elif self.location == self.game.player.location and self.inside == self.game.player.inside:
                return HumanAction.GIVE_QUEST
            elif not self.inside and properties.is_building:
                    return HumanAction.ENTER_BUILDING
            
        elif self.type == NPCType.PREPPER:
            if properties.is_building and not self.inside:
                return HumanAction.ENTER_BUILDING
            elif self.inside:
                for zombie in self.game.zombies.list:
                    if self.location == zombie.location and zombie.inside:
                        return HumanAction.ATTACK_NPC
                if current_block.is_ransacked:
                    return HumanAction.REPAIR_BUILDING
                elif current_block.barricade.level <= 4:
                    return HumanAction.HANDLE_BARRICADE
                else:
                    return HumanAction.FIND_TARGET
        
        elif self.type == NPCType.SCIENTIST:
            if current_block.current_zombies > 0:
                return HumanAction.ATTACK_NPC
            else:
                return HumanAction.FIND_TARGET
            
        elif self.type == NPCType.PKER:
            if self.location == self.game.player.location and self.inside == self.game.player.inside:
                self.pursuing_player = True
                self.last_known_player_location = self.game.player.location
                return HumanAction.ATTACK_PLAYER

        return None  # No behaviour determined