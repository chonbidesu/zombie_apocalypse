# goal_manager.py

import random

from ai.goals import SurviveGoal, SecureShelterGoal, HuntBrainsGoal, IdleGoal, StandGoal


class GoalManager:
    """Manages goals for NPCs, handling zombies and humans differently."""

    def __init__(self, character):
        self.character = character
        self.previous_goal = None
        self.current_goal = None

    def evaluate_goal(self):
        """Determines the appropriate goal based on character state."""
        if not self.current_goal or self.current_goal.is_complete():
            if self.character.is_human:
                new_goal = None #new_goal = self.evaluate_human_goal()
            else:
                new_goal = self.evaluate_zombie_goal()

            return self.set_goal(new_goal)
        
        return self.current_goal

    def evaluate_human_goal(self):
        """Human goal selection (they remember goals & react to danger)."""

        # If injured, switch to survival mode
        if self.character.hp < self.character.max_hp // 2 or type(self.current_goal) == SurviveGoal:
            return SurviveGoal(self)

        # Otherwise, set a new goal
        return SecureShelterGoal(self)

    def evaluate_zombie_goal(self):
        """Zombie goal selection."""

        # If zombie is dead, stand up
        if self.character.is_dead:
            return StandGoal(self)

        # If a human is visible, switch to hunting mode
        if self.current_goal and type(self.current_goal) == IdleGoal:
            last_known_target = self.current_goal.last_known_target
            new_goal = HuntBrainsGoal(self)
            new_goal.last_known_target = last_known_target
            return new_goal

        # If no humans are visible, wander aimlessly
        return IdleGoal(self)

    def find_visible_human(self):
        """Returns the closest visible human and their location."""
        city = self.character.game.state.city
        x, y = self.character.location
        block = city.block(x, y)
        adjacent_locations = self.character.helper.get_adjacent_locations()
        block_characters = self.character.helper.filter_characters_at_location(x, y, inside=self.character.inside)

        # Check if a human is standing nearby
        if block_characters.living_humans:
            return block_characters.living_humans[0], (x, y)

        # Check if a human is in the same block but outside
        block_characters_outside = self.character.helper.filter_characters_at_location(x, y, inside=False)
        if block_characters_outside.living_humans:
            return block_characters_outside.living_humans[0], (x, y)

        # Check if a human is inside and doors are open
        block_characters_inside = self.character.helper.filter_characters_at_location(x, y, inside=True)
        if block_characters_inside.living_humans and not block.doors_closed:
            return block_characters_inside.living_humans[0], (x, y)

        # Check adjacent blocks for visible humans outside
        random.shuffle(adjacent_locations)
        for loc in adjacent_locations:
            block_characters = self.character.helper.filter_characters_at_location(*loc, inside=False)
            if block_characters.living_humans:
                return block_characters.living_humans[0], loc

        return None, None   
    
    def find_watching_zombies(self):
        """Returns a list of zombies that can see the character."""
        watching_zombies = []
        city = self.character.game.state.city
        x, y = self.character.location
        block = city.block(x, y)
        adjacent_locations = self.character.helper.get_adjacent_locations()

        # Check if a zombie is standing nearby
        block_characters = self.character.helper.filter_characters_at_location(x, y, inside=self.character.inside)
        if block_characters.living_zombies:
            watching_zombies.extend(block_characters.living_zombies)

        # Check if zombies are in the same block but outside
        if self.character.inside:
            block_characters_outside = self.character.helper.filter_characters_at_location(x, y, inside=False)
            if block_characters_outside.living_zombies and not block.doors_closed:
                watching_zombies.extend(block_characters_outside.living_zombies)
            

        # Check if zombies are inside and doors are open
        else:
            block_characters_inside = self.character.helper.filter_characters_at_location(x, y, inside=True)
            if block_characters_inside.living_zombies:
                watching_zombies.extend(block_characters_inside.living_zombies)

        # Check adjacent blocks for watching zombies
        if not self.character.inside:
            for loc in adjacent_locations:
                block_characters_inside = self.character.helper.filter_characters_at_location(*loc, inside=True)
                block_characters_outside = self.character.helper.filter_characters_at_location(*loc, inside=False)
                if block_characters_inside.living_zombies:
                    watching_zombies.extend(block_characters_inside.living_zombies)
                elif block_characters_outside.living_zombies:
                    watching_zombies.extend(block_characters_outside.living_zombies)

        return watching_zombies

    def set_goal(self, new_goal):
        """Sets a new goal (zombies immediately switch, humans remember old goals)."""
        if type(new_goal) == type(self.current_goal):
            return self.current_goal

        self.previous_goal = self.current_goal
        self.current_goal = new_goal
        return new_goal

