# items.py
import pygame

from settings import *
from data import ITEMS

class Item(pygame.sprite.Sprite):
    """Base class for all items."""
    def __init__(self, type):
        super().__init__()
        self.type = type
        self.properties = ITEMS[self.type]
        self.image_file = self.properties.image_file
        self._original_image = self.load_image(self.image_file)  # Preload image during initialization
        self.image = self._original_image.copy()
        self.rect = self.image.get_rect()  # Use the image's rect for positioning
        self._cached_size = self.image.get_size()

    def load_image(self, image_file):
        """Load and scale the image to fit the inventory panel size."""
        if image_file:
            image = pygame.image.load(image_file).convert_alpha()
        else:
            image = pygame.Surface((32, 32))
            image.fill((128, 128, 128))
        return image

    def scale_image(self, width, height):
        if (width, height) != self._cached_size:
            self.image = pygame.transform.scale(self._original_image, (width, height))
            self.rect = self.image.get_rect(topleft=self.rect.topleft)
            self._cached_size = (width, height)

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