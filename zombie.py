# zombie.py
import random
import pygame
from settings import *

class CharacterSprite(pygame.sprite.Sprite):
    """A detailed zombie sprite for the description panel."""
    def __init__(self, zombie, image_path, panel_position):
        super().__init__()
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (100, 150))  # Example size
        self.rect = self.image.get_rect(center=panel_position)
        self.zombie = zombie  # Reference to the parent zombie


class Zombie(pygame.sprite.Sprite):
    """Represents a zombie in the city."""
    def __init__(self, x_groups, y_groups, zombie_group, x, y):
        super().__init__()
        self.x_groups, self.y_groups = x_groups, y_groups
        self.zombie_group = zombie_group
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
        self.image = pygame.Surface((10,10))
        self.image.fill((0, 255, 0))
        self.rect = self.image.get_rect()

        # Character image
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
        # self.rect.topleft = (new_x * BLOCK_SIZE, new_y * BLOCK_SIZE)  # Adjust offsets as needed

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
            total_row_width = total_zombie_width = zombie_width * total_zombies

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
    
    def gain_action_point(self):
        self.action_points += 1

    def take_action(self, player):
        if self.action_points >= 1 and not self.is_dead:
            target_building = self.find_lit_building()
            if target_building:  # Move towards lit building if adjacent
                if self.move_towards(target_building):
                    self.action_points -= 2
                else: # Attack barricades if in front of lit building
                    self.action_points -= 1
                    return self.attack_barricade(target_building)
                
            if (self.x, self.y) == player.location:  # Attack player if in same block
                self.action_points -= 1
                return self.attack(player)
            elif self.action_points >= 2:  # Move if no player or lit building to act upon
                self.action_points -= 2
                return self.move()
        elif self.is_dead and self.action_points >= 20:  # Stand up if dead
            self.stand_up()
        return "Zombie does nothing."

    def find_lit_building(self):
        """Finds adjacent lit buildings."""
        adjacent_positions = [
            (self.x + 1, self.y),
            (self.x - 1, self.y),
            (self.x, self.y + 1),
            (self.x, self.y - 1)
        ]
        lit_buildings = []

        for x, y in adjacent_positions:
            if 0 <= x < 100 and 0 <= y < 100:
                block = self.city[y][x]
                if hasattr(block, "lights_on") and block.lights_on:
                    lit_buildings.append(block)

        return random.choice(lit_buildings) if lit_buildings else None

    def move_towards(self, building):
        """Moves towards the given building if not already in front."""
        block = self.city[self.y][self.x]
        if block.lights_on:
            return False  # Already in front of a lit building.

        if building.x > self.x:
            self.x += 1
        elif building.x < self.x:
            self.x -= 1
        elif building.y > self.y:
            self.y += 1
        elif building.y < self.y:
            self.y -= 1
        return True

    def attack_barricade(self, building):
        """Attacks the barricades of the given building."""
        if hasattr(building, "barricade_level") and building.barricade.barricade_level > 0:
            if hasattr(building, "barricade_health") and building.barricade.barricade_health > 0:
                if random.random() < 0.3:  # 30% chance to successfully attack barricades
                    building.barricade.barricade_health -= 10
                    if building.barricade.barricade_health <= 0:  # Reduce barricade level if health reaches 0
                        building.barricade.barricade_health = 30  # Reset health for the next level
                        building.barricade.adjust_barricade_level(-1)
                        return "Zombie reduces barricade level!"
                    return "Zombie damages barricade."
            return "Zombie attack on barricade fails."
        return "No barricades to attack."

    def move(self):
        """Randomly moves the zombie to an adjacent block."""
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_x, new_y = self.x + dx, self.y + dy

        if 0 <= new_x < 100 and 0 <= new_y < 100:  # Ensure within city bounds
            self.x = new_x
            self.y = new_y
            return "Zombie moves."
        return "Zombie cannot move."

    def attack(self, player):
        """Attempts to attack a player if in the same block."""
        if (self.x, self.y) == player.location:
            player.take_damage(10)  # Zombies deal 10 damage
            return "Zombie attacks the player!"
        return "No target to attack."

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