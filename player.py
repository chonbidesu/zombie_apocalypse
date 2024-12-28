# player.py

class Player:
    """Represents the player's character."""
    def __init__(self, city, human_name, zombie_name, gender, age, occupation, x, y):
        self.human_name = human_name
        self.zombie_name = zombie_name
        self.gender = gender
        self.age = age
        self.occupation = occupation
        self.skills_human = []  # Skills active when human
        self.skills_zombie = []  # Skills active when a zombie
        self.inventory = []  # Items carried by the player
        self.max_hp = 100  # Maximum hit points
        self.hp = self.max_hp  # Current hit points
        self.max_action_points = 100  # Maximum action points
        self.action_points = self.max_action_points  # Current action points
        self.location = (x, y)  # Initial location in the 100x100 grid
        self.city = city
        self.inside = False
        self.starting_trait = self.assign_starting_trait(occupation)
        self.is_human = True  # Starts as human
        self.is_dead = False  # Status of the player

    def get_block_at(self, x, y):
        """Retrieve the block at a given (x, y) location in the city."""
        # Check if coordinates are within the bounds of the city grid
        if 0 <= x < len(self.city) and 0 <= y < len(self.city[0]):
            return self.city[y][x]  # Return the block at the coordinates
        return None  # Return None if out of bounds

    def get_current_block(self):
        """Retrieve the block (object) at the current location."""
        x, y = self.location
        return self.get_block_at(x, y)

    def assign_starting_trait(self, occupation):
        """Assigns a starting trait based on the player's occupation."""
        traits = {
            "Doctor": "First Aid Training",
            "Soldier": "Firearms Training",
            "Engineer": "Construction Skills",
            "Athlete": "Body Building",
            "Teacher": "Educational Resources",
            "Scientist": "Experimental Knowledge",
            "Police Officer": "Combat Training",
        }
        return traits.get(occupation, "Survivor Instinct")

    def gain_skill(self, skill, is_human=True):
        """Adds a skill to the player's skill list depending on their state."""
        if is_human:
            self.skills_human.append(skill)
        else:
            self.skills_zombie.append(skill)

    def add_item(self, item):
        """Adds an item to the player's inventory."""
        self.inventory.append(item)

    def remove_item(self, item):
        """Removes an item from the player's inventory."""
        if item in self.inventory:
            self.inventory.remove(item)

    def list_inventory(self):
        """Returns a string representation of the inventory."""
        if not self.inventory:
            return "Inventory is empty."
        return ", ".join(item.name for item in self.inventory)

    def spend_action_point(self):
        """Spends one action point if available."""
        if self.action_points > 0:
            self.action_points -= 1
            return True
        return False

    def regenerate_action_points(self, amount=1):
        """Regenerates action points up to the maximum."""
        self.action_points = min(self.action_points + amount, self.max_action_points)

    def take_damage(self, amount):
        """Reduces the player's health by the given amount."""
        self.hp -= amount
        if self.hp <= 0:
            self.hp = 0
            self.die()

    def heal(self, amount):
        """Heals the player by the given amount up to max health."""
        self.hp = min(self.hp + amount, self.max_hp)

    def die(self):
        """Handles the player's death."""
        self.is_dead = True
        self.is_human = False  # Becomes a zombie if dead
        return "The player has died and slumped to the floor."

#    def revive(self):
#        """Revives the player, switching them back to human form."""
#        if self.is_dead:
#            self.is_human = True
#            self.is_dead = False
#            self.hp = self.max_hp
#            return "The player has been revived and is now human again."
#        return "The player is not dead and cannot be revived."

    def status(self):
        """Returns the player's current status."""
        status = {
            "Human Name": self.human_name,
            "Zombie Name": self.zombie_name,
            "Gender": self.gender,
            "Age": self.age,
            "Occupation": self.occupation,
            "Location": self.location,
            "HP": self.hp,
            "Max HP": self.max_hp,
            "Action Points": self.action_points,
            "Max Action Points": self.max_action_points,
            "State": "Human" if self.is_human else "Zombie",
            "Dead": self.is_dead,
        }
        return status

    def update_observations(self):
        """Update the observations list based on the player's current state."""
        current_block = self.get_current_block()
        current_block.observations.clear()  # Clear existing observations
        if self.inside:
            current_block.observations.append(f'You are standing in {current_block.block_desc}.')
            current_block.observations.append(current_block.block_inside_desc)
            for observation in current_block.inside_observations:
                current_block.observations.append(observation)
        else:
            if current_block.is_building:
                current_block.observations.append(f'You are standing outside {current_block.block_desc}. A sign reads "{current_block.block_name}".')
            else:
                current_block.observations.append(f'You are standing in {current_block.block_desc}.')
            current_block.observations.append(current_block.block_outside_desc)
            for observation in current_block.outside_observations:
                current_block.observations.append(observation)

    def description(self):
        """Return the current list of observations as a list."""
        current_block = self.get_current_block()
        self.update_observations()  # Ensure observations are current
        return current_block.observations

    # Start of player actions

    def use_item(self, item_name):
        """Uses an item from the inventory if available."""
        for item in self.inventory:
            if item.name == item_name:
                result = item.use()
                if item.consumable:
                    self.remove_item(item)
                return result
        return f"You don't have a {item_name}."

    def move(self, dx, dy):
        """Moves the player to a new location on the grid."""
        if self.spend_action_point():
            x, y = self.location
            new_x, new_y = x + dx, y + dy

            # Check if the new coordinates are valid within the grid
            if 0 <= new_x < 100 and 0 <= new_y < 100:
                # If a player moves, they are no longer inside.
                self.inside = False

                self.location = (new_x, new_y)
                return f"Player moved to {self.location}."
            return "Movement out of bounds."
        return "Not enough action points to move."

    def barricade(self):
        current_block = self.get_current_block()
        if current_block.can_barricade and self.inside:
            add_barricade = current_block.barricade.adjust_barricade(1)
            print(add_barricade)
            if not add_barricade:
                return "You can't add more barricades."
            return f"You managed to add to the barricade. The building is now {current_block.barricade.get_barricade_description()}."
        else:
            return "You can't barricade here."

    def where(self):
        current_block = self.get_current_block()
        return f"You are standing in front of {current_block.block_desc} called {current_block.block_name}."

    def enter(self):
        current_block = self.get_current_block()
        if current_block.is_building:
            if not self.inside:
                self.inside = True
                self.update_observations()
                return "You entered the building."
            return "You are already inside."
        return "This is not a building."

    def leave(self):
        current_block = self.get_current_block()
        if current_block.is_building:
            if self.inside:
                self.inside = False
                self.update_observations()
                return "You left the building."
            return "You are already outside."
        return "You can't leave this place."

    def search(self):
        current_block = self.get_current_block()
        if current_block.is_building:
            if self.inside:
                message = "You search the building. "
                if current_block.powered and current_block.lights_on:
                    multiplier = 1.5
                else:
                    multiplier = 1.0
            else:
                return "You need to be inside the building to search it."
        return "You search but can't find anything."