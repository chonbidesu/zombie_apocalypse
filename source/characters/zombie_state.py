# zombie_state.py

import random
from enum import Enum, auto

from settings import *

class ZombieAction(Enum):
    # NPC actions
    FIND_TARGET = auto()            # Find a nearby location to move
    PURSUE = auto()                 # Pursue an enemy character based on last known location
    WANDER = auto()                 # Move randomly
    RELOCATE = auto()               # Push character to an adjacent block due to overcrowding

    # Gameplay actions
    MOVE = auto()                   # Move to the target
    ATTACK = auto()                 # Attack a target enemy
    ENTER = auto()                  # Enter a building
    LEAVE = auto()                  # Leave a building
    RANSACK = auto()                # Ransack a building
    STAND_UP = auto()               # Stand up after death or revivification

class ZombieSkill(Enum):
    pass

class Zombie:
    """Represents the zombie state."""
    def __init__(self, character, type=None):
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
        action = self._determine_behaviour(current_block)

        # Call action function
        if action == ZombieAction.RELOCATE:
            self.relocate_npc(current_block)
            return  # Skip action after relocation

        elif action == ZombieAction.ATTACK:
            self.game.chat_history.append(self.attack())
            return
        
        elif action == ZombieAction.PURSUE:
            self.follow(current_block)

        elif action == ZombieAction.MOVE:
            target_dx, target_dy = self.find_target_dxy()
            if target_dx is not None and self.action_points >= 2:
                self.move_towards(target_dx, target_dy)
                return

        elif action == ZombieAction.ENTER:
            self.enter()
            return
        
        elif action == ZombieAction.LEAVE:
            self.leave()
            return
        
        elif action == ZombieAction.RANSACK:
            self.ransack()
            return

        elif action == ZombieAction.WANDER:
            self.move()
            return

        elif action == ZombieAction.STAND_UP:
            self.stand_up()
            return

        return False  # No action taken        

    def _determine_behaviour(self, current_block):
        """Determine the priority for the zombie."""
        properties = BLOCKS[current_block.type]
        # Stand up if dead and have enough action points
        if self.is_dead:
            return ZombieAction.STAND_UP if self.action_points >= STAND_UP_AP else False

        # Relocate if the block is overcrowded
        if current_block.zombies > ZOMBIE_CAPACITY:
            return ZombieAction.RELOCATE        
            
        elif current_block.humans > 0:
            return ZombieAction.ATTACK

        elif self.is_enemy_adjacent():
            self.pursuing_enemy = True
            #self.last_known_enemy_location = self.game.player.location
            return ZombieAction.PURSUE

        elif properties.is_building and current_block.barricade.level == 0 and not self.inside and self.action_points >= 1:
            roll = random.randint(1, 20)
            if roll < 5:
                return ZombieAction.ENTER
                    
        if self.inside:
            if not current_block.is_ransacked and self.action_points >= 1:
                roll = random.randint(1, 20)
                if roll < 5:
                    return ZombieAction.RANSACK
                
        if self.find_target_dxy() and self.action_points >= 1:
            target_dx, target_dy = self.find_target_dxy()
            if (target_dx, target_dy) == (0, 0):
                return ZombieAction.HANDLE_BARRICADE
            else:
                return ZombieAction.MOVE_TOWARDS

        # Random movement if no targets or barricades present
        if self.action_points >= 2:
            return ZombieAction.WANDER

        return None  # No behaviour determined