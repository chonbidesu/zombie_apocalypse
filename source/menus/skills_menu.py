# skills_menu.py

import pygame
from settings import *
from data import SKILLS, SkillType, SkillCategory
from ui import Button


class SkillsMenu:
    """A menu displaying the player's skills and skill selection."""
    def __init__(self, game):
        self.game = game
        self.skill_spacing = 30
        self.margin = 100

        # Define columns
        self.column_width = SCREEN_WIDTH // 3
        self.column_x_positions = [self.margin, self.column_width + self.margin, 2 * self.column_width + self.margin]        
        self.category_columns = {
            SkillCategory.CIVILIAN: 0,
            SkillCategory.MILITARY: 1,
            SkillCategory.SCIENCE: 2,
            SkillCategory.ZOMBIE_HUNTER: 1,
            SkillCategory.ZOMBIE: 1,
        }        

    def draw(self, screen):
        """Draws the skills menu."""
        self.skill_slots = self._create_skill_slots()
        self.back_button = self._create_back_button()        
        player = self.game.state.player        

        # Create a dark green background
        screen.fill(DARK_GREEN)
        
        title_text = font_xxl.render("Skills", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 50))

        screen.blit(title_text, title_rect)
        self.back_button.draw(screen)

        xp = player.xp

        # Display XP at the top
        xp_text = font_large.render(f"XP: {xp}", True, (255, 255, 255))
        screen.blit(xp_text, (self.margin, 10))

        # Initialize y-offset for each column
        base_y = SCREEN_HEIGHT * 7 // 40

        # Draw skill categories
        for category in SkillCategory:

            column = self.category_columns.get(category, 0)  # Default to column 0 if not found
            x_pos = self.column_x_positions[column]
            y_offset = base_y
            
            # Handle Zombie Hunter separately to center it in the middle column
            if category == SkillCategory.ZOMBIE_HUNTER:
                y_offset += SCREEN_HEIGHT // 2  # Move to second row of middle column

            # Draw category title
            if (player.is_human and category != SkillCategory.ZOMBIE) or (not player.is_human and category == SkillCategory.ZOMBIE):
                category_text = font_xl.render(category.name.replace("_", " "), True, (200, 200, 0))
                screen.blit(category_text, (x_pos, y_offset))

        # Draw skill slots
        self.skill_slots.update()
        self.skill_slots.draw(screen)

    def _create_back_button(self):
        width = 116
        height = 51
        x, y = SCREEN_WIDTH * 4 // 5, SCREEN_HEIGHT - 100
        back_button = Button('menu_back', width, height)
        back_button.update(x, y)
        button_group = pygame.sprite.GroupSingle()
        button_group.add(back_button)
        return button_group
    
    def _create_skill_slots(self):
        """Create SkillSlots and add to skill_slots group"""
        player = self.game.state.player        
        skill_slots = pygame.sprite.Group()

        if player.is_human:
            acquired_skills = [skill for skill in SKILLS if skill in player.human_skills]
        else:
            acquired_skills = [skill for skill in SKILLS if skill in player.zombie_skills]

        # Initialize y-offset for each column
        base_y = SCREEN_HEIGHT // 4

        for category in SkillCategory:
            column = self.category_columns.get(category, 0)
            x_pos = self.column_x_positions[column]
            y_offset = base_y
            
            # Handle Zombie Hunter separately to center it in the middle column
            if category == SkillCategory.ZOMBIE_HUNTER:
                y_offset += SCREEN_HEIGHT // 2  # Move to second row of middle column

            for skill in SKILLS:
                properties = SKILLS[skill]
                if (player.is_human and properties.skill_category != SkillCategory.ZOMBIE) or (not player.is_human and properties.skill_category == SkillCategory.ZOMBIE):
                    if properties.skill_category == category:
                        skill_slot = SkillSlot(
                            skill, properties, x_pos, y_offset, self.column_width - 20,
                            acquired=(skill in acquired_skills)
                        )
                        skill_slots.add(skill_slot)
                        y_offset += self.skill_spacing     
        
        return skill_slots
    

class SkillSlot(pygame.sprite.Sprite):
    """A skill slot representing a selectable skill."""
    def __init__(self, skill, properties, x, y, width, acquired=False):
        super().__init__()
        self.skill = skill
        self.properties = properties
        self.acquired = acquired
        self.selected = False

        self.width = width
        self.height = 30
        self.rect = pygame.Rect(x, y, width, 30)
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    def toggle_selection(self):
        """Toggle the selected state of the skill slot."""
        self.selected = not self.selected
        self.update()

    def update(self):
        """Update the skill slot appearance."""
        self.image.fill((0, 0, 0, 0))

        border_colour = WHITE if self.selected else (0, 0, 0)
        text = font_large.render(self.properties.skill_type.replace("_", " ").title(), True, WHITE)

        # Draw selection border if selected
        if self.selected:
            pygame.draw.rect(self.image, border_colour, (0, 0, self.width, self.height), 2)

        self.image.blit(text, (10, 5))
