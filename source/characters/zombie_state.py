# zombie_state.py

import random
from dataclasses import dataclass

from settings import *
from data import Action, ActionResult, BLOCKS, SkillType
from characters.state import State, MoveTarget, BehaviourResult


@dataclass
class ZombieWeapon:
    name: str
    attack: int
    damage: int

    @classmethod
    def choose(cls):
        """Randomly select hands or teeth and return a ZombieWeapon instance."""
        attack_type, stats = random.choice(list(ZOMBIE_ATTACKS.items()))
        return cls(name=attack_type, attack=stats["attack"], damage=stats["damage"])


class Zombie(State):
    """Represents the zombie state."""
    def __init__(self, character):
        super().__init__(character)     

    def update_name(self):
        """Updates the character's name."""
        self.character.current_name = f"{self.character.name.zombie_adjective} {self.character.name.first_name}"

    def _determine_behaviour(self):
        """Determine the priority for the zombie."""
        # Get block properties at current location
        city = self.game.state.city
        block = city.block(self.character.location[0], self.character.location[1])        
        properties = BLOCKS[block.type]

        # Get character data at current location
        x, y = self.character.location[0], self.character.location[1]
        inside = self.character.inside

        # Get all characters at current location
        block_characters = self.filter_characters_at_location(x, y, inside)

        # Get adjacent block locations and targets
        adjacent_locations = self.get_adjacent_locations()
        move_targets = self.get_move_targets(adjacent_locations, x, y)

        # Priority 1: Stand up if dead
        if self.character.is_dead:
            return BehaviourResult(Action.STAND) if self.character.ap >= STAND_AP else False

        # Priority 2: Attack current target if in current location, otherwise change target if another human in current location
        if len(block_characters.living_humans) > 0:
            result = self._attack_target(block_characters)
            return result

        # Priority 3: If current target exists but not in current location, and no other brainz available, pursue target
        if self.current_target:
            result = self._pursue_target(block, adjacent_locations)
            return result

        # Priority 4: If no current target, move to adjacent target if one exists
        if move_targets:
            random.shuffle(move_targets) # Pick a random target
            return BehaviourResult(Action.MOVE, move_targets[0])

        # Priority 5: With no immediate priorities, let the zombie decide its next action
        if self.character.inside:
            action_weights = {
                Action.RANSACK: 50 if not block.ruined and self.character.has_skill(SkillType.RANSACK) else 0,
                Action.WANDER: 30,
                Action.LEAVE: 20,
            }
            choice = self._make_choice(action_weights)
            if choice:
                return BehaviourResult(choice)
        
        elif properties.is_building:
            action_weights = {
                Action.WANDER: 50,
                Action.DECADE: 25 if block.barricade.level > 0 else 0,
                Action.ENTER: 25 if block.barricade.level == 0 else 0,
            }
            choice = self._make_choice(action_weights)
            if choice:
                return BehaviourResult(choice)            
        
        return BehaviourResult(Action.WANDER)  # No behaviour determined, so wander

    def _attack_target(self, block_characters):
            if self.current_target not in block_characters.living_humans:
                random.shuffle(block_characters.living_humans)
                self.current_target = block_characters.living_humans[0] # Choose a new target
            return BehaviourResult(Action.ATTACK, self.current_target)        

    def _pursue_target(self, block, adjacent_locations):
        # Check if the current target is at the current location but not the same inside status
        if self.current_target.location == self.character.location and self.current_target.inside != self.character.inside:
            if self.character.inside: # Pursue the target outside, if possible
                if block.barricade.level == 0 and (not block.doors_closed or self.character.has_skill(SkillType.MEMORIES_OF_LIFE)):
                    return BehaviourResult(Action.LEAVE)
                else: # Attack barricades if they are in the way
                    return BehaviourResult(Action.DECADE)
            else: # Pursue the target inside, if possible
                if block.barricade.level == 0 and (not block.doors_closed or self.character.has_skill(SkillType.MEMORIES_OF_LIFE)):
                    return BehaviourResult(Action.ENTER)
                else: # Attack the barricades if they are in the way
                    return BehaviourResult(Action.DECADE)
        elif self.current_target.location in adjacent_locations: # If the current target is in an adjacent block, pursue
            for location in adjacent_locations:
                if location == self.current_target.location:
                    dx, dy = location[0] - self.character.location[0], location[1] - self.character.location[1]
                    target_direction = MoveTarget(dx, dy)
            return BehaviourResult(Action.MOVE, target_direction)
        else: # Lose current target if they have escaped pursuit
            self.current_target = None        

    def get_move_targets(self, adjacent_locations, x, y):
        move_targets = []
        for location in adjacent_locations:
            adjacent_x, adjacent_y = location
            adjacent_characters = self.filter_characters_at_location(x, y)
            if adjacent_characters.living_humans:
                dx, dy = adjacent_x - x, adjacent_y - y
                move_target = MoveTarget(dx, dy)
                move_targets.append(move_target)
        if not move_targets: # If no brainz available, look for lit buildings
            city = self.game.state.city
            for location in adjacent_locations:
                adjacent_x, adjacent_y = location
                block = city.block(adjacent_x, adjacent_y)
                properties = BLOCKS[block.type]
                if properties.is_building:
                    if block.lights_on:
                        dx, dy = adjacent_x - x, adjacent_y - y
                        move_target = MoveTarget(dx, dy)
                        move_targets.append(move_target)
        return move_targets        
    
    def attack(self, target):
        weapon = ZombieWeapon.choose()  # Get attack choice

        # Base attack success rate
        attack_chance = weapon.attack
        bonus_damage = 0

        # Apply skill bonuses
        if self.character.has_skill(SkillType.VIGOUR_MORTIS):
            attack_chance += 10
        if weapon.name == 'hands' and self.character.has_skill(SkillType.DEATH_GRIP):
            attack_chance += 15
            if self.character.has_skill(SkillType.REND_FLESH):
                bonus_damage = 1
        if weapon.name == 'teeth' and self.character.has_skill(SkillType.NECK_LURCH):
            attack_chance += 10

        roll = random.randint(1, 100)
        attack_success = roll <= attack_chance
        self.character.ap -= 1

        if attack_success:
            target.take_damage(weapon.damage + bonus_damage)
            self.character.gain_xp(weapon.damage + bonus_damage)
            if target.is_dead:
                self.character.gain_xp(10)

            # Trigger NPC sprite animation if visible
            sprites = list(self.game.game_ui.description_panel.human_sprite_group)
            for sprite in sprites:
                if target == sprite.npc:
                    if target.is_dead:
                        sprite.set_action(2)
                    else:
                        sprite.set_action(3)

            message = f"You attack {target.current_name} with {weapon.name} for {weapon.damage + bonus_damage} damage."
            witness = f"{self.character.current_name} attacks {target.current_name} with {weapon.name}."
            attacked = f"{self.character.current_name} attacks you with {weapon.name} for {weapon.damage + bonus_damage} damage!"
            return ActionResult(True, message, witness, attacked)
        else:
            message = "Your attack misses."
            return ActionResult(False, message)    
        
    def enter(self):
        x, y = self.character.location
        city = self.game.state.city
        building = city.block(x, y)

        if building.barricade.level == 0:
            if building.doors_closed:
                if self.character.has_skill(SkillType.MEMORIES_OF_LIFE):
                    building.doors_closed = False
                    self.character.inside = True
                    self.character.ap -= 1
                    message = "You enter the building, leaving the doors wide open."
                    witness = f"{self.character.current_name} entered the building, leaving the doors wide open."
                    return ActionResult(True, message, witness, sfx='footsteps')
                else:
                    return ActionResult(False, "You need the MEMORIES OF LIFE skill in order to open doors.")
            else:
                self.character.inside = True
                self.character.ap -= 1
                message = "You enter the building."
                witness = f"{self.character.current_name} entered the building."
                return ActionResult(True, message, witness, sfx='footsteps')   
        else:
            return ActionResult(False, "You have to break through the barricades first.")

    def leave(self):
        x, y = self.character.location
        city = self.game.state.city
        building = city.block(x, y)
    
        if building.barricade.level == 0:
            if building.doors_closed:
                if self.character.has_skill(SkillType.MEMORIES_OF_LIFE):
                    self.character.inside = False
                    self.character.ap -= 1
                    message = "You left the building, leaving the doors wide open."
                    witness = f"{self.character.current_name} left the building, leaving the doors wide open."
                    return ActionResult(True, message, witness, sfx='footsteps')   
                else:
                    return ActionResult(False, "You need the MEMORIES OF LIFE skill in order to open doors.")                         
            else:
                self.character.inside = False
                self.character.ap -= 1
                message = "You left the building."
                witness = f"{self.character.current_name} left the building."
                return ActionResult(True, message, witness, sfx='footsteps')
        else:
            return ActionResult(False, "You have to break through the barricades first.")       
        
    def move(self, dx, dy):
        """Moves the character to a new location."""
        x, y = self.character.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:
            self.character.inside = False
            if self.character.has_skill(SkillType.LURCHING_GAIT):
                self.character.ap -= 1
            else:
                self.character.ap -= 2
            self.character.location = (new_x, new_y)
        
        else:
            return False        

    def wander(self):
        """Randomly moves the actor to an adjacent block."""
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        self.move(dx, dy)

    def die(self):
        """Handles the character's death."""
        self.character.is_dead = True
