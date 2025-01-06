# items.py
import pygame

class Item(pygame.sprite.Sprite):
    """Base class for all items."""
    def __init__(self, name, image_file=None):
        super().__init__()
        self.name = name
        self._image_file = image_file
        self._image = None

        self.rect = pygame.Rect(0, 0, 32, 32)

    @property
    def image(self):
        """Lazy-load the image when it is accessed."""
        if self._image is None:
            if self._image_file:
                self._image = pygame.image.load(self._image_file)
                self._image = pygame.transform.scale(self._image, (32, 32))
            else:
                self._image = pygame.Surface((32, 32))
                self._image.fill ((128, 128, 128))
        return self._image

class Weapon(Item):
    """Base class for all weapons."""
    def __init__(self, name, damage, durability=None, loaded_ammo=None, max_ammo=None, image_file=None):
        super().__init__(name, image_file)
        self.damage = damage
        self.durability = durability
        self.loaded_ammo = loaded_ammo
        self.max_ammo = max_ammo
