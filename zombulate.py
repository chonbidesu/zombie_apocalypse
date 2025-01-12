import random

from zombie import Zombie
from settings import *

class GenerateZombies:
    """
    Class to generate and manage zombies in the city.
    """

    def __init__(self, player, city, chat_history, total_zombies=100):
        """
        Initialize the GenerateZombies class.

        Args:
            player (Player): The player object.
            city (City): The city object.
            total_zombies (int): Total number of zombies to generate in the city.
        """
        self.city = city
        self.player = player
        self.chat_history = chat_history
        self.total_zombies = total_zombies
        self.list = []

        self.populate_city()

    def populate_city(self):
        """
        Populate the city with zombies at random locations.
        """
        for _ in range(self.total_zombies):
            x = random.randint(0, CITY_SIZE - 1)
            y = random.randint(0, CITY_SIZE - 1)
            self.add_zombie(x, y)

    def add_zombie(self, x, y):
        """
        Add a single zombie at a specific location.

        Args:
            x (int): X-coordinate of the zombie's location.
            y (int): Y-coordinate of the zombie's location.
        """
        if 0 <= x < CITY_SIZE and 0 <= y < CITY_SIZE:
            zombie = Zombie(self.player, self.city, self.chat_history, x, y)
            block = self.city.block(x, y)
            block.current_zombies += 1
            self.list.append(zombie)

    def remove_zombie(self, zombie):
        """
        Remove a zombie from the city.

        Args:
            zombie (Zombie): The zombie object to remove.
        """
        if zombie in self.list:
            x, y = zombie.location[0], zombie.location[1]
            block = self.city.block(x, y)
            block.current_zombies -= 1
            self.list.remove(zombie)

    def get_zombies_at(self, x, y):
        """
        Get all zombies at a specific location.

        Args:
            x (int): X-coordinate of the location.
            y (int): Y-coordinate of the location.

        Returns:
            list: List of zombies at the specified location.
        """
        return [zombie for zombie in self.list if zombie.x == x and zombie.y == y]

    def move_zombies(self):
        """
        Allow all zombies to take an action, such as moving or attacking.
        """
        for zombie in self.list:
            zombie.take_action()

    def status(self):
        """
        Return a summary of the zombies in the city.

        Returns:
            dict: A dictionary summarizing the number of zombies, dead zombies, and zombies near the player.
        """
        living_zombies = [zombie for zombie in self.list if not zombie.is_dead]
        dead_zombies = [zombie for zombie in self.list if zombie.is_dead]
        nearby_zombies = [
            zombie for zombie in self.list
            if abs(zombie.x - self.player.location[0]) <= 1 and abs(zombie.y - self.player.location[1]) <= 1
        ]

        return {
            "Total Zombies": len(self.list),
            "Living Zombies": len(living_zombies),
            "Dead Zombies": len(dead_zombies),
            "Nearby Zombies": len(nearby_zombies),
        }
