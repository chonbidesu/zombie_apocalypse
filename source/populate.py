import random

from characters import Character
from settings import *
from data import Occupation, HUMAN_OCCUPATIONS


class GenerateNPCs:
    """Class to generate and manage NPCs in the city."""
    def __init__(self, game, total_humans, total_zombies):
        self.game = game
        self.list = []

        self.populate_city(total_humans, total_zombies)

    def populate_city(self, total_humans, total_zombies):
        """Populate the city with NPCs at random locations."""
        for _ in range(total_humans):
            x = random.randint(0, CITY_SIZE - 1)
            y = random.randint(0, CITY_SIZE - 1)
            self.add_npc(x, y, True)

        for _ in range(total_zombies):
            x = random.randint(0, CITY_SIZE - 1)
            y = random.randint(0, CITY_SIZE - 1)
            self.add_npc(x, y, False)

    def add_npc(self, x, y, is_human):
        """Add a single npc at a specific location."""
        # Determine NPC occupation
        if is_human:
            occupation = random.choice(HUMAN_OCCUPATIONS)
        else:
            occupation = Occupation.CORPSE

        if 0 <= x < CITY_SIZE and 0 <= y < CITY_SIZE:
            npc = Character(self.game, occupation, x, y, is_human)
            self.list.append(npc)

    def remove_npc(self, npc):
        """Remove an npc from the city."""
        if npc in self.list:
            self.list.remove(npc)

    def get_npcs_at(self, x, y):
        """Get all NPCs at a specific location."""
        return [npc for npc in self.list if npc.x == x and npc.y == y]

    def take_action(self):
        """Allow all NPCs to take an action, such as moving or attacking."""
        for npc in self.list:
            npc.state.act()