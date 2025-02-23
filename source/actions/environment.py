# environment.py

import random
import csv
from collections import defaultdict

from actions.base_command import ActionCommand
from data import ItemType
from settings import *


class CloseDoors(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        block = self.get_block()

        if not block.doors_closed:
            if self.is_player:
                action_progress = self.character.game.game_ui.action_progress
                action_progress.start("Closing doors", block.close_doors)
            else:
                block.close_doors()
            self.character.lose_ap(1)
            self.success = True
            self.message = "You close the doors of the building."
            self.sfx = 'door_close'


class OpenDoors(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        block = self.get_block()       

        if block.doors_closed:
            if self.is_player:
                action_progress = self.character.game.game_ui.action_progress
                action_progress.start("Opening doors", block.open_doors)
            else:
                block.open_doors()
            self.character.lose_ap(1)
            self.success = True
            self.message = "You open the doors of the building."
            self.sfx = 'door_open'    


class AddBarricades(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        block = self.get_block()
        block_npcs = self.get_block_npcs()

        success_chances = [1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2]
        if len(block_npcs.living_zombies) > 1:
            modifier = 0.5
        else:
            modifier = 1
        
        if block.ransack_level > 0:
            self.message = "You have to repair the building before you can add barricades."
            return
        elif block.barricade.level >= 7 and block.barricade.sublevel >= 4:
            self.message = "You can't add more barricades."
            return
        
        success_chance = success_chances[block.barricade.level]
        success = random.random() < success_chance * modifier
        if success:
            
            if self.is_player:
                action_progress = self.character.game.game_ui.action_progress
                action_progress.start("Barricading", block.barricade.adjust_sublevel, 1)
            else:
                block.barricade.adjust_sublevel(1)
           
            if block.barricade.level == 4 and block.barricade.sublevel == 2:
                self.message = "You reinforce the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in."
                self.witness = f"{self.character.current_name} reinforced the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in."
            
            elif self.barricade.sublevel == 0:
                barricade_description = block.barricade.get_barricade_description()
                self.message = f"You reinforce the barricade. The building is now {barricade_description}."   
                self.witness = f"{self.character.current_name} reinforced the barricade. The building is now {barricade_description}."
            
            elif self.barricade.sublevel > 0:
                self.message = "You reinforce the barricade."
                self.witness = f"{self.character.current_name} reinforced the barricade."

            self.character.lose_ap(1)
            self.success = True                
            self.sfx='barricade'
                   
        else:
            self.message = "You can't find anything to reinforce the barricade."
            

class Decade(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        block = self.get_block()

        if block.barricade.level > 0:
            block.barricade.register_hit()
            self.character.lose_ap(1)

            if self.barricade.level == 0:
                self.message = "You smash at the barricades. The last piece of it falls away."
                self.witness = "Something smashes through the last of the barricades."

            else:
                self.message = "You smash at the barricades."
                self.witness = "Something smashes at the barricades."

            self.success = True
            self.sfx='decade'
              

class Ransack(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        block = self.get_block()

        if not block.ruined:
            block.ransack()

            if block.ransack_level == 6:
                block.ruin()
                self.message = "You ransack further rooms of the buildling. The building is now ruined."
            else:
                if block.ransack_level == 1:
                    self.message = "You ransack the building."
                else:
                    self.message = "You ransack further rooms of the building."
            self.success = True
            self.character.lose_ap(1)

        else:
            self.message = "This building is already ruined."


class Dump(ActionCommand):
    """Dump a body outside the building."""
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        block_npcs = self.get_block_npcs()

        if block_npcs.dead_bodies:
            dead_body = random.choice(block_npcs.dead_bodies)
            dead_body.inside = False
            self.character.lose_ap(1)
            self.message = "You dump a body outside."
            self.witness = f"{self.character.current_name} dumps a body outside."
            self.success = True


class Search(ActionCommand):
    """Search inside a building for useful items."""
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        """Search a building for items."""
        block = self.get_block()

        search_path = DataPath('tables/search.csv').path
        search_chances = self._load_search_chances(search_path)
        items_held = len(self.character.inventory)
  
        # Determine search success chance
        if block.ruined:
            search_chance = 0.10 # 10% base chance if building ruined
        else:
            base_chance = 0.20 + (0.05 if block.lights_on else 0.00) # 20% unlit, 25% lit
            search_chance = max(0, base_chance - (block.ransack_level * 0.01)) # Subtract ransack penalty

        # Roll for success
        if random.random() >= search_chance:
            self.character.lose_ap(1)
            return False, "You didn't find anything."

        # If successful, determine the found item
        items = list(search_chances)
        weights = [search_chances[item].get(self.type.name, 0.0) for item in items]

        if not any(weights):
            self.character.lose_ap(1)
            return False, "You didn't find anything."
        
        item_type = random.choices(items, weights=weights, k=1)[0]
        item = self.character.create_item(item_type)

        # Check inventory capacity
        if items_held >= MAX_ITEMS:
            self.character.lose_ap(1)
            return False, f"You found {item.description}, but you are carrying too much!"

        # Check for duplicate portable generator
        if item.type == ItemType.PORTABLE_GENERATOR:
            for inventory_item in self.character.inventory:
                if hasattr(inventory_item, 'type') and inventory_item.type == ItemType.PORTABLE_GENERATOR:
                    self.character.lose_ap(1)
                    return False, "You found a portable generator, but you can only carry one at a time."
 
        # Add the item to inventory
        self.character.inventory.append(item)
        self.character.lose_ap(1)
        return True, f"You found {item.description}!"


    def _load_search_chances(self, file_path):
        """Load search chances from a CSV file."""
        search_chances = defaultdict(dict)
        with open(file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                item = row['Item']
                for building_type, chance in row.items():
                    if building_type != 'Item':  # Skip the 'Item' column
                        search_chances[item][building_type] = float(chance)
        return search_chances