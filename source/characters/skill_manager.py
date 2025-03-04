# skill_manager.py

import random

from data import OCCUPATIONS, OccupationCategory, SKILLS, SkillCategory


class SkillManager:
    """Manages skill selection and acquisition for NPCs."""
    
    def __init__(self, character):
        self.character = character
        self.selected_skill = None  # Skill NPC is currently trying to learn
    
    def select_skill(self):
        """NPC selects a skill they want to learn and retains it until they have enough XP."""
        if self.selected_skill is None:  # Only select if no skill is currently chosen
            occupation_category = OCCUPATIONS[self.character.occupation].occupation_category

            if self.character.is_human:
                skills = [
                    skill for skill, properties in SKILLS.items()
                    if properties.skill_category != SkillCategory.ZOMBIE and
                    (properties.skill_category != SkillCategory.ZOMBIE_HUNTER or self.character.level >= 10)
                ]
            else:
                skills = [
                    skill for skill, properties in SKILLS.items()
                    if properties.skill_category == SkillCategory.ZOMBIE
                ]

            acquired_skills = set(self.character.human_skills) if self.character.is_human else set(self.character.zombie_skills)

            # Filter skills where prerequisites are met
            skills_with_prereqs_met = [
                skill for skill in skills
                if all(prerequisite in acquired_skills for prerequisite in SKILLS[skill].prerequisite_skills)
            ]

            occupation_skills = [
                skill for skill, properties in SKILLS.items()
                if skill in skills_with_prereqs_met and properties.skill_category == occupation_category
            ]

            # Prioritize occupational skills
            if occupation_skills:
                self.selected_skill = random.choice(occupation_skills) if random.random() < 0.75 else random.choice(skills_with_prereqs_met)
            elif skills_with_prereqs_met:
                self.selected_skill = random.choice(skills_with_prereqs_met)

    def get_skill_xp_cost(self):
        """Get the XP cost for the currently selected skill."""
        if self.selected_skill is None:
            return None
        
        skill_category = SKILLS[self.selected_skill].skill_category
        occupation_category = OCCUPATIONS[self.character.occupation].occupation_category

        if skill_category == SkillCategory.CIVILIAN:
            return 100  # Fixed cost for civilian skills
        elif skill_category == SkillCategory.MILITARY:
            return 75 if occupation_category == OccupationCategory.MILITARY else 100 if occupation_category == OccupationCategory.CIVILIAN else 150
        elif skill_category == SkillCategory.SCIENCE:
            return 75 if occupation_category == OccupationCategory.SCIENCE else 100 if occupation_category == OccupationCategory.CIVILIAN else 150
        elif skill_category in (SkillCategory.ZOMBIE_HUNTER, SkillCategory.ZOMBIE):
            return 100  # Fixed cost

    def attempt_learn_skill(self):
        """Attempt to learn the selected skill if enough XP is available."""
        if self.selected_skill is None:
            return
        
        cost = self.get_skill_xp_cost()
        if cost is not None and self.character.xp >= cost:
            self.character.xp -= cost
            if self.character.is_human:
                self.character.human_skills.append(self.selected_skill)
            else:
                self.character.zombie_skills.append(self.selected_skill)

            if self.character.game.debug:
                print(f"{self.character.current_name} learned {self.selected_skill} for {cost} XP.")

            self.selected_skill = None  # Reset after learning
