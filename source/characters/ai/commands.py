# commands.py

from data import Action, ItemType


class DecisionCommand:
    """Base class for all AI decisions."""

    def is_valid(self, character):
        """Checks if this decision is valid for the character."""
        raise NotImplementedError("Subclasses must implement is_valid().")
    
    def execute(self, character, executor):
        """Executes the decision's action using ActionExecutor."""
        raise NotImplementedError("Subclasses must implement execute().")


class ScoutSafehouse(DecisionCommand):
    """Find a suitable safehouse based on NPC occupation."""

    def is_valid(self, character):
        """Valid if the NPC does not already have a safehouse."""
        return not character.has_safehouse
    
    def execute(self, character, executor):
        """Finds the best safehouse and moves toward it."""
        pass


class EnterSafehouse(DecisionCommand):
    """Enters the safehouse if standing outside of it."""

    def is_valid(self, character):
        """Valid if the NPC is at the safehouse but not inside."""

    def execute(self, character, executor):
        """Enters the building."""
        return executor.execute(Action.ENTER)
    

class SecureSafehouse(DecisionCommand):
    """Closes the doors after entering the safehouse."""

    def is_valid(self, character):
        """Valid if inside the safehouse and the doors are open."""
        return character.inside and not character.safehouse_secured
    
    def execute(self, character, executor):
        """Closes the doors to secure the safehouse."""
        return executor.execute(Action.CLOSE_DOORS)
    

class SeekFAK(DecisionCommand):
    """Searches for a First Aid Kit if health is low."""

    def is_valid(self, character):
        """Valid if health is low and no FAK in inventory."""
        return character.hp < 25 and ItemType.FIRST_AID_KIT not in character.inventory
    
    def execute(self, character, executor):
        """Searches for a First Aid Kit."""
        return executor.execute(Action.SEARCH)
    

class HealThyself(DecisionCommand):
    """Uses a First Aid Kit to heal when available."""

    def is_valid(self, character):
        """Valid if the NPC has a First Aid Kit and is injured."""
        return character.hp < character.max_hp - 10 and ItemType.FIRST_AID_KIT in character.inventory
    
    def execute(self, character, executor):
        """Uses the First Aid Kit to restore health."""
        fak = character.get_item(ItemType.FIRST_AID_KIT)
        return executor.execute(Action.USE, fak)