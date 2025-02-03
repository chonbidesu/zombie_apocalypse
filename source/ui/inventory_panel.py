# inventory_panel.py

import pygame

from settings import *
from data import ITEMS, ItemFunction


class InventoryPanel:
    """Draw the inventory panel, items and weapon."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.width, self.height = (SCREEN_WIDTH * 7 // 16) + (SCREEN_HEIGHT * -7 // 32) - 20, SCREEN_HEIGHT * 31 // 160
        self.weapon_size = self.height
        self.original_image = pygame.image.load(ResourcePath("assets/inventory_panel.png").path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
        self.original_weapon_image = pygame.image.load(ResourcePath("assets/equipped_panel.png").path).convert_alpha()
        self.weapon_image = pygame.transform.scale(self.original_weapon_image, (self.weapon_size, self.weapon_size))
        self.inventory_group = pygame.sprite.Group()

    def draw(self):
        """Draw the inventory panel."""
        x, y = SCREEN_WIDTH - self.width - 10, SCREEN_HEIGHT * 25 // 32 + 10
        weapon_x, weapon_y = x - self.weapon_size, y

        # Blit the panel backgrounds
        self.screen.blit(self.image, (x, y))
        self.screen.blit(self.weapon_image, (weapon_x, weapon_y))

        # Draw inventory items and weapon
        self._draw_items(x, y)

    def _draw_items(self, x, y):
        """Inventory item scaling, positioning and drawing."""
        item_width = int(self.width * 0.14)
        item_height = int(self.height * 0.32)
        highlight = pygame.Surface((item_width, item_height), pygame.SRCALPHA)

        # Position offsets for rows
        start_x = x + int(self.width * 0.06)
        first_row_y = y + int(self.height * 0.13)
        second_row_y = first_row_y + item_height + int(self.height * 0.11)

        # Keep track of items to update
        updated_sprites = []

        # Scale each inventory item image before drawing
        for index, item in enumerate(list(self.game.player.inventory)[:MAX_ITEMS]):
            row = index // MAX_ITEMS_PER_ROW
            col = index % MAX_ITEMS_PER_ROW

            item_x = start_x + col * (item_width + int(self.width * 0.05))
            item_y = first_row_y if row == 0 else second_row_y

            # Check if an InventorySprite for this item already exists
            existing_sprite = next((sprite for sprite in self.inventory_group if sprite.item == item), None)

            if existing_sprite:
                existing_sprite.update_position(item_x, item_y)
                updated_sprites.append(existing_sprite)
                sprite = existing_sprite
            else:
                new_sprite = InventorySprite(item, item_x, item_y, item_width, item_height)
                self.inventory_group.add(new_sprite)
                updated_sprites.append(new_sprite)
                sprite = new_sprite

            # Highlight the item's slot if the item is equipped
            if item == self.game.player.weapon:
                highlight.fill((TRANS_YELLOW))
                self.screen.blit(highlight, sprite.rect.topleft)

                # Draw enlarged equipped item
                weapon_properties = ITEMS[item.type]
                weapon_item_size = self.weapon_size * 3 // 5
                enlarged_weapon_image = pygame.transform.scale(sprite.image, (weapon_item_size, weapon_item_size))
                weapon_item_x = x - (self.weapon_size // 2) - (weapon_item_size // 2)
                weapon_item_y = y + (self.weapon_size // 2) - (weapon_item_size // 2)
                self.screen.blit(enlarged_weapon_image, (weapon_item_x, weapon_item_y))

                # Draw equipped item label
                weapon_text = font_large.render(weapon_properties.item_type, True, ORANGE)
                weapon_text_shadow = font_large.render(weapon_properties.item_type, True, BLACK)                
                text_width = weapon_text.get_width()
                self.screen.blit(weapon_text_shadow, (weapon_item_x + (weapon_item_size // 2) - (text_width // 2) + 1, weapon_item_y + weapon_item_size + 8))                
                self.screen.blit(weapon_text, (weapon_item_x + (weapon_item_size // 2) - (text_width // 2), weapon_item_y + weapon_item_size + 7))

                # Draw currently loaded ammo
                if weapon_properties.item_function == ItemFunction.FIREARM:
                    label_x = weapon_item_x + weapon_item_size - 20
                    label_y = weapon_item_y + weapon_item_size - 20
                    pygame.draw.rect(self.screen, WHITE, (label_x, label_y, 20, 20))
                    loaded_ammo = font_large.render(str(item.loaded_ammo), True, BLACK)
                    self.screen.blit(loaded_ammo, (label_x + 5, label_y + 2))

            else:
                highlight.fill((0, 0, 0, 0))

        # Remove any sprites that are no longer in the inventory
        for sprite in list(self.inventory_group):
            if sprite not in updated_sprites:
                sprite.kill()

        # Draw the inventory group to screen
        self.inventory_group.draw(self.screen)


class InventorySprite(pygame.sprite.Sprite):
    """An item sprite for the inventory panel."""
    def __init__(self, item, x, y, width, height):
        super().__init__()
        self.item = item  # Reference to the actual item object
        self.image = pygame.image.load(item.image_file).convert_alpha()  # Load item image
        self.image = pygame.transform.scale(self.image, (width, height))  # Scale to fit inventory
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_position(self, x, y):
        """Update sprite position when inventory layout changes."""
        self.rect.topleft = (x, y)  