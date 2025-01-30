# actions.py

class ActionExecutor:
    """Handles executing actions for both player and AI characters."""
    def __init__(self, character):
        self.character = character  # Define the actor

        def attack(self, target):
        if self.weapon:
            weapon = self.weapon.sprite
            properties = ITEMS[weapon.type]
            if properties.item_function == ItemFunction.FIREARM:
                if weapon.loaded_ammo == 0:
                    return "Your weapon is out of ammo."

            roll = random.randint(1, 20)
            attack_roll = (roll + properties.attack) >= ATTACK_DIFFICULTY

            if attack_roll:
                if properties.item_function == ItemFunction.FIREARM:
                    weapon.loaded_ammo -= 1
                elif properties.item_function == ItemFunction.MELEE:
                    weapon.durability -= 1
                    if weapon.durability <= 0:
                        weapon.kill()
                        return target.npc.take_damage(properties.damage) + " Your weapon breaks!"
                return target.npc.take_damage(properties.damage)
            else:
                return "Your attack misses."
        else:
            roll = random.randint(1, 20)
            attack_roll = roll >= ATTACK_DIFFICULTY

            if attack_roll:
                return "You punch the zombie. " + target.npc.take_damage(1)
            else:
                return "You try punching the zombie, but miss."


    def reload(self):
        weapon = self.weapon.sprite
        if weapon.type == ItemType.PISTOL:
            weapon.loaded_ammo = weapon.max_ammo
            return "You slap a new pistol clip into your gun."
        elif weapon.type == ItemType.SHOTGUN:
            weapon.loaded_ammo += 1
            return "You load a shell into your shotgun."

    def move(self, dx, dy):
        """Moves the player to a new location on the grid."""
        x, y = self.location
        new_x, new_y = x + dx, y + dy

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < 100 and 0 <= new_y < 100:
            # If a player moves, they are no longer inside.
            if self.inside:
                self.inside = False
            self.location = (new_x, new_y)
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