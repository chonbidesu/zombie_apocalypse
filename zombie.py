# zombie.py
import random
import pygame
from settings import *

class Zombie:
    """Represents a zombie in the city."""
    def __init__(self, player, city, x, y):
        super().__init__()
        self.player = player
        self.location = (x, y)
        self.city = city
        self.hp = ZOMBIE_START_HP
        self.action_points = 0
        self.is_dead = False
        self.inside = False

        #  Sprites will be lazily loaded
        self.zombie_sprite = None
        self.viewport_zombie = None
          
    def take_action(self):
        if self.action_points >= 1 and not self.is_dead:
            current_block = self.city.block(self.x, self.y)
            target_dy, target_dy = (None, None)

            if (self.x, self.y) == self.player.location:  # Attack player if in same block
                self.action_points -= 1
                return self.attack(self.player)

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
            return self.stand_up()
        return False

    def find_target_dxy(self):
        """Finds a nearby lit building."""
        current_block = self.city.block(self.x, self.y)
        lit_buildings_dxy = []

        if self.player.location == (self.x, self.y) or current_block in self.player.lights_on:
            return (0, 0)
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue

                adjacent_x = self.x + dx
                adjacent_y = self.y + dy

                if self.player.location == (adjacent_x, adjacent_y):
                    return (dx, dy)

                adjacent_block = self.city.block(adjacent_x, adjacent_y)
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
        new_x, new_y = self.x + dx, self.y + dy

        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:  # Ensure within city bounds
            self.action_points -= 2
            self.x, self.y = new_x, new_y
            return True
        return False

    def attack(self, player):
        """Attempts to attack a player if in the same block."""
        self.action_points -= 1
        if random.random() < 0.3:
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

    def stand_up(self):
        """Zombie stands up at full health after collecting enough action points."""
        self.is_dead = False
        self.hp = 50
        self.action_points -= 20
        return "Zombie stands up and continues acting."

    def status(self):
        """Returns the current status of the zombie."""
        return {
            "Location": (self.x, self.y),
            "HP": self.hp,
            "Action Points": self.action_points,
            "Dead": self.is_dead,
        }    