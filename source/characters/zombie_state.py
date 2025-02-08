# zombie_state.py

import random
from dataclasses import dataclass

from settings import *
from data import Action, BLOCKS
from characters.state import State, MoveTarget, Result


class Zombie(State):
    """Represents the zombie state."""
    def __init__(self, game, character):
        super().__init__(game, character)     

    def _determine_behaviour(self, block):
        """Determine the priority for the zombie."""
        properties = BLOCKS[block.type]
        living_zombies, living_humans, _ = self._filter_npcs_at_npc_location()       
        dx, dy = self._find_target_dxy(block)
        nearby_target = MoveTarget(dx, dy)

        # Stand up if dead and have enough action points
        if self.character.is_dead:
            return Result(Action.STAND) if self.character.ap >= STAND_AP else False

        # Relocate if the block is overcrowded
        if len(living_zombies + living_humans) > BLOCK_CAPACITY:
            return Result(Action.RELOCATE)

        elif len(living_humans) > 0:
            if self.current_target not in living_humans:
                random.shuffle(living_humans)
                self.current_target = living_humans[0] # Choose a new target
            return Result(Action.ATTACK, self.current_target)

        elif self.current_target:
            if self.current_target.location == self.character.location and self.current_target.inside != self.character.inside:
                if self.character.inside:
                    if block.barricade.level == 0:
                        return Result(Action.LEAVE)
                    else:
                        return Result(Action.DECADE)
                else:
                    if block.barricade.level == 0:
                        return Result(Action.ENTER)
                    else:
                        return Result(Action.DECADE)

        elif nearby_target.dx is not None and nearby_target.dy is not None:
            return Result(Action.MOVE, nearby_target)

        elif properties.is_building and block.barricade.level == 0 and not self.character.inside and self.character.ap >= 1:
            roll = random.randint(1, 20)
            if roll < 5:
                return Result(Action.ENTER)
                    
        if self.character.inside:
            if block.ransack_level < 5 and self.character.ap >= 1:
                roll = random.randint(1, 20)
                if roll < 5:
                    return Result(Action.RANSACK)
                
        # Random movement if no targets or barricades present
        if self.character.ap >= 2:
            return Result(Action.WANDER)

        return None  # No behaviour determined

    def _find_target_dxy(self, block):
        """Finds a nearby player or lit building."""
        properties = BLOCKS[block.type]
        player = self.game.state.player

        # Otherwise, move    
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue # Don't return the current block

                adjacent_x = self.character.location[0] + dx
                adjacent_y = self.character.location[1] + dy

                if 0 < adjacent_x < CITY_SIZE and 0 < adjacent_y < CITY_SIZE:
                    adjacent_humans = [
                        npc for npc in self.game.state.npcs.list
                        if (npc.location == (adjacent_x, adjacent_y)) and npc.is_human and not npc.is_dead and not npc.inside
                    ]

                    if player.location == (adjacent_x, adjacent_y) and player.is_human:
                        adjacent_humans.append(player)

                    if adjacent_humans: # Check if humans are nearby
                        return (dx, dy) # Shamble towards brains
                    else:
                        if properties.is_building and block.lights_on:
                            return (0, 0) # Stay put if current block is lit     
                        else:                 
                            adjacent_block = self.game.state.city.block(adjacent_x, adjacent_y)
                            adjacent_block_properties = BLOCKS[adjacent_block.type]
                            if adjacent_block_properties.is_building and adjacent_block.lights_on:
                                return (dx, dy) 

        return (None, None)