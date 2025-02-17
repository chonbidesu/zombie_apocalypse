# human_state.py

import random

from settings import *
from data import Action, BLOCKS, BlockType, Occupation, OccupationCategory, OCCUPATIONS, ITEMS, ItemType, ItemFunction, SkillType
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
            return self._determine_consumer_behaviour(block, block_characters, adjacent_locations, x, y)
            
        if occupation_properties.occupation_category == OccupationCategory.CIVILIAN:
            return self._determine_civilian_behaviour(block, block_characters, adjacent_locations, x, y)
        
        if occupation_properties.occupation_category == OccupationCategory.SCIENCE:
            return self._determine_science_behaviour(block, block_characters, adjacent_locations, x, y)
                
        if occupation_properties.occupation_category == OccupationCategory.MILITARY:
            return self._determine_military_behaviour(block, block_characters, adjacent_locations, x, y)
            
        if occupation == Occupation.CORPSE:
            return self._determine_corpse_behaviour()
        
    def _determine_consumer_behaviour(self, block, block_characters, adjacent_locations, x, y):
        properties = BLOCKS[block.type]        

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
        has_weapon = any(
            ITEMS[item.type].item_function == ItemFunction.MELEE
            for item in self.character.inventory
        )

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

        if self.character.inside and not block.doors_closed:
            return Result(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return Result(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return Result(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return Result(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return Result(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and SkillType.CONSTRUCTION in self.character.human_skills:
                return Result(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return Result(Action.BARRICADE)
                   
    def _determine_civilian_behaviour(self, block, block_characters, adjacent_locations, x, y):
        properties = BLOCKS[block.type]        
        inventory = self.character.inventory       
        
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
        has_weapon = any(
            ITEMS[item.type].item_function == ItemFunction.MELEE or ITEMS[item.type].item_function == ItemFunction.FIREARM
            for item in self.character.inventory
        )
        
        # Priority 2: If zombie is present and weapon equipped, attack
        if not self.character.weapon and has_weapon:
            weapon = next((item for item in inventory if ITEMS[item.type].item_function == ItemFunction.MELEE or ITEMS[item.type].item_function == ItemFunction.FIREARM))
            self.character.action.equip(weapon)

            if block_characters.living_zombies:
                return Result(Action.ATTACK, block_characters.living_zombies[0])
            
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

        if self.character.inside and not block.doors_closed:
            return Result(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return Result(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return Result(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return Result(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return Result(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and SkillType.CONSTRUCTION in self.character.human_skills:
                return Result(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return Result(Action.BARRICADE)

    def _determine_science_behaviour(self, block, block_characters, adjacent_locations, x, y):
        properties = BLOCKS[block.type]        
        inventory = self.character.inventory       
        
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
        has_weapon = any(
            ITEMS[item.type].item_function == ItemFunction.MELEE or ITEMS[item.type].item_function == ItemFunction.FIREARM
            for item in self.character.inventory
        )
        
        # Priority 2: If zombie is present and weapon equipped, attack
        if not self.character.weapon and has_weapon:
            weapon = next((item for item in inventory if ITEMS[item.type].item_function == ItemFunction.MELEE or ITEMS[item.type].item_function == ItemFunction.FIREARM))
            self.character.action.equip(weapon)

            if block_characters.living_zombies:
                return Result(Action.ATTACK, block_characters.living_zombies[0])
            
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

        if self.character.inside and not block.doors_closed:
            return Result(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return Result(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return Result(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return Result(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return Result(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and SkillType.CONSTRUCTION in self.character.human_skills:
                return Result(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return Result(Action.BARRICADE)       
            
    def _determine_military_behaviour(self, block, block_characters, adjacent_locations, x, y):
        properties = BLOCKS[block.type]        
        inventory = self.character.inventory       
        
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
        has_weapon = any(
            ITEMS[item.type].item_function == ItemFunction.MELEE or ITEMS[item.type].item_function == ItemFunction.FIREARM
            for item in self.character.inventory
        )
        
        # Priority 2: If zombie is present and weapon equipped, attack
        if not self.character.weapon and has_weapon:
            weapon = next((item for item in inventory if ITEMS[item.type].item_function == ItemFunction.MELEE or ITEMS[item.type].item_function == ItemFunction.FIREARM))
            self.character.action.equip(weapon)

            if block_characters.living_zombies:
                return Result(Action.ATTACK, block_characters.living_zombies[0])
            
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

        if self.character.inside and not block.doors_closed:
            return Result(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return Result(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return Result(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return Result(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return Result(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and SkillType.CONSTRUCTION in self.character.human_skills:
                return Result(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return Result(Action.BARRICADE)
        
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
        
    def _can_search(self, block, has_generator, has_fuel, has_toolbox, has_weapon):
        properties = BLOCKS[block.type]
        if (has_generator and has_fuel and has_toolbox and has_weapon) or \
        not properties.is_building or not self.character.inside:
            return False
        if len(self.character.inventory) >= 10:
            for item in self.character.inventory:
                if ITEMS[item.type].item_function in [ItemFunction.AMMO, ItemFunction.FIREARM] or \
                item.type in [ItemType.BINOCULARS, ItemType.DNA_EXTRACTOR, ItemType.MAP, ItemType.SYRINGE]:
                    self.character.action.drop(item)

        return True