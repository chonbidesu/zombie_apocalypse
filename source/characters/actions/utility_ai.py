# utility_ai.py

from data import Decision, Goal


class UtilityAI:
    def __init__(self, character):
        self.character = character

        self.goal_decisions = {
            Decision.SCOUT_SAFEHOUSE: self.score_scout_safehouse(),
            Decision.ATTACK_TO_KILL: self.score_attack_to_kill(),
            Decision.SEEK_ITEMS: self.score_seek_items(),
            Decision.SECURE_SAFEHOUSE: self.score_secure_safehouse(),
            Decision.BARRICADE_SAFEHOUSE: self.score_barricade_safehouse(),
            Decision.ENTER_SAFEHOUSE: self.score_enter_safehouse(),
            Decision.DEFEND_SAFEHOUSE: self.score_defend_safehouse(),
            Decision.POWER_SAFEHOUSE: self.score_power_safehouse(),
            Decision.ARM_THYSELF: self.score_arm_thyself(),
            Decision.HEAL_THYSELF: self.score_heal_thyself(),
            Decision.DUMP_BODIES: self.score_dump_bodies(),
            Decision.HUNT: self.score_hunt(),
            Decision.PATROL: self.score_patrol(),
            Decision.FLEE: self.score_flee(),
        }

        # Increase weight for decisions that align with current goal
        if self.character.current_goal == Goal.SECURE_SHELTER:
            scores[Decision.SCOUT_SAFEHOUSE] += 30
        elif self.character.current_goal == Goal.LEVEL_UP:
            scores[Decision.HUNT] += 40
        elif self.character.current_goal == Goal.SURVIVE:
            scores[Decision.HEAL_THYSELF] += 40