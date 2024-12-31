# items.py
import pygame

class Item(pygame.sprite.Sprite):
    """Base class for all items."""
    def __init__(self, name, image_file=None):
        super().__init__()
        self.name = name

        # Load and scale the image if provided
        if image_file:
            self.image = pygame.image.load(image_file)
            self.image = pygame.transform.scale(self.image, (32, 32))  # Default size for item sprites
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((128, 128, 128))  # Default placeholder gray color

        # Create a rect for positioning
        self.rect = self.image.get_rect()

class Weapon(Item):
    """Base class for all weapons."""
    def __init__(self, name, damage, durability=None, loaded_ammo=None, max_ammo=None, image_file=None):
        super().__init__(name, image_file)
        self.damage = damage
        self.durability = durability
        self.loaded_ammo = loaded_ammo
        self.max_ammo = max_ammo
