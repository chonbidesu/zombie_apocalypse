# zombie.py
import random
from enum import Enum, auto

from settings import *

class ZombieAction(Enum):
    FIND_TARGET = auto()            # Find a nearby player or lit building
    MOVE_TOWARDS = auto()           # Move toward the target
    ATTACK_PLAYER = auto()          # Attack the player
    HANDLE_BARRICADE = auto()       # Attack barricades if target is a lit building
    WANDER = auto()                 # Move randomly
    ENTER_BUILDING = auto()         # Enter unbarricaded buildings occasionally
    RANSACK = auto()                # Ransack a building
    RELOCATE = auto()               # Move to an adjacent block due to overcrowding
    STAND_UP = auto()               # Stand up after death

class Zombie:
    """Represents a zombie in the city."""
    def __init__(self, player, city, chat_history, x, y):
        super().__init__()
        self.player = player
        self.location = (x, y)
        self.city = city
        self.chat_history = chat_history
        self.hp = ZOMBIE_MAX_HP
        self.action_points = 0
        self.is_dead = False
        self.inside = False

        #  Sprites will be lazily loaded
        self.zombie_sprite = None
        self.viewport_zombie = None
          
    def take_action(self):
        """Determine and execute zombie behavior."""
        current_block = self.city.block(self.location[0], self.location[1])

        # Determine behavior
        action = self.determine_behaviour(current_block)

        if action == ZombieAction.RELOCATE:
            self.relocate_zombie(current_block)
            return  # Skip action after relocation

        if action == ZombieAction.ATTACK_PLAYER:
            self.chat_history.append(self.attack(self.player))
            return

        if action == ZombieAction.HANDLE_BARRICADE:
            self.handle_barricades(current_block)
            return

        if action == ZombieAction.MOVE_TOWARDS:
            target_dx, target_dy = self.find_target_dxy()
            if target_dx is not None and self.action_points >= 2:
                self.move_towards(target_dx, target_dy)
                return

        if action == ZombieAction.ENTER_BUILDING:
            self.enter()
            return
        
        if action == ZombieAction.RANSACK:
            self.ransack(current_block)
            return

        if action == ZombieAction.WANDER:
            self.move()
            return

        if action == ZombieAction.STAND_UP:
            self.stand_up()
            return

        return False  # No action taken

    def determine_behaviour(self, current_block):
        """Determine the priority for the zombie."""
        properties = BLOCKS[current_block.type]
        # Stand up if dead and have enough action points
        if self.is_dead:
            if self.action_points >= STAND_UP_AP:
                return ZombieAction.STAND_UP
            else:
                return False

        # Relocate if the block is overcrowded
        if current_block.current_zombies > ZOMBIE_CAPACITY:
            return ZombieAction.RELOCATE

        # Attack player if in the same block
        if self.location == self.player.location and self.inside == self.player.inside and self.action_points >= 1:
            return ZombieAction.ATTACK_PLAYER

        # Handle barricades or building entry if at target location
        if self.find_target_dxy() and self.action_points >= 1:
            target_dx, target_dy = self.find_target_dxy()
            if (target_dx, target_dy) == (0, 0):
                return ZombieAction.HANDLE_BARRICADE
            else:
                return ZombieAction.MOVE_TOWARDS

        # Chance to investigate nearby building
        if properties.is_building and current_block.barricade.level == 0 and not self.inside and self.action_points >= 1:
            roll = random.randint(1, 20)
            if roll < 5:
                return ZombieAction.ENTER_BUILDING
            
        if self.inside:
            if not current_block.is_ransacked and self.action_points >= 1:
                roll = random.randint(1, 20)
                if roll < 5:
                    return ZombieAction.RANSACK

        # Random movement if no targets or barricades present
        if self.action_points >= 2:
            return ZombieAction.WANDER

        return None  # No behaviour determined

    def relocate_zombie(self, current_block):
        """Move the zombie to an adjacent block due to overcrowding."""
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adjacent_x, adjacent_y = self.location[0] + dx, self.location[1] + dy
            adjacent_block = self.city.block(adjacent_x, adjacent_y)

            if adjacent_block.current_zombies < ZOMBIE_CAPACITY:
                print(f"Zombie at {self.location} relocating to ({adjacent_x}, {adjacent_y}) due to overcrowding.")
                current_block.current_zombies -= 1
                adjacent_block.current_zombies += 1
                self.location = (adjacent_x, adjacent_y)
                self.inside = False
                return


    def find_target_dxy(self):
        """Finds a nearby player or lit building."""
        current_block = self.city.block(self.location[0], self.location[1])
        current_block_properties = BLOCKS[current_block.type]
        lit_buildings_dxy = []

        # Check if the player or a lit building is nearby
        if self.player.location == self.location and self.inside == self.player.inside:
            return (0, 0) # Stay put
        elif current_block_properties.is_building:
            if current_block.lights_on:
                return (0, 0) # Stay put

        # Otherwise, move    
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx == 0 and dy == 0:
                    continue # Don't stay put

                adjacent_x = self.location[0] + dx
                adjacent_y = self.location[1] + dy

                if self.player.location == (adjacent_x, adjacent_y) and not self.player.inside: # Check if the player is next door
                    return (dx, dy) # Shamble towards player

                if 0 < adjacent_x < CITY_SIZE and 0 < adjacent_y < CITY_SIZE:
                    adjacent_block = self.city.block(adjacent_x, adjacent_y)
                    adjacent_block_properties = BLOCKS[adjacent_block.type]
                    if adjacent_block_properties.is_building:
                        if adjacent_block.lights_on:
                            lit_buildings_dxy.append((dx, dy)) 

        return random.choice(lit_buildings_dxy) if lit_buildings_dxy else None  # Shamble towards lit building

    def move_towards(self, dx, dy):
        """Moves the zombie towards the target if space is available."""
        new_x = self.location[0] + dx
        new_y = self.location[1] + dy

        current_block = self.city.block(self.location[0], self.location[1])
        target_block = self.city.block(new_x, new_y)

        # Check if the target block has capacity
        if target_block.current_zombies < ZOMBIE_CAPACITY:
            # Leave the current block
            current_block.current_zombies -= 1

            # Enter the new block
            target_block.current_zombies += 1
            self.location = (new_x, new_y)
            self.action_points -= 2
            self.inside = False
            return True

        # If target block is full, attempt to move to another adjacent block
        for dx_alt, dy_alt in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            alt_x, alt_y = self.location[0] + dx_alt, self.location[1] + dy_alt
            alt_block = self.city.block(alt_x, alt_y)
            if alt_block.current_zombies < ZOMBIE_CAPACITY:
                current_block.current_zombies -= 1
                alt_block.current_zombies += 1
                self.location = (alt_x, alt_y)
                self.inside = False
                self.action_points -= 2
                return True

        # No movement if no adjacent block has capacity
        return False

    def handle_barricades(self, current_block):
        """Attack barricades or attempt entry."""
        if current_block.barricade.level > 0 and not self.inside:
            return self.attack_barricade(current_block)

        if current_block.barricade.level == 0 and not self.inside:
            return self.enter()

        #if self.inside and not self.player.inside:
        #    return self.leave()        

    def attack_barricade(self, building):
        """Attacks the barricades of the given building."""
        if hasattr(building.barricade, "level") and building.barricade.level > 0:
            if random.random() < 0.3:  # 30% chance to successfully attack barricades
                building.barricade.health -= 5
                if building.barricade.health <= 0:  # Reduce barricade level if health reaches 0
                    building.barricade.health = 30  # Reset health for the next level
                    building.barricade.adjust_barricade_level(-1)
                self.action_points -= 1
                if self.location == self.player.location:
                    if building.barricade.level == 0:
                        return "You hear the last of the barricades fall away."
                    return "You hear something attack the barricades."

    def move(self):
        """Randomly moves the zombie to an adjacent block."""
        x, y = self.location[0], self.location[1]
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        new_x, new_y = x + dx, y + dy
        current_block = self.city.block(x, y)

        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:  # Ensure within city bounds
            new_block = self.city.block(new_x, new_y)
            self.action_points -= 2
            current_block.current_zombies -= 1
            new_block.current_zombies += 1
            self.location = (new_x, new_y)
            self.inside = False
            return True
        return False

    def attack(self, player):
        """Attempts to attack a player if in the same block."""
        self.action_points -= 1
        if random.random() < 0.3:
            player.take_damage(ZOMBIE_DAMAGE)  # Zombies deal 10 damage
            return "A zombie slams into you!"
        else:
            return "A zombie swipes at you, but misses."

    def enter(self):
        """Enter a building."""
        self.action_points -= 1
        self.inside = True
    
    def leave(self):
        """Leave a building."""
        self.action_points -= 1
        self.inside = False
        return "Zombie leaves the building."    
    
    def ransack(self, current_block):
        """Ransack a building."""
        self.action_points -= 1
        current_block.is_ransacked = True
        return "Zombie ransacks the building."

    def take_damage(self, amount):
        """Reduces the zombie's health."""
        self.hp -= amount
        if self.hp <= 0:
            self.die()
        return f"Zombie takes {amount} damage."

    def die(self):
        """Handles the zombie's death."""
        self.chat_history.append("A zombie slumps to the floor, apparently dead.")
        self.is_dead = True
        self.hp = 0

    def stand_up(self):
        """Zombie stands up at full health after collecting enough action points."""
        if self.location == self.player.location and self.inside == self.player.inside:
            self.chat_history.append("A zombie stirs, and gets to its feet, swaying.")
        self.is_dead = False
        self.hp = 50
        self.action_points -= 50

    def status(self):
        """Returns the current status of the zombie."""
        return {
            "Location": self.location,
            "HP": self.hp,
            "Action Points": self.action_points,
            "Dead": self.is_dead,
        }    