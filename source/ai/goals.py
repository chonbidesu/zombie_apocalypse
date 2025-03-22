# goals.py

import random

from .human_decisions import ScoutSafehouseDecision, EnterSafehouseDecision, SecureSafehouseDecision, SeekFAKDecision, HealThyselfDecision
from .zombie_decisions import PursueBrainsDecision, AttackBrainsDecision, BreakInsideDecision, MoveDecision
from .decisions import StandDecision
from data import BLOCKS


class GoalCommand:
    """Base class for all AI goals."""

    def __init__(self, manager, target=None):
        self.manager = manager
        self.current_decision = None  # Holds the active decision
        self._last_known_target = target  # Stores (human, last_seen_location)
        self.target_block = None        

    @property
    def last_known_target(self):
        """Dynamically updates if a human is visible, otherwise retains the last known target."""
        character = self.manager.character
        city = character.game.state.city        
        target_human, location = self.manager.find_visible_human()

        if target_human:
            self._last_known_target = (target_human, location)
            self.target_block = city.block(*location)
        else:
            self._last_known_target = None

        return self._last_known_target
    
    @last_known_target.setter
    def last_known_target(self, value):
        """Allows explicit assignment when external conditions (like line of sight) dictate it."""
        character = self.manager.character
        city = character.game.state.city        
        self._last_known_target = value
        if value:
            self.target_block = city.block(*value[1])

    def is_complete(self):
        """Returns True if the goal is fully achieved."""
        raise NotImplementedError

    def execute(self):
        """Determines the current decision or picks a new one."""
        
        # If there's no active decision or it's invalid, get a new decision
        next_decision = self.get_next_decision()

        if not self.current_decision or type(self.current_decision) != type(next_decision):
            self.current_decision = next_decision

        if self.current_decision:
            return self.current_decision.execute()

    def get_next_decision(self):
        """Defines the next decision for the goal."""
        for decision_class in self.get_decisions():
            decision = decision_class(self)
            if decision.is_valid():  # Check validity before assigning the decision
                return decision

        return None  # If no valid decisions, goal execution fails

    def get_decisions(self):
        """Returns a list of possible decisions (to be implemented by subclasses)."""
        raise NotImplementedError


class SecureShelterGoal(GoalCommand):
    """Ensures the NPC finds and secures a shelter."""
    def __init__(self, manager):
        super().__init__(manager)

    def is_complete(self):
        """Goal is complete when the shelter is secured."""
        character = self.manager.character
        return character.inside and character.safehouse_secured

    def get_decisions(self):
        """Determines the next step in securing a safehouse."""
        return [ScoutSafehouseDecision, EnterSafehouseDecision, SecureSafehouseDecision]


class SurviveGoal(GoalCommand):
    """Finds a hospital, searches for First Aid Kits, and heals."""
    def __init__(self, manager):
        super().__init__(manager)

    def is_complete(self):
        """Goal is complete when health is restored."""
        character = self.manager.character
        return character.hp == character.max_hp
    
    def get_decisions(self):
        character = self.manager.character

        if character.hp < character.max_hp:
            return [SeekFAKDecision, HealThyselfDecision]


class StandGoal(GoalCommand):
    """Goal to stand up if enough AP available."""
    def __init__(self, manager, target=None):
        super().__init__(manager, target)   

    def is_valid(self):
        """The goal is valid if the character is dead."""
        return self.manager.character.is_dead       

    def get_decisions(self):
        return [StandDecision]


class HuntBrainsGoal(GoalCommand):
    """Zombie goal to find and attack the nearest human, even if they move out of sight."""
    def __init__(self, manager, target=None):
        super().__init__(manager, target)

    def is_valid(self):
        """The goal is valid while a living human is visible or until their last known location is reached."""
        return bool(self.get_decisions()) and not self.manager.character.is_dead

    def get_decisions(self):
        """Determine the next decision based on human visibility and memory."""
        decisions = [AttackBrainsDecision, BreakInsideDecision, PursueBrainsDecision]
        return [decision for decision in decisions if decision(self).is_valid()]


class IdleGoal(GoalCommand):
    """Zombies wander unless they detect a human nearby."""
    def __init__(self, manager, target=None):
        super().__init__(manager, target)

    def is_valid(self):
        """IdleGoal is never truly 'complete' unless interrupted by a human presence."""
        return self.manager.character.is_dead == False

    def get_decisions(self):
        """Choose a movement target, prioritizing lit buildings or wandering randomly."""
        return [BreakInsideDecision, MoveDecision]
