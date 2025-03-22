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
        if not self.goal.last_known_target:
            return False
        
        target, location = self.goal.last_known_target
        character = self.goal.manager.character

        # True if human is not in attack range
        not_attackable = character.location != location or character.inside != target.inside
        return not_attackable

    def execute(self):
        """Move towards the nearest human, or fail if blocked."""
        character = self.goal.manager.character
        target_human, target_location = self.goal.last_known_target
        city = character.game.state.city
        x, y = character.location
        target_block = city.block(*target_location)
        properties = BLOCKS[target_block.type]

        # Determine the movement action
        if target_location in character.helper.get_adjacent_locations():
            self.action = Move(character)
            target_x, target_y = target_location[0], target_location[1]
            move_target = MoveTarget(target_x - x, target_y - y)
            self.action.execute(move_target)          

        elif target_human and target_human.inside and not character.inside:
            # Check if the building can be entered
            can_enter = (
                properties.is_building
                and target_block.barricade.level == 0
                and not target_block.doors_closed
            ) or character.helper.has_skill(SkillType.MEMORIES_OF_LIFE)

            if can_enter:
                self.action = Enter(character)
                self.action.execute()               

        elif target_human and not target_human.inside and character.inside:
            can_leave = (
                target_block.barricade.level == 0
                and not target_block.doors_closed
            ) or character.helper.has_skill(SkillType.MEMORIES_OF_LIFE)

            if can_leave:
                self.action = Leave(character)
                self.action.execute() 

        self.play_sfx()

    def play_sfx(self):
        """Play the sound effect if the zombie is near the player."""
        if self.action and self.action.sfx:
            self.action.play_sound()

class AttackBrainsDecision(DecisionCommand):
    """Zombie decision to attack a human if they are in the same block and within reach."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if target human is in the same block and has the same inside status."""
        character = self.goal.manager.character

        if not self.goal.last_known_target:
            return False
        
        target, location = self.goal.last_known_target
        
        return character.location == location and character.inside == target.inside # True if target is in range

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

    def is_valid(self):
        """Valid if the target location is reachable."""
        return True  # No extra validation needed for movement

    def execute(self):
        """Move toward the target location, or attempt to break barricades if blocked."""
        target_x = self.goal.target_block.x if self.goal.target_block else None
        target_y = self.goal.target_block.y if self.goal.target_block else None 
        target_properties = BLOCKS[self.goal.target_block.type] if self.goal.target_block else None      
        character = self.goal.manager.character
        x, y = character.location
        move_target = None # If no target is selected, wander randomly

        if character.location == (target_x, target_y) and not character.inside and target_properties and target_properties.is_building:
            if (
                self.goal.target_block.doors_closed and character.helper.has_skill(SkillType.MEMORIES_OF_LIFE) or
                not self.goal.target_block.doors_closed
            ):
                self.action = Enter(character)
                self.action.execute()
                return

        elif target_x: # If a target is selected, move there
            dx, dy = target_x - x, target_y - y

            if (dx, dy) == (0, 0):
                return

            # Move towards the target
            move_target = MoveTarget(dx, dy)

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
        print(f"Target human: {target_human}, location: {loc}, block: {block}")

        if not block:    
            return False
          
        properties = BLOCKS[block.type]

        if not properties.is_building:
            print("Target block is not a building")
            return False
    
        # Human is inside a barricaded building
        if target_human:
            print("Human is targeted")
            return (
                target_human.inside 
                and character.inside != target_human.inside 
                and block.barricade.level > 0 
                and character.location == loc
            )

        # No human, but the target is a lit building with barricades
        x, y = block.x, block.y

        print(f"Block at {x}, {y} is a building {properties.is_building} with barricades {block.barricade.level}")
        return block.lights_on and block.barricade.level > 0 and character.location == (x, y)

    def execute(self):
        """Execute the attack on barricades."""
        character = self.goal.manager.character
        self.action = Decade(character)
        self.action.execute()
        if self.action.sfx and character.location == character.game.state.player.location:
            self.action.play_sound()




