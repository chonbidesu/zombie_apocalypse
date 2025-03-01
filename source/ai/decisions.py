# decisions.py

from data import SkillType
from actions import Stand
from core.settings import *


class DecisionCommand:
    """Base class for all AI decisions."""
    def __init__(self, goal):
        self.goal = goal
        self.action = None

    def is_valid(self):
        """Checks if this decision is valid for the character."""
        raise NotImplementedError("Subclasses must implement is_valid().")
    
    def execute(self):
        """Executes the decision's action using ActionExecutor."""
        raise NotImplementedError("Subclasses must implement execute().")
    

class StandDecision(DecisionCommand):
    """The character decides to stand, if enough AP available."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        return self.goal.manager.character.is_dead
    
    def execute(self):
        character = self.goal.manager.character
        if character.helper.has_skill(SkillType.ANKLE_GRAB):
            ap_cost = 1
        else:
            ap_cost = STAND_AP

        if character.ap >= ap_cost:
            action = Stand(character)
            action.execute()
