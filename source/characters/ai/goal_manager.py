# goal_manager.py

from data import Goal

class GoalManager:
    """Determines NPC goal based on their current state."""

    @staticmethod
    def determine_goal(character):
        """Returns the NPC's current goal based on its state."""

        # Priority 1: if health drops below 25, switch to SURVIVE
        if character.hp < 25:
            return Goal.SURVIVE

        if not character.has_safehouse:
            return Goal.SECURE_SHELTER
        
