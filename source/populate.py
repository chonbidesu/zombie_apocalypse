# populate.py

import random
import csv

from characters import Character, CharacterName
from settings import *
from data import Occupation, OCCUPATIONS


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
        name = self._assign_name()

        # Determine NPC occupation
        if is_human:
            human_occupations = [occupation for occupation in OCCUPATIONS if occupation != Occupation.CORPSE]
            occupation = random.choice(human_occupations)
        else:
            occupation = Occupation.CORPSE

        if 0 <= x < CITY_SIZE and 0 <= y < CITY_SIZE:
            npc = Character(self.game, name, occupation, x, y, is_human)

            self.list.append(npc)

    def remove_npc(self, npc):
        """Remove an npc from the city."""
        if npc in self.list:
            self.list.remove(npc)

    def get_npcs_at(self, x, y):
        """Get all NPCs at a specific location."""
        return [npc for npc in self.list if npc.x == x and npc.y == y]

    def gain_ap(self):
        for npc in self.list:
            npc.ap += 1

    def take_action(self):
        """Allow all NPCs to take an action, such as moving or attacking."""
        for npc in self.list:
            npc.state.act()

    # Assign a random name to the character
    def _assign_name(self):
        file_path = DataPath('tables/character_names.csv').path
        name_generator = NameGenerator(file_path)
        return name_generator.generate_name()            

class NameGenerator:
    def __init__(self, csv_file):
        self.first_names = {}
        self.last_names = []
        self.zombie_adjectives = {}
        self.load_names(csv_file)

    def load_names(self, csv_file):
        with open(csv_file, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                first_name_letter = row['first_name'][0].upper()
                zombie_adjective_letter = row['zombie_adjective'][0].upper()
                if first_name_letter not in self.first_names:
                    self.first_names[first_name_letter] = []
                if zombie_adjective_letter not in self.zombie_adjectives:
                    self.zombie_adjectives[zombie_adjective_letter] = []
                self.first_names[first_name_letter].append(row['first_name'])
                self.last_names.append(row['last_name'])
                self.zombie_adjectives[zombie_adjective_letter].append(row['zombie_adjective'])
    
    def generate_name(self):
        first_letter = random.choice(list(self.first_names.keys()))
        first_name = random.choice(self.first_names[first_letter])
        last_name = random.choice(self.last_names)
        zombie_adjective = random.choice(self.zombie_adjectives[first_letter])
        return CharacterName(first_name, last_name, zombie_adjective)            