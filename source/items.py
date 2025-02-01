# items.py
import pygame

from settings import *
from data import ITEMS

class Item:
    """Base class for all items."""
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.properties = ITEMS[self.type]
        self.image_file = self.properties.image_file

    def get_attributes(self):
        return {}

class Weapon(Item):
    """Base class for all weapons."""
    def __init__(self, type):
        super().__init__(type)
        self.damage = self.properties.damage
        self.durability = self.properties.durability
        self.loaded_ammo = self.properties.max_ammo
        self.max_ammo = self.properties.max_ammo

    def get_attributes(self):
        attributes = {}
        if self.durability is not None:
            attributes['durability'] = self.durability
        if self.loaded_ammo is not None:
            attributes['loaded_ammo'] = self.loaded_ammo
        return attributes