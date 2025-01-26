import random

from npc import NPC
from settings import *

class GenerateZombies:
    """Class to generate and manage zombies in the city."""
    def __init__(self, player, city, chat_history, total_zombies=100):
        """
        Initialize the GenerateZombies class.
        """
        self.city = city
        self.player = player
        self.chat_history = chat_history
        self.total_zombies = total_zombies
        self.list = []

        self.populate_city()

    def populate_city(self):
        """Populate the city with zombies at random locations."""
        for _ in range(self.total_zombies):
            x = random.randint(0, CITY_SIZE - 1)
            y = random.randint(0, CITY_SIZE - 1)
            self.add_zombie(x, y)

    def add_zombie(self, x, y):
        """Add a single zombie at a specific location."""
        if 0 <= x < CITY_SIZE and 0 <= y < CITY_SIZE:
            type = random.choice(list(NPCType))
            zombie = NPC(self.player, self.city, self.chat_history, x, y, type=type, is_human=False)
            block = self.city.block(x, y)
            block.current_zombies += 1
            self.list.append(zombie)

    def remove_zombie(self, zombie):
        """Remove a zombie from the city."""
        if zombie in self.list:
            x, y = zombie.location[0], zombie.location[1]
            block = self.city.block(x, y)
            block.current_zombies -= 1
            self.list.remove(zombie)

    def get_zombies_at(self, x, y):
        """Get all zombies at a specific location."""
        return [zombie for zombie in self.list if zombie.x == x and zombie.y == y]

    def move_zombies(self):
        """Allow all zombies to take an action, such as moving or attacking."""
        for zombie in self.list:
            zombie.take_action()
