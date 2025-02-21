# goals.py

from ai.decisions import ScoutSafehouseDecision, EnterSafehouseDecision, SecureSafehouseDecision, SeekFAKDecision, HealThyselfDecision
from ai.goal_manager import GoalManager
from data import ItemType


class GoalCommand:
    """Base class for all AI goals."""

    def __init__(self):
        self.current_decision = None  # Holds the active decision

    def is_complete(self, character):
        """Returns True if the goal is fully achieved."""
        raise NotImplementedError

    def execute(self, character):
        """Determines the current decision or picks a new one."""
        
        # If there's no active decision or it's complete, get a new decision
        if not self.current_decision or self.current_decision.is_complete(character):
            self.current_decision = self.get_next_decision(character)

        return self.current_decision.execute(character)

    def get_next_decision(self, character):
        """Defines the next decision for the goal (to be implemented by subclasses)."""
        raise NotImplementedError


class SecureShelterGoal(GoalCommand):
    """Ensures the NPC finds and secures a shelter."""

    def is_complete(self, character):
        """Goal is complete when the shelter is secured."""
        return character.inside and character.safehouse_secured

    def get_next_decision(self, character):
        """Determines the next step in securing a safehouse."""
        if not character.has_safehouse:
            return ScoutSafehouseDecision()
        elif not character.inside:
            return EnterSafehouseDecision()
        elif not character.safehouse_secured:
            return SecureSafehouseDecision()
        return None


class SurviveGoal(GoalCommand):
    """Finds a hospital, searches for First Aid Kits, and heals."""

    def is_complete(self, character):
        """Goal is complete when health is restored."""
        return character.hp == character.max_hp
    
    def execute(self, character):
        if character.hp < character.max_hp:
            if ItemType.FIRST_AID_KIT not in character.inventory:
                return SeekFAKDecision() # Find a First Aid Kit
            return HealThyselfDecision() # Heal using a FAK
        
        # Once healing is done, return to previous goal
        return GoalManager.resume_goal(character)