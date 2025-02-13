# human_state.py

import random

from settings import *
from data import Action, BLOCKS, BlockType, Occupation, OccupationCategory, OCCUPATIONS, ItemType
from characters.state import State, MoveTarget, Result


class Human(State):
    """Represents the human state."""
    def __init__(self, game, character):
        super().__init__(game, character)

    def _determine_behaviour(self):
        """Determine the priority for the NPC."""
        # Get block properties at current location
        city = self.game.state.city
        x, y = self.character.location[0], self.character.location[1]
        block = city.block(x, y)        
        properties = BLOCKS[block.type]        

        # Get character properties
        occupation = self.character.occupation
        inventory = self.character.inventory
        inside = self.character.inside

        # Get adjacent locations
        adjacent_locations = self.get_adjacent_locations()

        # Get characters at character location
        block_characters = self.filter_characters_at_location(x, y, inside)

        # Priority 1: Stand up if dead
        if self.character.is_dead:
            return Result(Action.STAND) if self.character.ap >= STAND_AP else False
        
        # Priority 2+: Determine action based on occupation  
        occupation_properties = OCCUPATIONS[occupation]      
        if occupation == Occupation.CONSUMER:
            return self._determine_consumer_behaviour(block, properties, block_characters, adjacent_locations, x, y)
            
        if occupation_properties.occupation_category == OccupationCategory.CIVILIAN:
            return self._determine_civilian_behaviour(block, properties, block_characters, inventory)
        
        if occupation_properties.occupation_category == OccupationCategory.SCIENCE:
            return self._determine_science_behaviour(block, properties, block_characters, inventory)
                
        if occupation_properties.occupation_category == OccupationCategory.MILITARY:
            return self._determine_military_behaviour(block_characters)
            
        if occupation == Occupation.CORPSE:
            return self._determine_corpse_behaviour()
        
    def _determine_consumer_behaviour(self, block, properties, block_characters, adjacent_locations, x, y):
        # Check for target locations
        target_types = [BlockType.FACTORY, BlockType.AUTO_REPAIR, BlockType.WAREHOUSE]
        target_locations = [
            loc for loc in adjacent_locations
            if self._is_target_location(loc, target_types)
        ]        

        # Check inventory for needed items
        has_generator = any(item.type == ItemType.PORTABLE_GENERATOR for item in self.character.inventory)
        has_fuel = any(item.type == ItemType.FUEL_CAN for item in self.character.inventory)
        has_toolbox = any(item.type == ItemType.TOOLBOX for item in self.character.inventory)

        # Priority 2: Flee if zombies are present
        if len(block_characters.living_zombies) > 0:
            if target_locations:
                target_location = random.choice(target_locations)
                dx, dy = target_location[0] - x, target_location[1] - y
                return Result(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return Result(Action.WANDER) # Move randomly if no desireable target present

        # Priority 3: If outside, find a safe place to hide
        if not self.character.inside:
            if block.type in target_types:
                return Result(Action.ENTER) # Enter current building if a desirable target
            elif target_locations:
                target_location = random.choice(target_locations)
                dx, dy = target_location[0] - x, target_location[1] - y
                return Result(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return Result(Action.WANDER) # Move randomly if no desireable target present

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox):
            return Result(Action.SEARCH)
        

#####################################################################
        elif self.character.location == self.game.state.player.location and self.character.inside == self.game.state.player.inside:
            return Result(Action.GIVE_QUEST)
        elif not self.character.inside and properties.is_building:
            return Result(Action.ENTER)
        elif not self.character.inside and not properties.is_building:
            return Result(Action.WANDER)
        
    def _determine_civilian_behaviour(self, block, properties, block_characters, inventory):
        if properties.is_building and not self.character.inside:
            return Result(Action.ENTER)
        elif self.character.inside:
            if block_characters.living_zombies:
                return Result(Action.ATTACK, block_characters.living_zombies[0])
            elif block.ransack_level > 0:
                for item in inventory:
                    if item.type == ItemType.TOOLBOX:
                        return Result(Action.USE, item)
            elif block.barricade.level <= 4:
                return Result(Action.BARRICADE)
            else:
                return Result(Action.SEARCH)

    def _determine_science_behaviour(self, block, properties, block_characters, inventory):
        if properties.is_building and not self.character.inside:
            return Result(Action.ENTER)
        elif self.character.inside:
            if block_characters.living_zombies:
                return Result(Action.ATTACK, block_characters.living_zombies[0])
            elif block.ransack_level > 0:
                for item in inventory:
                    if item.type == ItemType.TOOLBOX:
                        return Result(Action.USE, item)
            elif block.barricade.level <= 4:
                return Result(Action.BARRICADE)
            else:
                return Result(Action.SEARCH)        
            
    def _determine_military_behaviour(self, block_characters):
        if block_characters.living_zombies:
            return Result(Action.ATTACK, block_characters.living_zombies[0])
        else:
            return Result(Action.WANDER)
        
    def _determine_corpse_behaviour(self):
        pass

    def _is_target_location(self, location, target_types):
        """Determine if location is a desirable target."""
        x, y = location
        city = self.game.state.city
        block = city.block(x, y)

        if block.type in target_types:
            return True
        else:
            return False
        
    def _can_search(self, block, has_generator, has_fuel, has_toolbox):
        return False