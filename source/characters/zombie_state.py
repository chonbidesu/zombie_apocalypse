# zombie_state.py

import random
from dataclasses import dataclass

from characters.state import State
from settings import *


@dataclass
class ZombieWeapon:
    name: str
    attack: int
    damage: int

    @classmethod
    def choose(cls):
        """Randomly select hands or teeth and return a ZombieWeapon instance."""
        attack_type, stats = random.choice(list(ZOMBIE_ATTACKS.items()))
        return cls(name=attack_type, attack=stats["attack"], damage=stats["damage"])


class Zombie(State):
    """Represents the zombie state."""
    def __init__(self, character):
        super().__init__(character)     

    def update_name(self):
        """Updates the character's name."""
        self.character.current_name = f"{self.character.name.zombie_adjective} {self.character.name.first_name}"