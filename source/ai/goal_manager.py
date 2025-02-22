# goal_manager.py

from ai.goals import SurviveGoal

class GoalManager:
    """Determines NPC goal based on their current state."""
    def __init__(self):
        self.goal_stack = [] # Stack to remember goals if interrupted

    def evaluate_goal(self, character):
        """Evaluates the NPC's current goal and whether to switch goals."""

        # High priority interruption
        if character.hp < character.max_hp // 2:
            return self.set_goal(character, SurviveGoal())
        
        # Resume previous goal if interruption is over
        if character.current_goal and character.current_goal.is_complete(character):
            return self.resume_goal(character)
        
        # Otherwise, return the current goal or set a new one
        return character.current_goal if character.current_goal else self.set_goal(character)

    def set_goal(self, character, new_goal):
        """Set a new goal, saving the current goal to the stack."""

        # Push the goal if it's different from the current one
        if character.current_goal and character.current_goal != new_goal:
            self.goal_stack.append(character.current_goal)

        character.current_goal = new_goal
        return new_goal

    def resume_goal(self, character):
        """Resume the previous goal when the current one is completed."""
        if self.goal_stack:
            character.current_goal = self.goal_stack.pop()
            return character.current_goal
        return None
