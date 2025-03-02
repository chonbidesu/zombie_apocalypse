# goals.py

import random

from .human_decisions import ScoutSafehouseDecision, EnterSafehouseDecision, SecureSafehouseDecision, SeekFAKDecision, HealThyselfDecision
from .zombie_decisions import PursueBrainsDecision, AttackBrainsDecision, ChaseBrainsDecision, BreakInsideDecision, MoveDecision
from .decisions import StandDecision
from data import BLOCKS


class GoalCommand:
    """Base class for all AI goals."""

    def __init__(self, manager):
        self.manager = manager
        self.current_decision = None  # Holds the active decision

    def is_complete(self):
        """Returns True if the goal is fully achieved."""
        raise NotImplementedError

    def execute(self):
        """Determines the current decision or picks a new one."""
        
        # If there's no active decision or it's invalid, get a new decision
        if not self.current_decision or not self.current_decision.is_valid():
            self.current_decision = self.get_next_decision()

        if self.current_decision:
            return self.current_decision.execute()

    def get_next_decision(self):
        """Defines the next decision for the goal."""
        for decision_class in self.get_decisions():
            decision = decision_class(self)
            if decision.is_valid():  # Check validity before assigning the decision
                return decision

        return None  # If no valid decisions, goal execution fails

    def get_decisions(self):
        """Returns a list of possible decisions (to be implemented by subclasses)."""
        raise NotImplementedError


class SecureShelterGoal(GoalCommand):
    """Ensures the NPC finds and secures a shelter."""
    def __init__(self, manager):
        super().__init__(manager)

    def is_complete(self):
        """Goal is complete when the shelter is secured."""
        character = self.manager.character
        return character.inside and character.safehouse_secured

    def get_decisions(self):
        """Determines the next step in securing a safehouse."""
        return [ScoutSafehouseDecision, EnterSafehouseDecision, SecureSafehouseDecision]


class SurviveGoal(GoalCommand):
    """Finds a hospital, searches for First Aid Kits, and heals."""
    def __init__(self, manager):
        super().__init__(manager)

    def is_complete(self):
        """Goal is complete when health is restored."""
        character = self.manager.character
        return character.hp == character.max_hp
    
    def get_decisions(self):
        character = self.manager.character

        if character.hp < character.max_hp:
            return [SeekFAKDecision, HealThyselfDecision]


class StandGoal(GoalCommand):
    """Goal to stand up if enough AP available."""
    def __init__(self, manager):
        super().__init__(manager)   
        self.last_known_target = None 

    def is_valid(self):
        """The goal is valid if the character is dead."""
        return self.manager.character.is_dead       

    def get_decisions(self):
        return [StandDecision]


class HuntBrainsGoal(GoalCommand):
    """Zombie goal to find and attack the nearest human, even if they move out of sight."""
    def __init__(self, manager, target=None):
        super().__init__(manager)
        self._last_known_target = target  # Stores (human, last_seen_location)
        self._target_block = None

    @property
    def last_known_target(self):
        """Dynamically updates if a human is visible, otherwise retains the last known target."""
        target_human, location = self.manager.find_visible_human()

        if target_human:
            self._last_known_target = (target_human, location)

        return self._last_known_target
    
    @property
    def target_block(self):
        character = self.manager.character
        city = character.game.state.city        
        _, location = self.last_known_target
        self._target_block = city.block(*location)
        return self._target_block

    def is_valid(self):
        """The goal is valid while a living human is visible or until their last known location is reached."""
        return self.last_known_target and all(value for value in self.last_known_target) and not self.manager.character.is_dead

    def get_decisions(self):
        """Determine the next decision based on human visibility and memory."""
        character = self.manager.character
        city = character.game.state.city

        # If no visible human, but we have a last known location, chase them
        if self.last_known_target:
            target_human, _ = self.last_known_target

            # If the human entered a building, attempt to break in
            if target_human.inside and self.target_block.doors_closed:
                return [BreakInsideDecision]
            
            else:

                # Attack if in melee range, otherwise pursue
                return [AttackBrainsDecision, PursueBrainsDecision, ChaseBrainsDecision]

        return []


class IdleGoal(GoalCommand):
    """Zombies wander unless they detect a human nearby."""
    def __init__(self, manager, target=None):
        super().__init__(manager)
        self.last_known_target = target  # Stores (human, last_seen_location)
        self.target_block = None

    def is_valid(self):
        """WanderGoal is never truly 'complete' unless interrupted by a human presence."""
        return self.last_known_target is None or any(value is None for value in self.last_known_target) and not self.manager.character.is_dead

    def get_decisions(self):
        """Choose a movement target, prioritizing lit buildings or wandering randomly."""
        character = self.manager.character

        # Get nearby locations
        adjacent_locations = character.helper.get_adjacent_locations()
        city = character.game.state.city

        # Check if current building is lit
        x, y = character.location
        block = city.block(x, y)
        properties = BLOCKS[block.type]

        if properties.is_building and block.lights_on:
            self.target_block = block
            return [BreakInsideDecision]

        # Prioritize moving toward lit buildings
        lit_buildings = [
            loc for loc in adjacent_locations
            if hasattr(city.block(*loc), 'lights_on') and city.block(*loc).lights_on
        ]

        if lit_buildings:
            self.target_block = city.block(random.choice(lit_buildings))
        else:
            self.target_block = None

        # Move or wander
        return [MoveDecision]
