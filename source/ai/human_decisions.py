# decisions.py

from data import Action, ItemType
from .decisions import DecisionCommand


class ScoutSafehouseDecision(DecisionCommand):
    """Find a suitable safehouse based on NPC occupation."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if the NPC does not already have a safehouse."""
        return character.safehouse is None
    
    def execute(self):
        """Finds the best safehouse and moves toward it."""
        pass


class EnterSafehouseDecision(DecisionCommand):
    """Enters the safehouse if standing outside of it."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if the NPC has a safehouse but not inside."""
        safehouse_x = 
        return character.safehouse is not None and not character.inside

    def execute(self, character, executor):
        """Enters the building."""
        return executor.execute(Action.ENTER)
    

class SecureSafehouseDecision(DecisionCommand):
    """Closes the doors after entering the safehouse."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self):
        """Valid if inside the safehouse and the doors are open."""
        return character.inside and not character.safehouse_secured
    
    def execute(self, character, executor):
        """Closes the doors to secure the safehouse."""
        return executor.execute(Action.CLOSE_DOORS)
    

class SeekFAKDecision(DecisionCommand):
    """Searches for a First Aid Kit if health is low."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self, character):
        """Valid if health is low and no FAK in inventory."""
        return character.hp < 25 and ItemType.FIRST_AID_KIT not in character.inventory
    
    def execute(self, character, executor):
        """Searches for a First Aid Kit."""
        return executor.execute(Action.SEARCH)
    

class HealThyselfDecision(DecisionCommand):
    """Uses a First Aid Kit to heal when available."""
    def __init__(self, goal):
        super().__init__(goal)
        self.goal = goal

    def is_valid(self, character):
        """Valid if the NPC has a First Aid Kit and is injured."""
        return character.hp < character.max_hp - 10 and ItemType.FIRST_AID_KIT in character.inventory
    
    def execute(self, character, executor):
        """Uses the First Aid Kit to restore health."""
        fak = character.get_item(ItemType.FIRST_AID_KIT)
        return executor.execute(Action.USE, fak)