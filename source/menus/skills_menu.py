# skills_menu.py

import pygame
from settings import *
from data import SKILLS, SkillType, SkillCategory
from ui import Button


class SkillsMenu:
    """A menu displaying the player's skills and skill selection."""
    def __init__(self, game):
        self.game = game
        self.back_button = self._create_back_button()
        self.skill_spacing = 30
        self.margin = 100

    def draw(self, screen):
        """Draws the skills menu."""
        # Create a dark green background
        screen.fill(DARK_GREEN)
        
        title_text = font_xxl.render("Skills", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))

        screen.blit(title_text, title_rect)
        self.back_button.draw(screen)

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

        # Display XP at the top
        xp_text = font_large.render(f"XP: {xp}", True, (255, 255, 255))
        screen.blit(xp_text, (self.margin, 10))

        # Display skills by category
        # Define columns
        column_width = SCREEN_WIDTH // 3
        column_x_positions = [self.margin, column_width + self.margin, 2 * column_width + self.margin]

        # Define category-to-column mapping
        category_columns = {
            SkillCategory.CIVILIAN: 0,  # Left column
            SkillCategory.MILITARY: 1,  # Middle column
            SkillCategory.SCIENCE: 2,   # Right column
            SkillCategory.ZOMBIE_HUNTER: 1,  # Middle column (second row, centered)
            SkillCategory.ZOMBIE: 0  # If zombie skills are displayed later
        }

        # Initialize y-offsets for each column
        y_offsets = [140, 140, 140]

        # Display skills by category
        for category, skills in skill_categories.items():
            column = category_columns.get(category, 0)  # Default to column 0 if not found
            x_pos = column_x_positions[column]
            
            # Handle Zombie Hunter separately to center it in the middle column
            if category == SkillCategory.ZOMBIE_HUNTER:
                y_offsets[1] += 50  # Move to second row of middle column

            # Draw category title
            category_text = font_xl.render(category.name.replace("_", " "), True, (200, 200, 0))
            screen.blit(category_text, (x_pos, y_offsets[column]))
            y_offsets[column] += category_text.get_height()  # Space after category title

            for skill, properties in skills:
                skill_text = properties.skill_type.replace("_", " ").title()
                color = (200, 200, 200) if skill in acquired_skills else (255, 255, 255)

                skill_label = font_large.render(skill_text, True, color)
                screen.blit(skill_label, (x_pos, y_offsets[column]))

                # Show 'Gain Skill' button if the skill is not acquired and player has enough XP
                if skill not in acquired_skills and xp >= 100:
                    gain_button_rect = pygame.Rect(x_pos + 200, y_offsets[column] - 5, 80, 20)
                    pygame.draw.rect(screen, (0, 150, 0), gain_button_rect)  # Green button
                    button_text = self.button_font.render("Gain", True, (255, 255, 255))
                    screen.blit(button_text, (gain_button_rect.x + 15, gain_button_rect.y + 2))
                
                y_offsets[column] += self.skill_spacing  # Move to next skill

    def _create_back_button(self):
        width = 116
        height = 51
        x, y = SCREEN_WIDTH * 4 // 5, SCREEN_HEIGHT - 100
        back_button = Button('menu_back', width, height)
        back_button.update(x, y)
        button_group = pygame.sprite.GroupSingle()
        button_group.add(back_button)
        return button_group