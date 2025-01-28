# npc.py
import random
from enum import Enum, auto

from settings import *

class NPCAction(Enum):
    GIVE_QUEST = auto()             # Provide a quest to the player
    FIND_TARGET = auto()            # Find a nearby player or lit building
    MOVE_TOWARDS = auto()           # Move toward the target
    FOLLOW_PLAYER = auto()          # After encountering player, follow them
    ATTACK_PLAYER = auto()          # Attack the player
    ATTACK_NPC = auto()             # Attack another NPC
    EXTRACT_DNA = auto()            # Extract DNA from a zombie
    REVIVE_NPC = auto()             # Revive a zombie to human form
    HANDLE_BARRICADE = auto()       # Deal with barricades (reinforce or attack)
    REPAIR_BUILDING = auto()        # Repair damaged buildings
    WANDER = auto()                 # Move randomly
    ENTER_BUILDING = auto()         # Enter buildings
    RANSACK = auto()                # Ransack a building
    RELOCATE = auto()               # Move to an adjacent block due to overcrowding
    STAND_UP = auto()               # Stand up after death

class NPC:
    """Represents an NPC in the city."""
    def __init__(self, game, x, y, type=None, is_human=False, inside=False):
        super().__init__()
        self.type = type
        self.game = game
        self.location = (x, y)
        self.hp = NPC_MAX_HP
        self.action_points = 0
        self.is_dead = False
        self.is_human = is_human
        self.hostile = self.is_hostile()
        self.inside = inside
        self.action_points_lost = 0

        self.pursuing_player = False
        self.last_known_player_location = None

    def is_hostile(self):
        if self.type == NPCType.PKER:
            return True
        else:
            return False

    def take_action(self):
        """Determine and execute NPC behavior."""
        self.action_points_gained = 0
        self.action_points_lost = 0
        if self.action_points < 1:
            return False
        
        current_block = self.game.city.block(self.location[0], self.location[1])

        # Determine behavior
        if self.is_human:
            action = self.determine_human_behaviour(current_block)
        else:
            action = self.determine_zombie_behaviour(current_block)

        # Start NPC actions
        if action == NPCAction.RELOCATE:
            self.relocate_npc(current_block)
            return  # Skip action after relocation

        elif action == NPCAction.ATTACK_PLAYER:
            self.game.chat_history.append(self.attack())
            return
        
        elif action == NPCAction.FOLLOW_PLAYER:
            self.follow(current_block)

        elif action == NPCAction.HANDLE_BARRICADE:
            self.handle_barricades(current_block)
            return

        elif action == NPCAction.MOVE_TOWARDS:
            target_dx, target_dy = self.find_target_dxy()
            if target_dx is not None and self.action_points >= 2:
                self.move_towards(target_dx, target_dy)
                return

        elif action == NPCAction.ENTER_BUILDING:
            self.enter()
            return
        
        elif action == NPCAction.RANSACK:
            self.ransack(current_block)
            return

        elif action == NPCAction.WANDER:
            self.move()
            return

        elif action == NPCAction.STAND_UP:
            self.stand_up()
            return

        return False  # No action taken

    def determine_human_behaviour(self, current_block):
        """Determine the priority for the NPC."""
        properties = BLOCKS[current_block.type]
        # Stand up if dead and have enough action points
        if self.is_dead:
            return NPCAction.STAND_UP if self.action_points >= STAND_UP_AP else False

        # Relocate if the block is overcrowded
        if current_block.current_humans > HUMAN_CAPACITY:
            return NPCAction.RELOCATE
        
        elif self.type == NPCType.SURVIVOR:
            if current_block.current_zombies > 0:
                return NPCAction.FIND_TARGET # Flee to another building
            elif self.location == self.game.player.location and self.inside == self.game.player.inside:
                return NPCAction.GIVE_QUEST
            elif not self.inside and properties.is_building:
                    return NPCAction.ENTER_BUILDING
            
        elif self.type == NPCType.PREPPER:
            if properties.is_building and not self.inside:
                return NPCAction.ENTER_BUILDING
            elif self.inside:
                for zombie in self.game.zombies.list:
                    if self.location == zombie.location and zombie.inside:
                        return NPCAction.ATTACK_NPC
                if current_block.is_ransacked:
                    return NPCAction.REPAIR_BUILDING
                elif current_block.barricade.level <= 4:
                    return NPCAction.HANDLE_BARRICADE
                else:
                    return NPCAction.FIND_TARGET
        
        elif self.type == NPCType.SCIENTIST:
            if current_block.current_zombies > 0:
                return NPCAction.ATTACK_NPC
            else:
                return NPCAction.FIND_TARGET
            
        elif self.type == NPCType.PKER:
            if self.location == self.game.player.location and self.inside == self.game.player.inside:
                self.pursuing_player = True
                self.last_known_player_location = self.game.player.location
                return NPCAction.ATTACK_PLAYER

        return None  # No behaviour determined

    def determine_zombie_behaviour(self, current_block):
        """Determine the priority for the NPC."""
        properties = BLOCKS[current_block.type]
        # Stand up if dead and have enough action points
        if self.is_dead:
            return NPCAction.STAND_UP if self.action_points >= STAND_UP_AP else False

        # Relocate if the block is overcrowded
        if current_block.current_zombies > ZOMBIE_CAPACITY:
            return NPCAction.RELOCATE
        
        elif self.location == self.game.player.location and self.inside == self.game.player.inside:
            self.pursuing_player = True
            self.last_known_player_location = self.game.player.location
            return NPCAction.ATTACK_PLAYER            
            
        elif current_block.current_humans > 0:
            return NPCAction.ATTACK_NPC

        elif self.pursuing_player:
            return NPCAction.FOLLOW_PLAYER

        elif self.is_player_adjacent():
            self.pursuing_player = True
            self.last_known_player_location = self.game.player.location
            return NPCAction.FOLLOW_PLAYER

        elif self.type == NPCType.SURVIVOR:
            return NPCAction.WANDER
        
        elif self.type == NPCType.SCIENTIST:
            return NPCAction.WANDER
        
        elif self.type == NPCType.PKER:
            return NPCAction.WANDER

        elif self.type == NPCType.PREPPER:
            if properties.is_building and current_block.barricade.level == 0 and not self.inside and self.action_points >= 1:
                roll = random.randint(1, 20)
                if roll < 5:
                    return NPCAction.ENTER_BUILDING
                        
            if self.inside:
                if not current_block.is_ransacked and self.action_points >= 1:
                    roll = random.randint(1, 20)
                    if roll < 5:
                        return NPCAction.RANSACK
                    
            if self.find_target_dxy() and self.action_points >= 1:
                target_dx, target_dy = self.find_target_dxy()
                if (target_dx, target_dy) == (0, 0):
                    return NPCAction.HANDLE_BARRICADE
                else:
                    return NPCAction.MOVE_TOWARDS

            # Random movement if no targets or barricades present
            if self.action_points >= 2:
                return NPCAction.WANDER

        return None  # No behaviour determined

    def is_player_adjacent(self):
        """Check if the player is in an adjacent square."""
        npc_x, npc_y = self.location
        player_x, player_y = self.game.player.location

        # Check if the player is within a 1-tile radius in any direction
        return abs(npc_x - player_x) <= 1 and abs(npc_y - player_y) <= 1 and self.inside == self.game.player.inside

    def relocate_npc(self, current_block):
        """Move the zombie to an adjacent block due to overcrowding."""
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            adjacent_x, adjacent_y = self.location[0] + dx, self.location[1] + dy
            adjacent_block = self.game.city.block(adjacent_x, adjacent_y)

            if adjacent_block.current_zombies < ZOMBIE_CAPACITY:
                print(f"NPC at {self.location} relocating to ({adjacent_x}, {adjacent_y}) due to overcrowding.")
                current_block.current_zombies -= 1
                adjacent_block.current_zombies += 1
                self.location = (adjacent_x, adjacent_y)
                self.inside = False
                return

    def follow(self, current_block):
        properties = BLOCKS[current_block.type]
        if not self.last_known_player_location:
            self.pursuing_player = False
            return False
        
        px, py = self.last_known_player_location
        dx, dy = self.get_direction_toward(px, py)

        if (dx, dy) == (0, 0) and self.inside != self.game.player.inside and properties.is_building:
            if self.inside and current_block.barricade.level == 0:
                self.leave()
            elif not self.inside and current_block.barricade.level == 0:
                self.enter()
            elif current_block.barricade.level > 0:
                self.attack_barricade(current_block)
            return True

        if dx is not None and dy is not None:
            self.move_towards(dx, dy)

        if self.distance_to(self.game.player) <= 1 and self.inside == self.game.player.inside:
            self.last_known_player_location = self.game.player.location
        else:
            self.pursuing_player = False
            self.last_known_player_location = None

    def get_direction_toward(self, target_x, target_y):
        """Calculate the best direction to move towards the target."""
        dx = target_x - self.location[0]
        dy = target_y - self.location[1]

        if dx != 0:
            dx = 1 if dx > 0 else -1
        if dy != 0:
            dy = 1 if dy > 0 else -1

        return dx, dy
    
    def distance_to(self, target):
        """Calculate Manhattan distance to the target."""
        return abs(self.location[0] - target.location[0]) + abs(self.location[1] - target.location[1])

    def find_target_dxy(self):
        """Finds a nearby player or lit building."""
        current_block = self.game.city.block(self.location[0], self.location[1])
        current_block_properties = BLOCKS[current_block.type]
        lit_buildings_dxy = []

        # Check if the player or a lit building is nearby
        if self.game.player.location == self.location and self.inside == self.game.player.inside:
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

                if self.game.player.location == (adjacent_x, adjacent_y) and not self.game.player.inside: # Check if the player is next door
                    return (dx, dy) # Shamble towards player

                if 0 < adjacent_x < CITY_SIZE and 0 < adjacent_y < CITY_SIZE:
                    adjacent_block = self.game.city.block(adjacent_x, adjacent_y)
                    adjacent_block_properties = BLOCKS[adjacent_block.type]
                    if adjacent_block_properties.is_building:
                        if adjacent_block.lights_on:
                            lit_buildings_dxy.append((dx, dy)) 

        return random.choice(lit_buildings_dxy) if lit_buildings_dxy else None  # Shamble towards lit building

    def move_towards(self, dx, dy):
        """Moves the NPC towards the target if space is available."""


        new_x = self.location[0] + dx
        new_y = self.location[1] + dy

        current_block = self.game.city.block(self.location[0], self.location[1])
        target_block = self.game.city.block(new_x, new_y)

        # Check if the target block has capacity
        if target_block.current_zombies < ZOMBIE_CAPACITY:
            # Leave the current block
            current_block.current_zombies -= 1

            # Enter the new block
            target_block.current_zombies += 1
            self.location = (new_x, new_y)
            self.action_points -= 2
            self.action_points_lost += 2
            self.inside = False
            return True
        
        # If target block is full, attempt to move to another adjacent block
        for dx_alt, dy_alt in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            alt_x, alt_y = self.location[0] + dx_alt, self.location[1] + dy_alt
            alt_block = self.game.city.block(alt_x, alt_y)
            if alt_block.current_zombies < ZOMBIE_CAPACITY:
                current_block.current_zombies -= 1
                alt_block.current_zombies += 1
                self.location = (alt_x, alt_y)
                self.inside = False
                self.action_points -= 2
                self.action_points_lost += 2
                return True

        # No movement if no adjacent block has capacity
        return False

    def handle_barricades(self, current_block):
        """Attack barricades or attempt entry."""
        if current_block.barricade.level > 0 and not self.inside:
            return self.attack_barricade(current_block)

        if current_block.barricade.level == 0 and not self.inside:
            return self.enter()
        
    def attack_barricade(self, building):
        """Attacks the barricades of the given building."""
        if hasattr(building.barricade, "level") and building.barricade.level > 0:
            if random.random() < 0.3:  # 30% chance to successfully attack barricades
                building.barricade.adjust_barricade_sublevel(-1)
                self.action_points -= 1
                self.action_points_lost += 1
                if self.location == self.game.player.location:
                    if building.barricade.level == 0:
                        return "You hear the last of the barricades fall away."
                    return "You hear something attack the barricades."

    def move(self):
        """Randomly moves the zombie to an adjacent block."""
        x, y = self.location[0], self.location[1]
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        new_x, new_y = x + dx, y + dy
        current_block = self.game.city.block(x, y)

        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:  # Ensure within city bounds
            new_block = self.game.city.block(new_x, new_y)
            self.action_points -= 2
            self.action_points_lost += 2
            current_block.current_zombies -= 1
            new_block.current_zombies += 1
            self.location = (new_x, new_y)
            self.inside = False
            return True
        return False

    def attack(self):
        """Attempts to attack a player if in the same block."""
        self.action_points -= 1
        self.action_points_lost += 1
        if random.random() < 0.3:
            self.game.player.take_damage(ZOMBIE_DAMAGE)  # Zombies deal 10 damage
            return "A zombie slams into you!"
        else:
            return "A zombie swipes at you, but misses."

    def enter(self):
        """Enter a building."""
        self.action_points -= 1
        self.action_points_lost += 1
        self.inside = True
    
    def leave(self):
        """Leave a building."""
        self.action_points -= 1
        self.action_points_lost += 1
        self.inside = False
        return "Zombie leaves the building."    
    
    def ransack(self, current_block):
        """Ransack a building."""
        self.action_points -= 1
        self.action_points_lost += 1
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
        self.is_dead = True
        self.hp = 0
        if self.is_human:
            self.game.chat_history.append("A human slumps to the floor, unresponsive.")
            self.is_human = False
        else:
            self.game.chat_history.append("A zombie slumps to the floor, apparently dead.")

    def stand_up(self):
        """Zombie stands up at full health after collecting enough action points."""
        if self.location == self.game.player.location and self.inside == self.game.player.inside:
            self.game.chat_history.append("A zombie stirs, and gets to its feet, swaying.")
        self.is_dead = False
        self.hp = 50
        self.action_points -= 50
        self.action_points_lost += 50

    def status(self):
        """Returns the current status of the zombie."""
        return {
            "Location": self.location,
            "HP": self.hp,
            "Action Points": self.action_points,
            "Dead": self.is_dead,
        }    