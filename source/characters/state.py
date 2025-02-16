# state.py

from dataclasses import dataclass
import random

from data import Action, SKILLS, SkillType, SkillCategory, OCCUPATIONS, OccupationCategory
from settings import *


@dataclass
class MoveTarget:
    dx: int = 0
    dy: int = 0


@dataclass
class Result:
    action: Action
    target: object = None


@dataclass
class BlockNPCs:
    x: int
    y: int
    inside: bool
    living_humans: list
    living_zombies: list
    dead_bodies: list
    dead_zombies: list
    revivifying_bodies: list


class State:
    """Represents an NPC state."""
    def __init__(self, game, character):
        self.game = game
        self.character = character # Reference the parent character
        self.current_target = None
        self.next_action = None
        self.selected_skill = None

    def get_action(self):
        """Determines next behaviour and stores the action."""
        self.next_action = self._determine_behaviour()

    def act(self):
        """Execute AI behaviour."""
        # Only act if action points are available
        if self.character.ap < 1:
            return False
        
        # Execute action if one was determined
        if self.next_action:
            action_result = self.character.action.execute(self.next_action.action, self.next_action.target)
            if action_result:
                if action_result.attacked and self.next_action.target == self.game.state.player:
                    self.game.chat_history.append(action_result.attacked)
                elif action_result.witness and self.character.location == self.game.state.player.location:
                    if self.character.inside == self.game.state.player.inside:
                        self.game.chat_history.append(action_result.witness) 
                        if action_result.sfx:
                            pygame.mixer.Sound.play(self.game.sounds[action_result.sfx])                        
                    else:
                        if self.next_action.action == Action.DECADE:
                            self.game.chat_history.append(action_result.witness)
                            if action_result.sfx:
                                pygame.mixer.Sound.play(self.game.sounds[action_result.sfx])                               

    def filter_characters_at_location(self, x, y, inside=False, include_player=True):
        """Retrieve all characters at a given location and categorize them."""
        player = self.game.state.player
        characters_here = [
            npc for npc in self.game.state.npcs.list
            if npc.location == (x, y) and npc.inside == inside
        ]

        if include_player:
            # Add the player to the list if they are at location
            if player.location == (x, y) and player.inside == inside:
                characters_here.append(player)

        zombies_here = [character for character in characters_here if not character.is_human]
        humans_here = [character for character in characters_here if character.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [c for c in characters_here if c.is_dead]
        dead_zombies = [z for z in zombies_here if z.is_dead]
        revivifying_bodies = [h for h in humans_here if h.is_dead]

        return BlockNPCs(x, y, inside, living_humans, living_zombies, dead_bodies, dead_zombies, revivifying_bodies)                      
    
    def get_adjacent_locations(self):
        """Returns a list of (x, y) coordinates for the 8 adjacent blocks."""
        x, y = self.character.location
        adjacent_locations = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), # Top row
            (x - 1, y),                 (x + 1, y),     # Middle row
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)  # Bottom row
        ]
        valid_locations = []

        # Filter only valid locations in bounds
        for location in adjacent_locations:
            x, y = location
            if 0 < x < CITY_SIZE - 1 and 0 < y < CITY_SIZE - 1:
                valid_locations.append(location)
        return valid_locations
    
    def _make_choice(self, actions):
        """Choose an action based on weighted probabilities."""
        valid_actions = [(action, weight) for action, weight in actions.items() if weight > 0]
        if not valid_actions:
            return None # No valid actions
        
        choices, weights = zip(*valid_actions)
        return random.choices(choices, weights=weights, k=1)[0] # Select an action    
    
    def gain_skill(self):
        """If enough XP available, gain a skill."""
        if self.character.is_dead:
            return
        
        if not self.selected_skill:
            self.selected_skill = self.select_skill()

        if self.selected_skill:
            skill_xp_cost = self._get_skill_xp_cost(self.selected_skill)

            if self.character.xp >= skill_xp_cost:
                self.character.add_skill(self.selected_skill)
                print(f"NPC gained skill: {self.selected_skill}")
                self.character.xp -= skill_xp_cost
                self.selected_skill = None

    def select_skill(self):
        """Selects a skill to learn."""
        occupation_category = OCCUPATIONS[self.character.occupation].occupation_category

        if self.character.is_human:
            skills = [skill for skill, properties in SKILLS.items() if properties.skill_category != SkillCategory.ZOMBIE]
        else:
            skills = [skill for skill, properties in SKILLS.items() if properties.skill_category == SkillCategory.ZOMBIE]           

        acquired_skills = [skill for skill in self.character.human_skills] \
            if self.character.is_human else \
            [skill for skill in self.character.zombie_skills]

        skills_with_prereqs_met = [
            skill for skill in skills if all(prerequisite in acquired_skills for prerequisite in SKILLS[skill].prerequisite_skills)
        ]
        occupation_skills = [skill for skill, properties in SKILLS.items() if skill in skills_with_prereqs_met and properties.skill_category == occupation_category]

        # Learn occupation skills first
        for skill in occupation_skills:
            if skill not in acquired_skills:
                return skill
        
        for skill in skills_with_prereqs_met:
            if skill not in acquired_skills:
                return skill
            
        return None

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