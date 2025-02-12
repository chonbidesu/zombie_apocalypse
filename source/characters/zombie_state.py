# zombie_state.py

import random

from settings import *
from data import Action, BLOCKS
from characters.state import State, MoveTarget, Result


class Zombie(State):
    """Represents the zombie state."""
    def __init__(self, game, character):
        super().__init__(game, character)     

    def _determine_behaviour(self, block):
        """Determine the priority for the zombie."""
        # Get block properties at current location
        properties = BLOCKS[block.type]

        # Get character data at current location
        x, y = self.character.location[0], self.character.location[1]
        inside = self.character.inside

        # Get all characters at current location
        block_characters = self.filter_characters_at_location(x, y, inside)

        # Get adjacent block locations and targets
        adjacent_locations = self.get_adjacent_locations()
        move_targets = self.get_move_targets(adjacent_locations, x, y)

        # Priority 1: Stand up if dead
        if self.character.is_dead:
            return Result(Action.STAND) if self.character.ap >= STAND_AP else False

        # Priority 2: Attack current target if in current location, otherwise change target if another human in current location
        if len(block_characters.living_humans) > 0:
            if self.current_target not in block_characters.living_humans:
                random.shuffle(block_characters.living_humans)
                self.current_target = block_characters.living_humans[0] # Choose a new target
            return Result(Action.ATTACK, self.current_target)

        # Priority 3: If current target exists but not in current location, and no other brainz available, pursue target
        if self.current_target:
            # Check if the current target is at the current location but not the same inside status
            if self.current_target.location == self.character.location and self.current_target.inside != self.character.inside:
                if self.character.inside: # Pursue the target outside, if possible
                    if block.barricade.level == 0:
                        return Result(Action.LEAVE)
                    else: # Attack barricades if they are in the way
                        print("Attacking barricades to get at target outside")
                        return Result(Action.DECADE)
                else: # Pursue the target inside, if possible
                    if block.barricade.level == 0:
                        return Result(Action.ENTER)
                    else: # Attack the barricades if they are in the way
                        print("Attacking barricades to get at target inside")
                        return Result(Action.DECADE)
            elif self.current_target.location in adjacent_locations: # If the current target is in an adjacent block, pursue
                for location in adjacent_locations:
                    if location == self.current_target.location:
                        dx, dy = location[0] - self.character.location[0], location[1] - self.character.location[1]
                        target_direction = MoveTarget(dx, dy)
                return Result(Action.MOVE, target_direction)
            else: # Lose current target if they have escaped pursuit
                self.current_target = None

        # Priority 4: If no current target, move to adjacent target if one exists
        if move_targets:
            random.shuffle(move_targets) # Pick a random target
            return Result(Action.MOVE, move_targets[0])

        # Priority 5: With no immediate priorities, let the zombie decide its next action
        if self.character.inside:
            action_weights = {
                Action.RANSACK: 50 if not block.ruined else 0,
                Action.WANDER: 30,
                Action.LEAVE: 20,
            }
            choice = self._make_choice(action_weights)
            if choice:
                return Result(choice)
        
        elif properties.is_building:
            action_weights = {
                Action.WANDER: 50,
                Action.DECADE: 25 if block.barricade.level > 0 else 0,
                Action.ENTER: 25 if block.barricade.level == 0 else 0,
            }
            choice = self._make_choice(action_weights)
            if choice:
                return Result(choice)            
        
        return Result(Action.WANDER)  # No behaviour determined, so wander

    def get_move_targets(self, adjacent_locations, x, y):
        move_targets = []
        for location in adjacent_locations:
            adjacent_x, adjacent_y = location
            adjacent_characters = self.filter_characters_at_location(x, y)
            if adjacent_characters.living_humans:
                dx, dy = adjacent_x - x, adjacent_y - y
                move_target = MoveTarget(dx, dy)
                move_targets.append(move_target)
        if not move_targets: # If no brainz available, look for lit buildings
            city = self.game.city
            for location in adjacent_locations:
                adjacent_x, adjacent_y = location
                block = city.block(adjacent_x, adjacent_y)
                properties = BLOCKS[block.type]
                if properties.is_building:
                    if block.lights_on:
                        dx, dy = adjacent_x - x, adjacent_y - y
                        move_target = MoveTarget(dx, dy)
                        move_targets.append(move_target)
        return move_targets        