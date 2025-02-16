# skills_menu.py

import pygame

from settings import *
from data import SKILLS, SkillType, SkillCategory, OCCUPATIONS, OccupationCategory
from ui import Button, WrapText


class SkillsMenu:
    """A menu displaying the player's skills and skill selection."""
    def __init__(self, game):
        self.game = game
        self.skill_spacing = 35
        self.margin = 75
        self.selected_skill = None

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
        player = self.game.state.player        

        # Create a dark green background
        screen.fill(DARK_GREEN)
        
        title_text = font_xxl.render("Skills", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 75))

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

        # Draw info panel if a skill is selected
        if self.selected_skill:
            self._draw_info_panel(screen)

    def update(self):
        """Deselect all other skills when a new one is selected."""
        for skill_slot in self.skill_slots:
            skill_slot.selected = (skill_slot == self.selected_skill)
            skill_slot.update()

    def _draw_info_panel(self, screen):
        """Draws the information panel for the selected skill."""
        x, y = 50, SCREEN_HEIGHT // 2
        width, height = SCREEN_WIDTH // 3, SCREEN_HEIGHT // 2 - 40
        player = self.game.state.player

        # Draw border
        pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)

        # Draw skill name
        properties = SKILLS[self.selected_skill.skill]
        skill_name = font_large.render(properties.skill_type, True, WHITE)
        skill_name_width = skill_name.get_width()
        screen.blit(skill_name, (x + width // 2 - skill_name_width // 2, y + 10))

        # Draw skill description
        wrapped_description = WrapText(properties.description, font_large, width - 20)
        y_offset = y + 50
        for line in wrapped_description.lines:
            text_surface = font_large.render(line, True, WHITE)
            screen.blit(text_surface, (x + 10, y_offset))
            y_offset += 20

        # Determine XP cost
        xp_cost = self._get_skill_xp_cost(self.selected_skill.skill)

        # Skill acquisition rules
        if xp_cost is None:
            status_text = "Requires Level 10+"
            colour = RED
        elif self.selected_skill.skill in player.human_skills or self.selected_skill.skill in player.zombie_skills:
            status_text = "Skill already learned"
            colour = LIGHT_GRAY
        elif player.xp < xp_cost:
            status_text = f"Requires {xp_cost} XP"
            colour = RED
        else:
            self._draw_gain_button(screen, x, y, width, xp_cost)
            return
        
        # Draw status text
        status_surface = font_large.render(status_text, True, colour)
        status_rect = status_surface.get_rect(center=(x + width // 2, y + height - 40))
        screen.blit(status_surface, status_rect)

    def _draw_gain_button(self, screen, x, y, width, xp_cost):
        """Draw the 'GAIN SKILL' button at the bottom of the info panel."""
        button_width, button_height = 120, 40
        button_x = x + width // 2 - button_width // 2
        button_y = y + width - 60

        self.gain_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)

        # Draw button
        pygame.draw.rect(screen, (0, 150, 0), self.gain_button_rect)
        pygame.draw.rect(screen, WHITE, self.gain_button_rect, 2)

        # Draw button text
        text_surface = font_large.render(f"GAIN SKILL", True, WHITE)
        text_rect = text_surface.get_rect(center=self.gain_button_rect.center)
        screen.blit(text_surface, text_rect)

    def _get_skill_xp_cost(self, skill):
        """Calculate the XP cost for the given skill based on the player's occupation."""
        player = self.game.state.player
        skill_category = SKILLS[skill].skill_category
        occupation_category = OCCUPATIONS[player.occupation].occupation_category

        if skill_category == SkillCategory.CIVILIAN:
            return 100 # Fixed cost for civilian skills
        
        elif skill_category == SkillCategory.MILITARY:
            if occupation_category == OccupationCategory.MILITARY:
                return 75
            elif occupation_category == OccupationCategory.CIVILIAN:
                return 100
            else: # Science occupation
                return 150
            
        elif skill_category == SkillCategory.SCIENCE:
            if occupation_category == OccupationCategory.SCIENCE:
                return 75
            elif occupation_category == OccupationCategory.CIVILIAN:
                return 100
            else: # Military occupation
                return 150
            
        elif skill_category == SkillCategory.ZOMBIE_HUNTER:
            if player.level >= 10: # Requires level 10
                return 100
            else:
                return None
            
        elif skill_category == SkillCategory.ZOMBIE:
            return 100 # Fixed cost for zombie skills

    def _gain_skill(self):
        """Grants the selected skill if the player has enough XP."""
        if not self.selected_skill:
            return
        
        player = self.game.state.player
        skill = self.selected_skill.skill
        xp_cost = self._get_skill_xp_cost(skill)

        player.xp -= xp_cost
        player.add_skill(skill)

    def create_resources(self):
        self.skill_slots = self._create_skill_slots()
        self.back_button = self._create_back_button()         

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

        self.checkmark = pygame.image.load(ResourcePath("assets/checkmark.png").path).convert_alpha()
        self.checkmark = pygame.transform.scale(self.checkmark, (16, 16))

    def update(self):
        """Update the skill slot appearance."""
        self.image.fill((0, 0, 0, 0))

        border_colour = WHITE if self.selected else (0, 0, 0)
        text = font_large.render(self.properties.skill_type, True, WHITE)

        # Draw selection border if selected
        if self.selected:
            pygame.draw.rect(self.image, border_colour, (0, 0, self.width - 100, self.height), 2)

        self.image.blit(text, (10, 5))

        if self.acquired:
            self.image.blit(self.checkmark, (self.width - 20, 5))

    def handle_event(self, event, skills_menu):
        """Handle mouse events to change button state."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                skills_menu.selected_skill = self if not self.selected else None
                skills_menu.update()
