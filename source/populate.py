import random

from npc import NPC
from settings import *

class GenerateCharacters:
    """Class to generate and manage NPCs in the city."""
    def __init__(self, game, total_humans, total_zombies):
        self.game = game
        self.list = []

        self.populate_city(total_humans, total_zombies)

    def populate_city(self, total_humans, total_zombies):
        """Populate the city with NPCs at random locations."""
        for _ in range(self.total_npcs):
            x = random.randint(0, CITY_SIZE - 1)
            y = random.randint(0, CITY_SIZE - 1)
            self.add_npc(x, y)

    def add_npc(self, x, y, state):
        """Add a single npc at a specific location."""
        if 0 <= x < CITY_SIZE and 0 <= y < CITY_SIZE:
            type = random.choice(list(NPCType))
            npc = NPC(self.game, x, y, type=type, is_human=self.is_human)
            block = self.game.city.block(x, y)
            if self.is_human:
                block.current_humans += 1
            else:
                block.current_zombies += 1
            self.list.append(npc)

    def remove_npc(self, npc):
        """Remove a zombie from the city."""
        if npc in self.list:
            x, y = npc.location[0], npc.location[1]
            block = self.game.city.block(x, y)
            if self.is_human:
                block.current_humans -= 1
            else:
                block.current_zombies -= 1
            self.list.remove(npc)

    def get_npcs_at(self, x, y):
        """Get all NPCs at a specific location."""
        return [npc for npc in self.list if npc.x == x and npc.y == y]

    def move_npcs(self):
        """Allow all NPCs to take an action, such as moving or attacking."""
        for npc in self.list:
            npc.take_action()