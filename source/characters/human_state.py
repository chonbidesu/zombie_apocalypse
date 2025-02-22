# human_state.py

import random

from settings import *
from data import Goal, Action, ActionResult, BLOCKS, BlockType, Occupation, OccupationCategory, OCCUPATIONS, ITEMS, ItemType, ItemFunction, SkillType
from characters.state import State, MoveTarget, BehaviourResult


class Human(State):
    """Represents the human state."""
    def __init__(self, character):
        super().__init__(character)
        self.character = character
   
    def update_name(self):
        """Updates the character's name."""
        self.character.current_name = f"{self.character.name.first_name} {self.character.name.last_name}"
                                