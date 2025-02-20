# blocks.py

import random
from collections import defaultdict
import csv

from settings import *
from data import BLOCKS, BarricadeState, BARRICADE_DESCRIPTIONS, ActionResult, ITEMS, ItemType, SkillType

class CityBlock:
    """Base class for a city block."""
    def __init__(self):
        self.name = 'City Block'
        self.type = None
        self.x, self.y = 0, 0
        self.block_outside_desc = 'A non-descript city block.'
        self.observations = []
        self.neighbourhood = ''
        self.current_zombies = 0 # Number of zombies currently in the block
        self.current_humans = 0
        self.is_known = False # Has the player seen the block

    def generate_descriptions(self, descriptions_data):
        """Randomly construct three-sentence descriptions of city blocks."""
        if self.type.name in descriptions_data:
            data = descriptions_data[self.type.name]
            
            # Randomly assemble outside descriptions
            outside = data.get("outside", defaultdict(list))
                       
            self.block_outside_desc = " ".join([
                random.choice(outside["first"]) if outside["first"] else "",
                random.choice(outside["second"]) if outside["second"] else "",
                random.choice(outside["third"]) if outside["third"] else ""
            ])
        else:
            # Default descriptions if block type is not found
            self.block_outside_desc = "This place shows signs of decay and neglect."

class BuildingBlock(CityBlock):
    """A block with a building that can be barricaded and searched."""
    def __init__(self):
        super().__init__()
        self.barricade = self.BarricadeLevel()
        self.fuel_expiration = 0
        self.block_inside_desc = 'The inside of a building.'
        self.doors_closed = False
        self.ransack_level = 0
        self.ruined = False
        self.lights_on = False
        self.generator_installed = False

    def generate_descriptions(self, descriptions_data):
        """Randomly construct three-sentence descriptions of building blocks."""
        if self.type.name in descriptions_data:
            data = descriptions_data[self.type.name]
            
            # Randomly assemble inside and outside descriptions
            inside = data.get("inside", defaultdict(list))
            outside = data.get("outside", defaultdict(list))
            
            self.block_inside_desc = " ".join([
                random.choice(inside["first"]) if inside["first"] else "",
                random.choice(inside["second"]) if inside["second"] else "",
                random.choice(inside["third"]) if inside["third"] else ""
            ])
            
            self.block_outside_desc = " ".join([
                random.choice(outside["first"]) if outside["first"] else "",
                random.choice(outside["second"]) if outside["second"] else "",
                random.choice(outside["third"]) if outside["third"] else ""
            ])
        else:
            # Default descriptions if block type is not found
            self.block_inside_desc = "Inside, this place looks abandoned and forgotten."
            self.block_outside_desc = "Outside, the building shows signs of decay and neglect."

    def close_doors(self, actor):
        self.doors_closed = True
        actor.ap -= 1
        return ActionResult(True, "You close the doors of the building.", sfx='door_close')
    
    def open_doors(self, actor):
        self.doors_closed = False
        actor.ap -= 1
        return ActionResult(True, "You open the doors of the building.", sfx='door_open')

    def add_barricades(self, actor):
        block_npcs = actor.state.filter_characters_at_location(self.x, self.y, inside=True)

        success_chances = [1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2]
        if len(block_npcs.living_zombies) > 1:
            modifier = 0.5
        else:
            modifier = 1
        
        if actor.inside:
            if self.ransack_level > 0:
                return ActionResult(False, "You have to repair the building before you can add barricades.")
            elif self.barricade.level >= 7 and self.barricade.sublevel >= 4:
                return ActionResult(False, "You can't add more barricades.")
            
            success_chance = success_chances[self.barricade.level]
            success = random.random() < success_chance * modifier
            if success:
                add_barricade = self.barricade.adjust_barricade_sublevel(1)
                if not add_barricade:
                    return ActionResult(False, "You can't add more barricades.")
                elif self.barricade.level == 4 and self.barricade.sublevel == 2:
                    actor.ap -= 1
                    message = "You reinforce the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in."
                    witness = f"{actor.current_name} reinforced the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in."
                    return ActionResult(True, message, witness, sfx='barricade')
                elif self.barricade.sublevel == 0:
                    barricade_description = self.barricade.get_barricade_description()
                    actor.ap -= 1         
                    message = f"You reinforce the barricade. The building is now {barricade_description}."   
                    witness = f"{actor.current_name} reinforced the barricade. The building is now {barricade_description}."
                    return ActionResult(True, message, witness, sfx='barricade')
                elif self.barricade.sublevel > 0:
                    actor.ap -= 1
                    message = "You reinforce the barricade."
                    witness = f"{actor.current_name} reinforced the barricade."
                    return ActionResult(True, message, witness, sfx='barricade')
            else:
                return ActionResult(False, "You can't find anything to reinforce the barricade.")
        else:
            return ActionResult(False, "You have to be inside a building to barricade.")

    def decade(self, actor):
        if self.barricade.level > 0:
            self.barricade.register_hit()
            actor.ap -= 1
            if self.barricade.level == 0:
                message = "You smash at the barricades. The last piece of it falls away."
                witness = "Something smashes through the last of the barricades."
            else:
                message = "You smash at the barricades."
                witness = "Something smashes at the barricades."
            return ActionResult(True, message, witness, sfx='decade')
        else:
            return ActionResult(False, "There are no barricades to break.")                

    def ransack(self, actor):
        if actor.inside:
            if not self.ruined:
                self.ransack_level += 1
                if self.ransack_level == 6:
                    self.ruined = True
                    return ActionResult(True, "You ransack further rooms of the buildling. The building is now ruined.")
                else:
                    if self.ransack_level == 1:
                        return ActionResult(True, "You ransack the building.")
                    else:
                        return ActionResult(True, "You ransack further rooms of the building.")
            else:
                return ActionResult(False, "This building is already ruined.")
        else:
            return ActionResult(False, "You have to be inside to ransack.")

    def search(self, actor):
        """Search a building for items."""
        search_path = DataPath('tables/search.csv').path
        search_chances = self._load_search_chances(search_path)
        items_held = len(actor.inventory)
  
        # Determine search success chance
        if self.ruined:
            search_chance = 0.10 # 10% base chance if building ruined
        else:
            base_chance = 0.20 + (0.05 if self.lights_on else 0.00) # 20% unlit, 25% lit
            search_chance = max(0, base_chance - (self.ransack_level * 0.01)) # Subtract ransack penalty

        # Roll for success
        if random.random() >= search_chance:
            actor.ap -= 1
            return ActionResult(False, "You didn't find anything.")

        # If successful, determine the found item
        items = list(search_chances)
        weights = [search_chances[item].get(self.type.name, 0.0) for item in items]

        if not any(weights):
            actor.ap -= 1
            return ActionResult(False, "You didn't find anything.")
        
        item_type = random.choices(items, weights=weights, k=1)[0]
        item = actor.create_item(item_type)
        item_properties = ITEMS[item.type]

        # Check inventory capacity
        if items_held >= MAX_ITEMS:
            actor.ap -= 1
            return ActionResult(False, f"You found {item_properties.description}, but you are carrying too much!")

        # Check for duplicate portable generator
        if item.type == ItemType.PORTABLE_GENERATOR:
            for inventory_item in actor.inventory:
                if hasattr(inventory_item, 'type') and inventory_item.type == ItemType.PORTABLE_GENERATOR:
                    actor.ap -= 1
                    return ActionResult(False, "You found a portable generator, but you can only carry one at a time.")
 
        # Add the item to inventory
        actor.inventory.append(item)
        actor.ap -= 1
        return ActionResult(True, f"You found {item_properties.description}!")


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

    def install_generator(self, actor, item):
        if not actor.inside:
            return ActionResult(False, "Generators need to be installed inside buildings.")

        if self.generator_installed:
            return ActionResult(False, "A generator is already installed.")
        else:
            actor.ap -= 1
            actor.inventory.remove(item)            
            return ActionResult(True, "You install a generator. It needs fuel to operate.")
        
    def fuel_generator(self, actor, item):
        if not actor.inside:
            return ActionResult(False, "You have to be inside a building to use this.")

        if self.lights_on:
            return ActionResult(False, "Generator already has fuel.")
        elif not self.generator_installed:
            return ActionResult(False, "You need to install a generator first.")
        else:
            actor.ap -= 1
            self.fuel_expiration = actor.game.ticker + FUEL_DURATION
            self.lights_on = True
            actor.inventory.remove(item)            
            return ActionResult(True, "You fuel the generator. The lights are now on.")
        
    def repair_building(self, actor, item):
        if not actor.inside:
            return ActionResult(False, "You have to be inside a building to use this.")

        if self.ransack_level == 0:
            return ActionResult(False, "This building does not need repairs.")

        if self.ruined:
            if not self.lights_on:
                return ActionResult(False, "Ruined buildings need to be powered in order to be repaired.")
            elif not SkillType.CONSTRUCTION in actor.human_skills:
                return ActionResult(False, "You need the Construction skill to repair ruins.")
            else:
                message = "You repair the damage to the building, clearing the rubble and cleaning up the mess."
        else:
            message = "You repaired the interior of the building and cleaned up the mess."
        actor.ap -= 1
        self.ransack_level = 0
        self.ruined = False        
        return ActionResult(True, message)

    def dump(self, actor):
        """Dump a body outside the building."""
        block_npcs = actor.state.filter_characters_at_location(self.x, self.y, actor.inside, include_player=True)

        if block_npcs.dead_bodies:
            dead_body = random.choice(block_npcs.dead_bodies)
            dead_body.inside = False
            actor.ap -= 1
            message = "You dump a body outside."
            witness = f"{actor.current_name} dumps a body outside."
            return ActionResult(True, message, witness)


    class BarricadeLevel:
        """Model barricade levels for buildings"""
        def __init__(self, level=0):
            # Set default barricade level (0 by default, i.e., no barricade)
            self.level = level
            self.set_barricade_level(level)
            self.sublevel = 0
            self.successful_hits = 0

        def set_barricade_level(self, level):
            """
            Sets the barricade level. 
            If the level is out of bounds (less than 0 or greater than 7), it will be capped at 0 or 7.
            """
            self.level = max(0, min(level, 7))  # Keep the level within the bounds
            self.description = self.get_barricade_description()

        def adjust_barricade_level(self, delta):
            """
            Adjust the barricade level by adding or subtracting `delta`.
            """
            new_level = self.level + delta
            self.set_barricade_level(new_level)

        def adjust_barricade_sublevel(self, delta):
            """
            Adjust the barricade sublevel by adding or subtracting `delta`.
            Levels 0-1 have 1 sublevel. Levels 2-6 have 3 sublevels. Level 7 has 5 sublevels.
            """
            new_sublevel = self.sublevel + delta

            if self.level <= 1 and new_sublevel > 0:
                self.adjust_barricade_level(1)
                self.successful_hits = 0
                return True
            
            elif self.level <= 2 and new_sublevel < 0:
                self.adjust_barricade_level(-1)
                self.successful_hits = 0
                return True

            elif 3 <= self.level <= 7 and new_sublevel < 0:
                self.adjust_barricade_level(-1)
                self.sublevel = 2
                self.successful_hits = 0
                return True

            elif 2 <= self.level < 7 and new_sublevel < 3:
                self.sublevel = new_sublevel
                self.successful_hits = 0
                return True

            elif 2 <= self.level < 7 and new_sublevel >= 3:
                self.adjust_barricade_level(1)
                self.sublevel = 0
                self.successful_hits = 0
                return True

            elif self.level == 7 and 0 <= new_sublevel < 5:
                self.sublevel = new_sublevel
                self.successful_hits = 0
                return True

            else:
                return False     

        def register_hit(self):
            """Register a successful hit on the barricade."""
            self.successful_hits += 1
            if self.successful_hits == 3:
                self.adjust_barricade_sublevel(-1)
                self.successful_hits = 0

        def get_barricade_description(self):
            """
            Returns the current description of the barricade.
            """
            barricade_state = list(BarricadeState)[self.level]
            return BARRICADE_DESCRIPTIONS[barricade_state]
        
        def can_pass(self, actor):
            """Returns true if the actor can pass the barricade."""
            if actor.is_human and self.level <= 4:
                return True
            elif not actor.is_human and self.level == 0:
                return True
            else:
                return False