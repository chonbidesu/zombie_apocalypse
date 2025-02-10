# skills_panel.py

import pygame
from settings import *
from data import SKILLS, SkillType, SkillCategory


class SkillsPanel:
    """A UI panel displaying the player's skills and skill selection."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.width = 300
        self.height = 400
        self.panel_rect = pygame.Rect(50, 50, self.width, self.height)
        self.skill_spacing = 30
        self.margin = 10

    def draw(self):
        """Draws the skills panel."""
        player = self.game.state.player
        xp = player.xp

        if player.is_human:
            skill_categories = {
                SkillCategory.CIVILIAN: [],
                SkillCategory.MILITARY: [],
                SkillCategory.SCIENCE: [],
                SkillCategory.ZOMBIE_HUNTER: []
            }
            acquired_skills = player.human_skills
        else:
            skill_categories = {SkillCategory.ZOMBIE: []}
            acquired_skills = player.zombie_skills
        
        # Organize skills into categories
        for skill, properties in SKILLS.items():
            if properties.skill_category in skill_categories:
                skill_categories[properties.skill_category].append((skill, properties))

        # Draw panel background
        pygame.draw.rect(self.screen, (50, 50, 50), self.panel_rect)  # Dark grey panel
        pygame.draw.rect(self.screen, (255, 255, 255), self.panel_rect, 2)  # White border

        # Display XP at the top
        xp_text = self.font.render(f"XP: {xp}", True, (255, 255, 255))
        self.screen.blit(xp_text, (self.panel_rect.x + self.margin, self.panel_rect.y + self.margin))

        # Display skills by category
        y_offset = self.panel_rect.y + 40  # Offset from top for XP display
        for category, skills in skill_categories.items():
            category_text = self.font.render(category.name.replace("_", " "), True, (200, 200, 0))  # Yellowish color
            self.screen.blit(category_text, (self.panel_rect.x + self.margin, y_offset))
            y_offset += 25  # Space after category title

            for skill, properties in skills:
                skill_text = properties.skill_type.replace("_", " ").title()
                color = (200, 200, 200) if skill in acquired_skills else (255, 255, 255)  # Greyed out if acquired

                skill_label = self.font.render(skill_text, True, color)
                self.screen.blit(skill_label, (self.panel_rect.x + self.margin, y_offset))

                # Show 'Gain Skill' button if the skill is not acquired and player has enough XP
                if skill not in acquired_skills and xp >= 100:
                    gain_button_rect = pygame.Rect(self.panel_rect.x + 200, y_offset - 5, 80, 20)
                    pygame.draw.rect(self.screen, (0, 150, 0), gain_button_rect)  # Green button
                    button_text = self.button_font.render("Gain", True, (255, 255, 255))
                    self.screen.blit(button_text, (gain_button_rect.x + 15, gain_button_rect.y + 2))
                
                y_offset += self.skill_spacing