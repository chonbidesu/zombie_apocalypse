# decision_manager.py

from data import Goal
from ai.commands import ScoutSafehouse, EnterSafehouse, SecureSafehouse, SeekFAK, HealThyself


class DecisionManager:
    """Determines which decision an NPC should take based on its goal."""

    # Mapping of goals to decision sequences
    goal_decisions = {
        Goal.SECURE_SHELTER: [
            ScoutSafehouse(),
            EnterSafehouse(),
            SecureSafehouse(),
        ],
        Goal.SURVIVE: [
            SeekFAK(),
            HealThyself(),
        ]
    }

    @staticmethod
    def determine_decision(character):
        """Returns the first valid decision for the NPC based on their goal."""

        # Get the character's current goal
        goal = character.current_goal

        # Get decision sequence for this goal
        decisions = DecisionManager.goal_decisions.get(goal, [])

        for decision in decisions:
            if decision.is_valid(character):
                return decision
        
        return None # No valid decision found