# zombie_decisions.py

from .decisions import DecisionCommand
from actions import Move, MoveTarget, Enter, Leave, Attack, Decade
from data import SkillType, BLOCKS


class PursueBrainsDecision(DecisionCommand):
    """Zombie decision to pursue fresh brains when a living human is in sight."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if target human is visible within the zombie's perception range."""
        if self.goal.last_known_target:
            not_attackable = (self.goal.last_known_target and self.goal.manager.character.location != self.goal.last_known_target[1] or 
                              self.goal.manager.character.inside != self.goal.last_known_target[0].inside)
        else:
            not_attackable = False
        return self.goal.last_known_target and all(value for value in self.goal.last_known_target) and not_attackable

    def execute(self):
        """Move towards the nearest human, or fail if blocked."""
        character = self.goal.manager.character
        target_human, target_location = self.goal.last_known_target
        city = character.game.state.city
        x, y = character.location
        block = city.block(x, y)
        target_block = city.block(*target_location)
        properties = BLOCKS[target_block.type]

        # Determine the movement action
        if target_location in character.helper.get_adjacent_locations():
            self.action = Move(character)
            target_x, target_y = target_location[0], target_location[1]
            move_target = MoveTarget(target_x - x, target_y - y)
            self.action.execute(move_target)
            if self.action.sfx:
                self.action.play_sound()             

        elif target_human and target_human.inside and not character.inside:
            # Check if the building can be entered
            if properties.is_building and (target_block.barricade.level == 0 and not target_block.doors_closed) or character.helper.has_skill(SkillType.MEMORIES_OF_LIFE):
                self.action = Enter(character)
                self.action.execute()
                if self.action.sfx:
                    self.action.play_sound()                 

        elif target_human and not target_human.inside and character.inside:
            if (target_block.barricade.level == 0 and not target_block.doors_closed) or character.helper.has_skill(SkillType.MEMORIES_OF_LIFE):
                self.action = Leave(character)
                self.action.execute() 
                if self.action.sfx:
                    self.action.play_sound()   

class AttackBrainsDecision(DecisionCommand):
    """Zombie decision to attack a human if they are in the same block and within reach."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if target human is in the same block and has the same inside status."""
        character = self.goal.manager.character

        if self.goal.last_known_target:
            target, location = self.goal.last_known_target
            return character.location == location and character.inside == target.inside # True if target is in range
        
        return False

    def execute(self):
        """Attack the nearest human in the same block."""
        character = self.goal.manager.character        
        x, y = character.location
        block_characters = character.helper.filter_characters_at_location(x, y, inside=character.inside)

        if not block_characters.living_humans:
            return  # No valid targets, GoalManager will handle another decision

        character.choose_zombie_attack()
        target = block_characters.living_humans[0]  # Attack the first human found
        self.action = Attack(character)
        self.action.execute(target)
        if self.action.sfx and character.location == character.game.state.player.location:
            self.action.play_sound()

class MoveDecision(DecisionCommand):
    """Move towards a target location."""

    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal
        self.target_x = goal.target_block.x if goal.target_block else None
        self.target_y = goal.target_block.y if goal.target_block else None        

    def is_valid(self):
        """Valid if the target location is reachable."""
        return True  # No extra validation needed for movement

    def execute(self):
        """Move toward the target location, or attempt to break barricades if blocked."""
        character = self.goal.manager.character
        x, y = character.location

        if self.target_x: # If a target is selected, move there
            dx, dy = self.target_x - x, self.target_y - y

            # Move towards the target
            move_target = MoveTarget(dx, dy)

        else:
            move_target = None # If no target is selected, wander randomly

        self.action = Move(character)
        self.action.execute(move_target)
        if self.action.sfx and character.location == character.game.state.player.location:
            self.action.play_sound()        


class BreakInsideDecision(DecisionCommand):
    """Attempts to break down barricades to reach a lit building."""

    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if a human is inside a barricaded building OR the target is a lit building with barricades."""
        character = self.goal.manager.character
        target_human, loc = self.goal.last_known_target if self.goal.last_known_target else (None, None)
        block = self.goal.target_block

        if block:        
            properties = BLOCKS[block.type]
        
            if properties.is_building:
                # Human is inside a barricaded building
                if target_human:
                    return (
                        target_human.inside 
                        and character.inside != target_human.inside 
                        and block.barricade.level > 0 
                        and character.location == loc
                    )

                # No human, but the target is a lit building with barricades
                x, y = block.x, block.y

                return block.lights_on and block.barricade.level > 0 and character.location == (x, y)

        return False

    def execute(self):
        """Execute the attack on barricades."""
        character = self.goal.manager.character
        self.action = Decade(character)
        self.action.execute()
        if self.action.sfx and character.location == character.game.state.player.location:
            self.action.play_sound()




