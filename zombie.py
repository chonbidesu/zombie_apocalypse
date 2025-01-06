# zombie.py
import random
import pygame
from settings import *

class CharacterSprite(pygame.sprite.Sprite):
    """A detailed zombie sprite for the description panel."""
    def __init__(self, zombie, image_path, panel_position):
        super().__init__()
        self.zombie = zombie  # Reference to the parent zombie
        self._image = None  # Private attribute for image
        self.image_path = image_path  # Store the path for lazy loading
        self.rect = pygame.Rect(panel_position, (100, 150))  # Example size for sprite rect

    @property
    def image(self):
        """Lazy load the image when accessed."""
        if self._image is None:
            # Load and transform the image when it's first needed
            self._image = pygame.image.load(self.image_path).convert_alpha()
            self._image = pygame.transform.scale(self._image, (100, 150))  # Scale to desired size
        return self._image

    @image.setter
    def image(self, value):
        """Setter for image, useful if you need to manually set the image."""
        self._image = value


class Zombie(pygame.sprite.Sprite):
    """Represents a zombie in the city."""
    def __init__(self, player, get_block_at_xy, x, y):
        super().__init__()
        self.player = player
        self.x_groups, self.y_groups = player.x_groups, player.y_groups
        self.zombie_group = player.zombie_group
        self.get_block_at_xy = get_block_at_xy
        self.hp = ZOMBIE_START_HP
        self.action_points = 0
        self.is_dead = False
        self.inside = False
        self.start_location = x, y

        # Add zombie to sprite groups
        self.x_groups[x].add(self)
        self.y_groups[y].add(self)
        self.zombie_group.add(self)

        # Set up viewport sprite
        self.image = pygame.Surface((10, 10))  # Placeholder surface
        self.image.fill((0, 255, 0))  # Example fill color (green)
        self.rect = self.image.get_rect()

        # Character sprite will be lazily loaded
        self.character_sprite = None

    def get_coordinates(self):
        """Get the zombie's (x, y) position in the city."""
        for x, group in enumerate(self.x_groups):
            if self in group:
                x_coordinate = x
                break

        for y, group in enumerate(self.y_groups):
            if self in group:
                y_coordinate = y
                break

        return x_coordinate, y_coordinate

    def update_position(self, new_x, new_y):
        """Updates the position of the zombie's sprite rect based on city coordinates."""
        current_x, current_y = self.get_coordinates()

        self.x_groups[current_x].remove(self)
        self.y_groups[current_y].remove(self)
        self.x_groups[new_x].add(self)
        self.y_groups[new_y].add(self)

    def update_character_sprite(self, player, index, total_zombies):
        """
        Update the character sprite for the description panel.

        Args:
            player (Player): The player object.
            index (int): The index of the zombie among zombies at the same location.
            total_zombies (int): The total number of zombies at the location.
        """
        current_x, current_y = self.get_coordinates()
        if (current_x, current_y) == player.location and player.inside == self.inside:
            # Calculate the setting_image dimensions and position
            description_start_x = SCREEN_WIDTH // 3 + 10
            description_width = SCREEN_WIDTH * 2 // 3 - 10
            setting_image_width = description_width * 5 // 6
            setting_image_height = (setting_image_width * 4) // 9
            setting_image_x = description_start_x + (description_width - setting_image_width) // 2
            setting_image_y = 10

            # Calculate zombie sprite row alignment
            zombie_width = setting_image_width // max(total_zombies, 1)  # Space for each zombie
            zombie_width = min(zombie_width, 50)  # Limit zombie width
            total_row_width = zombie_width * total_zombies

            # Center the row horizontally within the setting_image
            row_start_x = setting_image_x + (setting_image_width - total_row_width) // 2
            row_y = setting_image_y + setting_image_height - 10  # Align to bottom edge with padding

            # Calculate the position for this zombie
            zombie_x = row_start_x + index * zombie_width

            # Update or create the character sprite
            if not self.character_sprite:
                image_path = "assets/zombie_character.png"
                self.character_sprite = CharacterSprite(self, image_path, (zombie_x, row_y))
            else:
                self.character_sprite.rect.midbottom = (zombie_x + zombie_width // 2, row_y)

            return self.character_sprite  # Return the sprite to be added to the group
        else:
            self.character_sprite = None  # Remove the sprite if conditions aren't met
            return None
            
    def take_action(self, player):
        if self.action_points >= 1 and not self.is_dead:
            current_x, current_y = self.get_coordinates()
            current_block = self.get_block_at_xy(player, current_x, current_y)
            target_dy, target_dy = (None, None)

            if (current_x, current_y) == player.location:  # Attack player if in same block
                self.action_points -= 1
                return self.attack(player)

            if self.find_target_dxy():
                target_dx, target_dy = self.find_target_dxy()            
                if (target_dx, target_dy) == (0, 0):
                    if current_block.barricade.level < 0 and not self.inside:
                        return self.attack_barricade(current_block)
                    elif current_block.barricade.level == 0 and not self.inside:
                        return self.enter()
                elif self.action_points >= 2:
                    return self.move_towards(target_dx, target_dy)

            elif self.action_points >= 2:  # Move if no player or lit building to act upon
                return self.move()
             

        elif self.is_dead and self.action_points >= 20:  # Stand up if dead
            self.stand_up()
        return "Zombie does nothing."

    def find_target_dxy(self):
        """Finds a nearby lit building."""
        current_x, current_y = self.get_coordinates()
        current_block = self.get_block_at_xy(self.player, current_x, current_y)
        lit_buildings_dxy = []

        if self.player.location == (current_x, current_y) or current_block in self.player.lights_on:
            return (0, 0)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue

                adjacent_x = current_x + dx
                adjacent_y = current_y + dy

                if self.player.location == (adjacent_x, adjacent_y):
                    return (dx, dy)

                adjacent_block = self.get_block_at_xy(self.player, adjacent_x, adjacent_y)
                if adjacent_block in self.player.lights_on:
                    lit_buildings_dxy.append((dx, dy))

        return random.choice(lit_buildings_dxy) if lit_buildings_dxy else None

    def move_towards(self, dx, dy):
        """Moves towards the given building if not already in front."""
        current_x, current_y = self.get_coordinates()
        new_x = current_x + dx
        new_y = current_y + dy
        
        if dx == 0 and dy == 0:
            return False
        self.action_points -= 2
        return self.update_position(new_x, new_y)
        

    def attack_barricade(self, building):
        """Attacks the barricades of the given building."""
        if hasattr(building.barricade, "level") and building.barricade.level > 0:
            if hasattr(building.barricade, "health") and building.barricade.health > 0:
                if random.random() < 0.3:  # 30% chance to successfully attack barricades
                    building.barricade.health -= 10
                    if building.barricade.health <= 0:  # Reduce barricade level if health reaches 0
                        building.barricade.health = 30  # Reset health for the next level
                        building.barricade.adjust_barricade_level(-1)
                        self.action_points -= 1
                        return "Zombie reduces barricade level!"
                    return "Zombie damages barricade."
            return "Zombie attack on barricade fails."
        return "No barricades to attack."

    def move(self):
        """Randomly moves the zombie to an adjacent block."""
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        current_x, current_y = self.get_coordinates()
        new_x, new_y = current_x + dx, current_y + dy

        if 0 <= new_x < 100 and 0 <= new_y < 100:  # Ensure within city bounds
            self.action_points -= 2
            return self.update_position(new_x, new_y)
        return False

    def attack(self, player):
        """Attempts to attack a player if in the same block."""
        if random.random() < 0.3:
            self.action_points -= 1
            return player.take_damage(10)  # Zombies deal 10 damage
        else:
            return False

    def enter(self):
        """Enter a building."""
        self.action_points -= 1
        self.inside = True
        return "Zombie enters the building."

    def take_damage(self, amount):
        """Reduces the zombie's health."""
        self.hp -= amount
        if self.hp <= 0:
            self.die()
            return "Zombie is dead."
        return "Zombie takes damage."

    def die(self):
        """Handles the zombie's death."""
        self.is_dead = True
        self.hp = 0
        self.dead_body_visible = True

    def stand_up(self):
        """Zombie stands up at full health after collecting enough action points."""
        self.is_dead = False
        self.hp = 50
        self.dead_body_visible = False
        self.action_points = 0
        return "Zombie stands up and continues acting."

    def status(self):
        """Returns the current status of the zombie."""
        return {
            "Location": (self.x, self.y),
            "HP": self.hp,
            "Action Points": self.action_points,
            "Dead": self.is_dead,
            "Dead Body Visible": self.dead_body_visible
        }    