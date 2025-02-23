# human_state.py

from characters.state import State


class Human(State):
    """Represents the human state."""
    def __init__(self, character):
        super().__init__(character)
        self.character = character
   
    def update_name(self):
        """Updates the character's name."""
        self.character.current_name = f"{self.character.name.first_name} {self.character.name.last_name}"
                                