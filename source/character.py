# character.py

from settings import *

class Character:
    """Base class for Player and NPC Characters."""
    def __init__(self, game, name, occupation, x, y, is_human, inside=False):
        self.game = game
        self.name = name
        self.occupation = occupation
        self.location = (x, y)
        self.hp = MAX_HP
        self.action_points = 0
        self.is_dead = False
        self.is_human = is_human
        self.inside = inside
        self.inventory = []
        self.skills = set()
