# actions.py

import random

from settings import *

class ActionExecutor:
    """Handles executing actions for both player and AI characters."""
    def __init__(self, game, actor):
        self.game = game
        self.actor = actor  # Define the actor

    def witness_action(self, message):
        """Append action message to chat if the player is present."""
        player = self.game.player
        if self.actor.location == player.location and self.actor.inside == player.inside:
            self.game.chat_history.append(message)

    def attack(self, target):
        weapon = self.actor.weapon
        if weapon:
            properties = ITEMS[weapon.type]
            if properties.item_function == ItemFunction.FIREARM:
                if weapon.loaded_ammo == 0:
                    return self.game.chat_history.append("Your weapon is out of ammo.")

            roll = random.randint(1, 20)
            attack_roll = (roll + properties.attack) >= ATTACK_DIFFICULTY

            if attack_roll:
                weapon_broke = False
                if properties.item_function == ItemFunction.FIREARM:
                    weapon.loaded_ammo -= 1
                elif properties.item_function == ItemFunction.MELEE:
                    weapon.durability -= 1
                    if weapon.durability <= 0:
                        self.actor.inventory.remove(weapon)
                        self.actor.weapon = None
                        weapon_broke = True

                # Display result in chat window if applicable
                if self.actor == self.game.player:
                    self.game.chat_history.append(f"You attack {target.name} for {properties.damage} damage.")
                    if weapon_broke:
                        self.game.chat_history.append(f"Your weapon breaks!")
                else:
                    self.witness_action(f"{self.actor.name} attacks {target.name} for {properties.damage} damage.")

                return target.npc.take_damage(properties.damage)
            else:
                if self.actor == self.game.player:
                    self.game.chat_history.append("Your attack misses.")

        else: # If no weapon equipped, punch the enemy.
            roll = random.randint(1, 20)
            attack_roll = roll >= ATTACK_DIFFICULTY

            if attack_roll:
                # Display result in chat window if applicable
                if self.actor == self.game.player:
                    self.game.chat_history.append(f"You punch {target.name} for 1 damage.")
                else:
                    self.witness_action(f"{self.actor.name} punches {target.name} for 1 damage.")
            else:
                return "You try punching the zombie, but miss."


    def reload(self):
        weapon = self.actor.weapon.sprite
        if weapon.type == ItemType.PISTOL:
            weapon.loaded_ammo = weapon.max_ammo
            if self.actor == self.game.player:
                self.game.chat_history.append("You slap a new pistol clip into your gun.")
            else:
                self.witness_action(f"{self.actor.name} reloads their pistol.")
        elif weapon.type == ItemType.SHOTGUN:
            weapon.loaded_ammo += 1
            if self.actor == self.game.player:
                self.game.chat_history.append("You load a shell into your shotgun.")
            else:
                self.witness_action(f"{self.actor.name} loads a shell into their shotgun.")

    def move(self, dx, dy):
        """Moves the actor to a new location."""
        x, y = self.actor.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < 100 and 0 <= new_y < 100:
            # If a player moves, they are no longer inside.
            if self.actor.inside:
                self.actor.inside = False
            self.actor.location = (new_x, new_y)

    def wander(self):
        """Randomly moves the actor to an adjacent block."""
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

    def barricade(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        success_chances = [1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2]
        if properties.is_building and self.inside:
            if current_block.barricade.level >= 7 and current_block.barricade.sublevel >= 4:
                return "You can't add more barricades.", False
            
            success_chance = success_chances[current_block.barricade.level]
            success = random.random() < success_chance
            if success:
                add_barricade = current_block.barricade.adjust_barricade_sublevel(1)
                if not add_barricade:
                    return "You can't add more barricades.", False
                elif current_block.barricade.level == 4 and current_block.barricade.sublevel == 2:
                    return f"You reinforce the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in.", False
                elif current_block.barricade.sublevel == 0:
                    return f"You reinforce the barricade. The building is now {current_block.barricade.get_barricade_description()}.", False
                elif current_block.barricade.sublevel > 0:
                    return f"You reinforce the barricade.", False
            else:
                return "You could not find anything to add to the barricade.", False
        else:
            return "You can't barricade here.", False

    def repair_building(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building and self.inside:
            if current_block.is_ransacked:
                current_block.is_ransacked = False
                return "You repaired the interior of the building and cleaned up the mess.", False
            else:
                return "There's nothing to repair here.", False

    def enter(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building:
            if not self.inside:
                if current_block.barricade.level == 0:
                    self.inside = True
                    return "You entered the building."
                elif current_block.barricade.level <= 4:
                    self.inside = True
                    return "You climb through the barricades and are now inside."
                else:
                    return "You can't find a way through the barricades."
            return "You are already inside."
        return "This is not a building."

    def leave(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        properties = BLOCKS[current_block.type]
        if properties.is_building:
            if self.inside:
                if current_block.barricade.level == 0:
                    self.inside = False
                    return "You left the building."
                elif current_block.barricade.level <= 4:
                    self.inside = False
                    return "You climb through the barricades and are now outside."
                else:
                    return "The building has been so heavily barricaded that you cannot leave through the main doors."                    
            return "You are already outside."
        return "You can't leave this place."

    def search(self):
        items_held = len(self.inventory.sprites())
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        block_properties = BLOCKS[current_block.type]
        if block_properties.is_building:
            if self.inside:
                if current_block.lights_on:
                    multiplier = LIGHTSON_MULTIPLIER
                elif current_block.is_ransacked:
                    multiplier = RANSACKED_MULTIPLIER
                else:
                    multiplier = SEARCH_MULTIPLIER
                items = list(self.search_chances.keys())
                random.shuffle(items)

                for item_type in items:
                    search_chance = self.search_chances[item_type].get(current_block.type.name, 0.0) # Default to 0.0 if item not found
                    roll = random.random()
                    if roll < search_chance * multiplier:
                        item = self.create_item(item_type)
                        item_properties = ITEMS[item.type]
                        if item is not None:
                            if items_held >= MAX_ITEMS:
                                return f"You found {item_properties.description}, but you are carrying too much and it falls under a pile of debris!", False
                            elif item_type == 'PORTABLE_GENERATOR':
                                for sprite in self.inventory:
                                    if hasattr(sprite, 'type') and sprite.type == ItemType.PORTABLE_GENERATOR:
                                        return 'You found Portable Generator, but you can only carry one at a time.', False
                            self.inventory.add(item)
                            return f"You found {item_properties.description}!", False
                        else:
                            return f"Tried to add {item_properties.description} to inventory!", False
                return f"You found nothing.", False
            
            else:
                return "You search around the building but there is nothing to be found.", False
        else:
            return "You search but there is nothing to be found.", False
        
    def install_generator(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        if current_block.generator_installed:
            return "Generator is already installed.", False
        else:
            current_block.generator_installed = True
            return "You install a generator. It needs fuel to operate.", True
        
    def fuel_generator(self):
        current_x, current_y = self.location
        current_block = self.city.block(current_x, current_y)
        if current_block.lights_on:
            return "Generator already has fuel.", False
        elif not current_block.generator_installed:
            return "You need to install a generator first.", False
        else:
            current_block.fuel_expiration = self.ticker + FUEL_DURATION
            current_block.lights_on = True
            return "You fuel the generator. The lights are now on.", True        
        
    def stand(self):
        """Actor stands up at full health after collecting enough action points."""
        if self.location == self.game.player.location and self.inside == self.game.player.inside:
            self.game.chat_history.append("A zombie stirs, and gets to its feet, swaying.")
        self.is_dead = False
        self.hp = 50
        self.action_points -= 50
        self.action_points_lost += 50        