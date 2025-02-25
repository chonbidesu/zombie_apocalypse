# zombie_decisions.py

from .decisions import DecisionCommand
from actions import Move, MoveTarget, Enter, Leave, Attack
from data import SkillType


class PursueBrainsDecision(DecisionCommand):
    """Zombie decision to pursue fresh brains when a living human is in sight."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if a human is visible within the zombie's perception range."""
        character = self.goal.manager.character
        x, y = character.location
        block_characters = character.helper.filter_characters_at_location(x, y, inside=character.inside)

        return self.goal.manager.find_visible_human() is not None and not bool(block_characters.living_humans)

    def execute(self):
        """Move towards the nearest human, or fail if blocked."""
        character = self.goal.manager.character
        target_human, target_location = self.goal.manager.find_visible_human()
        city = character.game.state.city
        x, y = character.location
        block = city.block(x, y)

        # Determine the movement action
        if target_location in character.helper.get_adjacent_locations():
            action = Move(character)
            target_x, target_y = target_location[0], target_location[1]
            move_target = MoveTarget(target_x - x, target_y - y)
            action.execute(move_target)

        elif target_human and target_human.inside and not character.inside:
            # Check if the building can be entered
            if (block.barricade.level == 0 and not block.doors_closed) or character.helper.has_skill(SkillType.MEMORIES_OF_LIFE):
                action = Enter(character)
                action.execute()
            else:
                self.success = False  # Blocked, let the goal manager handle another decision

        elif target_human and not target_human.inside and character.inside:
            if (block.barricade.level == 0 and not block.doors_closed) or character.helper.has_skill(SkillType.MEMORIES_OF_LIFE):
                action = Leave(character)
                action.execute()
            else:
                self.success = False
    

class AttackBrainsDecision(DecisionCommand):
    """Zombie decision to attack a human if they are in the same block and within reach."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if a human is in the same block and has the same inside status."""
        character = self.goal.manager.character
        x, y = character.location
        block_characters = character.helper.filter_characters_at_location(x, y, inside=character.inside)

        return bool(block_characters.living_humans)  # True if there are humans to attack

    def execute(self):
        """Attack the nearest human in the same block."""
        character = self.goal.manager.character        
        x, y = character.location
        block_characters = character.helper.filter_characters_at_location(x, y, inside=character.inside)

        if not block_characters.living_humans:
            return  # No valid targets, GoalManager will handle another decision

        target = block_characters.living_humans[0]  # Attack the first human found
        action = Attack(character)
        action.execute(target)


class ChaseBrainsDecision(DecisionCommand):
    """Zombies chase the last known location of a human who moved out of sight."""

    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal
        self.target_human, self.target_location = goal.last_known_target if goal.last_known_target else None, None  # (Human, (x, y))

    def is_valid(self):
        """Valid if the zombie hasn't yet reached the last known location."""
        character = self.goal.manager.character
        return self.goal.last_known_target and character.location != self.target_location

    def execute(self):
        """Move towards the last known location of the human."""
        character = self.goal.manager.character        

        # Move toward the last known location
        x, y = character.location
        if self.target_location:
            target_x, target_y = self.target_location
            move_target = MoveTarget(target_x - x, target_y - y)
            action = Move(self)
            action.execute(move_target)

            if character.location == (target_x, target_y):
                self.goal.last_known_target = None
                self.goal.target_block = None


class MoveDecision(DecisionCommand):
    """Move towards a target location."""

    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal
        self.target_location = goal.target_block.location if goal.target_block else None, None

    def is_valid(self):
        """Valid if the target location is reachable."""
        return True  # No extra validation needed for movement

    def execute(self):
        """Move toward the target location, or attempt to break barricades if blocked."""
        character = self.goal.manager.character
        x, y = character.location

        if self.target_location: # If a target is selected, move there
            target_x, target_y = self.target_location
            dx, dy = target_x - x, target_y - y

            # Move towards the target
            move_target = MoveTarget(dx, dy)

        else:
            move_target = None # If no target is selected, wander randomly

        Move(character).execute(move_target)


class BreakInsideDecision(DecisionCommand):
    """Attempts to break down barricades to reach a lit building."""

    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal
        self.target_block = goal.target_block

    def is_valid(self):
        """Valid if the block has barricades."""
        character = self.goal.manager.character
        return self.target_block and self.target_block.barricade.level > 0 or \
            (self.target_block.doors_closed and character.helper.has_skill(SkillType.MEMORIES_OF_LIFE)) or \
            self.target_block.doors_closed == False

    def execute(self):
        """Execute the attack on barricades."""



