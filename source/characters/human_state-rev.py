# human_state.py

import random

from settings import *
from data import Goal, Action, ActionResult, BLOCKS, BlockType, Occupation, OccupationCategory, OCCUPATIONS, ITEMS, ItemType, ItemFunction, SkillType
from characters.state import State, MoveTarget, BehaviourResult
from characters.ai import GoalManager, DecisionManager


class Human(State):
    """Represents the human state."""
    def __init__(self, character):
        super().__init__(character)
        self.character = character

    def _determine_behaviour(self):
        """Determine the NPCs behaviour based on their current goal."""

        # Determine the current goal
        self.character.current_goal = GoalManager.determine_goal(self.character)
        
        # Determine the best decision for the goal
        decision = DecisionManager.determine_decision(self.character)

        if decision:
            return decision
        
        return None # No decision found