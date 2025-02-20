# human_state.py

import random

from settings import *
from data import Action, ActionResult, BLOCKS, BlockType, Occupation, OccupationCategory, OCCUPATIONS, ITEMS, ItemType, ItemFunction, SkillType
from characters.state import State, MoveTarget, BehaviourResult


class Human(State):
    """Represents the human state."""
    def __init__(self, character):
        super().__init__(character)


    def update_name(self):
        """Updates the character's name."""
        self.character.current_name = f"{self.character.name.first_name} {self.character.name.last_name}"

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
            return BehaviourResult(Action.STAND) if self.character.ap >= STAND_AP else False
        
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
                return BehaviourResult(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return BehaviourResult(Action.WANDER) # Move randomly if no desireable target present

        # Priority 3: If outside, find a safe place to hide
        if not self.character.inside:
            if block.type in target_types:
                return BehaviourResult(Action.ENTER) # Enter current building if a desirable target
            elif target_locations:
                target_location = random.choice(target_locations)
                dx, dy = target_location[0] - x, target_location[1] - y
                return BehaviourResult(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return BehaviourResult(Action.WANDER) # Move randomly if no desireable target present

        if self.character.inside and not block.doors_closed:
            return BehaviourResult(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return BehaviourResult(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return BehaviourResult(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return BehaviourResult(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return BehaviourResult(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and self.character.has_skill(SkillType.CONSTRUCTION):
                return BehaviourResult(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return BehaviourResult(Action.BARRICADE)
                   
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
            self.character.action.execute(Action.EQUIP, weapon)

            if block_characters.living_zombies:
                return BehaviourResult(Action.ATTACK, block_characters.living_zombies[0])
            
        # Priority 3: If outside, find a safe place to hide
        if not self.character.inside:
            if block.type in target_types:
                return BehaviourResult(Action.ENTER) # Enter current building if a desirable target
            elif target_locations:
                target_location = random.choice(target_locations)
                dx, dy = target_location[0] - x, target_location[1] - y
                return BehaviourResult(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return BehaviourResult(Action.WANDER) # Move randomly if no desireable target present

        if self.character.inside and not block.doors_closed:
            return BehaviourResult(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return BehaviourResult(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return BehaviourResult(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return BehaviourResult(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return BehaviourResult(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and self.character.has_skill(SkillType.CONSTRUCTION):
                return BehaviourResult(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return BehaviourResult(Action.BARRICADE)

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
            self.character.action.execute(Action.EQUIP, weapon)

            if block_characters.living_zombies:
                return BehaviourResult(Action.ATTACK, block_characters.living_zombies[0])
            
        # Priority 3: If outside, find a safe place to hide
        if not self.character.inside:
            if block.type in target_types:
                return BehaviourResult(Action.ENTER) # Enter current building if a desirable target
            elif target_locations:
                target_location = random.choice(target_locations)
                dx, dy = target_location[0] - x, target_location[1] - y
                return BehaviourResult(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return BehaviourResult(Action.WANDER) # Move randomly if no desireable target present

        if self.character.inside and not block.doors_closed:
            return BehaviourResult(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return BehaviourResult(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return BehaviourResult(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return BehaviourResult(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return BehaviourResult(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and self.character.has_skill(SkillType.CONSTRUCTION):
                return BehaviourResult(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return BehaviourResult(Action.BARRICADE)       
            
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
            self.character.action.execute(Action.EQUIP, weapon)

            if block_characters.living_zombies:
                return BehaviourResult(Action.ATTACK, block_characters.living_zombies[0])
            
        # Priority 3: If outside, find a safe place to hide
        if not self.character.inside:
            if block.type in target_types:
                return BehaviourResult(Action.ENTER) # Enter current building if a desirable target
            elif target_locations:
                target_location = random.choice(target_locations)
                dx, dy = target_location[0] - x, target_location[1] - y
                return BehaviourResult(Action.MOVE, MoveTarget(dx, dy)) # Move to nearby building if desirable target
            else:
                return BehaviourResult(Action.WANDER) # Move randomly if no desireable target present

        if self.character.inside and not block.doors_closed:
            return BehaviourResult(Action.CLOSE_DOORS)

        # Priority 4: If conditions allow searching for items, search
        if self._can_search(block, has_generator, has_fuel, has_toolbox, has_weapon):
            return BehaviourResult(Action.SEARCH)
        
        # Priority 5: Install generator and fuel it
        if self.character.inside and properties.is_building and has_generator and has_fuel:
            if not block.generator_installed:
                genny = next((item for item in self.character.inventory if item.type == ItemType.PORTABLE_GENERATOR))
                return BehaviourResult(Action.USE, genny)
            else:
                if not block.lights_on:
                    fuel = next((item for item in self.character.inventory if item.type == ItemType.FUEL_CAN))
                    return BehaviourResult(Action.USE, fuel)
                
        # Priority 6: Repair building if ransacked, or barricade
        if self.character.inside and properties.is_building:
            if block.ransack_level > 0 and not block.ruined and has_toolbox:
                return BehaviourResult(Action.REPAIR_BUILDING)
            elif block.ruined and has_toolbox and self.character.has_skill(SkillType.CONSTRUCTION):
                return BehaviourResult(Action.REPAIR_BUILDING)
            if block.barricade.level < 4 and has_toolbox:
                return BehaviourResult(Action.BARRICADE)
        
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
                    self.character.action.execute(Action.DROP, item)

        return True
    
    def attack(self, target):
        weapon = self.character.weapon
        if weapon:
            properties = ITEMS[weapon.type]

            
            if properties.item_function == ItemFunction.FIREARM and weapon.loaded_ammo == 0:
                return ActionResult(False, "Your firearm is out of ammo.")
            elif properties.item_function == ItemFunction.SCIENCE:
                result = self._science_attack(target, weapon)
                return result

            # Base attack success rate
            attack_chance = properties.attack

            # Apply skill bonuses
            if properties.item_function == ItemFunction.FIREARM:
                if self.character.has_skill(SkillType.BASIC_FIREARMS_TRAINING):
                    attack_chance += 25
                if weapon.type == ItemType.PISTOL:
                    if self.character.has_skill(SkillType.PISTOL_TRAINING):
                        attack_chance += 25
                    if self.character.has_skill(SkillType.ADV_PISTOL_TRAINING):
                        attack_chance += 10
                if weapon.type == ItemType.SHOTGUN:
                    if self.character.has_skill(SkillType.SHOTGUN_TRAINING):
                        attack_chance += 25
                    if self.character.has_skill(SkillType.ADV_SHOTGUN_TRAINING):
                        attack_chance += 10
            if properties.item_function == ItemFunction.MELEE:
                if self.character.has_skill(SkillType.HAND_TO_HAND):
                    attack_chance += 15
                if weapon.type == ItemType.KNIFE and self.character.has_skill(SkillType.KNIFE_COMBAT):
                        attack_chance += 15
                if weapon.type == ItemType.FIRE_AXE and self.character.has_skill(SkillType.AXE_PROFICIENCY):
                        attack_chance += 15
            
            roll = random.randint(1, 100)
            attack_success = roll <= attack_chance
            self.character.ap -= 1

            if attack_success:
                # Resolve action result
                self._deplete_weapon()
                target.take_damage(properties.damage)
                self.character.gain_xp(properties.damage)
                if target.is_dead:
                    self.character.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)


                if target.is_dead and self.character.has_skill(SkillType.HEADSHOT):
                    target.permadeath = True
                    if self.character.weapon:
                        message = f"You deal a headshot for {properties.damage} damage."
                        witness = f"{self.character.current_name} deals a headshot against {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                    else:
                        message = f"You deal a headshot for {properties.damage} damage. Your weapon breaks!"
                        witness = f"{self.character.current_name} deals a headshot against {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                else:
                    if self.character.weapon:
                        message = f"Your attack hits for {properties.damage} damage."
                        witness = f"{self.character.current_name} attacks {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)
                    else:
                        message = f"Your attack hits for {properties.damage} damage. Your weapon breaks!"
                        witness = f"{self.character.current_name} attacks {target.current_name} with {properties.description}."
                        return ActionResult(True, message, witness)                    
            else:
                return ActionResult(False, "Your attack misses.")

        else: # If no weapon equipped, punch the enemy.
            roll = random.randint(1, 20)
            attack_success = roll >= ATTACK_DIFFICULTY

            self.character.ap -= 1

            if attack_success:
                target.take_damage(1)
                self.character.gain_xp(1)
                if target.is_dead:
                    self.character.gain_xp(10)                

                # Trigger NPC sprite animation if visible
                sprites = list(self.game.game_ui.description_panel.zombie_sprite_group)
                for sprite in sprites:
                    if target == sprite.npc:
                        if target.is_dead:
                            sprite.set_action(2)
                        else:
                            sprite.set_action(3)

                return ActionResult(True, "You punch the enemy for 1 damage.", f"{self.character.current_name} punches {target.current_name}.")
            else:
                return ActionResult(False, "Your attack misses.")
            
    def _deplete_weapon(self):
        """Reduce loaded ammo or durability, depending on weapon type."""
        properties = ITEMS[self.character.weapon.type]
        if properties.item_function == ItemFunction.FIREARM:
            self.character.weapon.loaded_ammo -= 1
        elif properties.item_function == ItemFunction.MELEE:
            self.character.weapon.durability -= 1
            if self.character.weapon.durability <= 0:
                self.character.inventory.remove(self.character.weapon)
                self.character.weapon = None  

    def enter(self):
        x, y = self.character.location
        city = self.game.state.city
        building = city.block(x, y)

        if building.barricade.level == 0:
            self.character.inside = True
            self.character.ap -= 1
            message = "You entered the building."
            witness = f"{self.character.current_name} entered the building."
            return ActionResult(True, message, witness, sfx='footsteps')
        elif building.barricade.level <= 4:
            self.character.inside = True
            self.character.ap -= 1
            message = "You climb through the barricades and are now inside."
            witness = f"{self.character.current_name} climbed through the barricades and is now inside."
            return ActionResult(True, message, witness, sfx='footsteps')
        else:
            return ActionResult(False, "You can't find a way through the barricades.")

    def leave(self):
        x, y = self.character.location
        city = self.game.state.city
        building = city.block(x, y)

        if building.barricade.level == 0:
            self.character.inside = False
            self.character.ap -= 1
            message = "You left the building."
            witness = f"{self.character.current_name} left the building."
            return ActionResult(True, message, witness, sfx='footsteps')
        if building.barricade.level <= 4:
            self.character.inside = False
            self.character.ap -= 1
            message = "You climb through the barricades and are now outside."
            witness = f"{self.character.current_name} climbed through the barricades and is now outside."
            return ActionResult(True, message, witness, sfx='footsteps')
        else:
            return ActionResult(False, "The building has been so heavily barricaded that you cannot leave through the main doors.")
        
    def move(self, dx, dy):
        """Moves the character to a new location."""
        city = self.game.state.city
        x, y = self.character.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:
            new_block = city.block(new_x, new_y)
            block_properties = BLOCKS[new_block.type]

            if block_properties.is_building:
                if self.character.has_skill(SkillType.FREE_RUNNING):
                    if new_block.ruined:
                        self.character.inside = False
                        self._fall()                    
                else:
                    self.character.inside = False                        
            else:
                self.inside = False

            self.character.ap -= 1
            self.character.location = (new_x, new_y)
        
        else:
            return False   

    def _fall(self):
        """Character falls from a building, taking damage."""
        self.character.take_damage(5, fatal=False)
        if self.character == self.game.state.player:
            self.game.chat_history.append("You fall from the crumbling building, injuring yourself.")             

    def wander(self):
        """Randomly moves the actor to an adjacent block."""
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        self.move(dx, dy)

    def die(self):
        """Handles the character's death."""
        self.character.is_dead = True
        self.character.is_human = False
        self.character.get_state()

        # Reassign passive skill effects
        for skill in self.character.human_skills:
            self.character.apply_skill_effect(skill, remove=True)
        for skill in self.character.zombie_skills:
            self.character.apply_skill_effect(skill)            