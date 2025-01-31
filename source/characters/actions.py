# actions.py

import random

from settings import *
from data import Action, ITEMS, ItemType, ItemFunction, BLOCKS

class ActionExecutor:
    """Handles executing actions for both player and AI characters."""
    def __init__(self, game, actor):
        self.game = game
        self.actor = actor  # Define the acting character

    def execute(self, action, target):
        """Execute AI and player actions."""

        # System actions
        if action == Action.QUIT:
            self.game.quit_game()

        elif action == Action.PAUSE:
            self.game.pause_game()

        elif action == Action.OPTIONS:
            pass # NEED TO SET THIS UP

        elif action == Action.CLOSE_MAP:
            self.close_map()

        elif action == Action.ZOOM_IN:
            self.zoom_in()

        elif action == Action.ZOOM_OUT:
            self.zoom_out()

        # Movement
        elif action == Action.MOVE_UP:
            self.move(0, -1)
        elif action == Action.MOVE_DOWN:
            self.move(0, 1)
        elif action == Action.MOVE_LEFT:
            self.move(-1, 0)
        elif action == Action.MOVE_RIGHT:
            self.move(1, 0)
        elif action == Action.MOVE_UPLEFT:
            self.move(-1, -1)
        elif action == Action.MOVE_UPRIGHT:
            self.move(1, -1)
        elif action == Action.MOVE_DOWNLEFT:
            self.move(-1, 1)
        elif action == Action.MOVE_DOWNRIGHT:
            self.move(1, 1)       
        elif action == Action.MOVE:
            dx, dy = target.dx, target.dy
            self.move(dx, dy)
        
        # Combat
        elif action == Action.ATTACK:
            self.attack(target)            

        # Building actions
        elif action == Action.BARRICADE:
            self.barricade()
        elif action == Action.SEARCH:
            self.search()
        elif action == Action.ENTER:
            self.enter()
        elif action == Action.LEAVE:
            self.leave()

        # Inventory actions
        elif action == Action.EQUIP:
            self.equip(target)

        elif action == Action.UNEQUIP:
            self.unequip(target)

        elif action == Action.USE:
            self.use(target)
     
        elif action == Action.DROP:
            self.drop(target)

        # Update sprites after taking action
        self.game.game_ui.update()

    def attack(self, target):
        """Execute an attack depending on the attacker's state."""
        if self.actor.is_human:
            self._human_attack(target)
        else:
            self._zombie_attack(target)

    def _human_attack(self, target):
        weapon = self.actor.weapon
        if weapon:
            properties = ITEMS[weapon.type]
            if properties.item_function == ItemFunction.FIREARM and weapon.loaded_ammo == 0:
                    return False

            roll = random.randint(1, 20)
            attack_success = (roll + properties.attack) >= ATTACK_DIFFICULTY

            if attack_success:
                self._deplete_weapon(weapon, properties)
                target.npc.take_damage(properties.damage)

        else: # If no weapon equipped, punch the enemy.
            roll = random.randint(1, 20)
            attack_success = roll >= ATTACK_DIFFICULTY

            if attack_success:
                target.npc.take_damage(1)

    def _zombie_attack(self, target):
        attack_type, damage = self._get_zombie_attack()
        roll = random.randint(1, 20)
        attack_success = roll >= ATTACK_DIFFICULTY

        if attack_success:
            target.take_damage(damage)

    def _deplete_weapon(self, weapon, properties):
        """Reduce loaded ammo or durability, depending on weapon type."""
        if properties.item_function == ItemFunction.FIREARM:
            weapon.loaded_ammo -= 1
        elif properties.item_function == ItemFunction.MELEE:
            weapon.durability -= 1
            if weapon.durability <= 0:
                self.actor.inventory.remove(weapon)
                self.actor.weapon = None        

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

    def equip(self, item):        
        properties = ITEMS[item.type]
        if properties.item_function == ItemFunction.MELEE or properties.item_function == ItemFunction.FIREARM:
            player.weapon = item
            self.game.chat_history.append(f"Equipped {properties.description}.")
        else:
            self.game.chat_history.append(f"You can't equip {properties.description}!")

    def unequip(self, item):
        properties = ITEMS[item.type]
        player.weapon = None
        self.game.chat_history.append(f"Unequipped {properties.description}.")

    def use(self, item):
        properties = ITEMS[item.type]

        if item.type == ItemType.FIRST_AID_KIT:
            if player.hp < player.max_hp:
                player.heal(20)
                player.inventory.remove(item)
                self.game.chat_history.append("Used a first aid kit, feeling a bit better.")
            else:
                self.game.chat_history.append("You already feel healthy.")
    
        elif item.type == ItemType.PORTABLE_GENERATOR:
            if player.inside:
                self.game.game_ui.action_progress.start('Installing generator', player.install_generator)
                result, item_used = player.install_generator()
                self.game.chat_history.append(result)
                if item_used:
                    item.kill()
            else:
                self.game.chat_history.append("Generators must be installed inside buildings.")
    
        elif item.type == ItemType.FUEL_CAN:
            if player.inside:
                self.game.game_ui.action_progress.start('Fuelling generator')
                result, item_used = player.fuel_generator()
                self.game.chat_history.append(result)
                if item_used:
                    item.kill()
            else:
                self.game.chat_history.append("There is no generator here.")

        elif item.type == ItemType.TOOLBOX:
            if player.inside:
                self.game.game_ui.action_progress.start('Repairing building')
                self.game.chat_history.append(player.repair_building())
            else:
                self.game.chat_history.append("You have to be inside a building to use this.")

        elif item.type == ItemType.MAP:
            self.game.reading_map = True
        
        elif item.type == ItemType.PISTOL_CLIP:
            weapon = player.weapon.sprite
            if weapon.type == ItemType.PISTOL:
                if weapon.loaded_ammo < weapon.max_ammo:
                    self.game.chat_history.append(player.reload())
                    item.kill()
                else:
                    self.game.chat_history.append("Your weapon is already fully loaded.")
            else:
                self.game.chat_history.append(f"You can't reload {properties.description}.")

        elif item.type == ItemType.SHOTGUN_SHELL:
            weapon = player.weapon.sprite
            if weapon.type == ItemType.SHOTGUN:
                if weapon.loaded_ammo < weapon.max_ammo:
                    self.game.chat_history.append(player.reload())
                    item.kill()
                else:
                    self.game.chat_history.append("Your weapon is already fully loaded.")
            else:
                self.game.chat_history.append(f"You can't reload {properties.description}.")               

    def drop(self, item):
        properties = ITEMS[item.type]
        item.kill()
        self.game.chat_history.append(f"Dropped {properties.description}.")        

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

    def close_map(self):
        self.game.reading_map = False
    
    def zoom_in(self):
        self.game.game_ui.map.zoom_in = True

    def zoom_out(self):
        self.game.game_ui.map.zoom_in = False


