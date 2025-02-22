# environment.py

import pygame
import random

from actions import ActionCommand
from data import Action, SkillType
from settings import *


class CloseDoors(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.CLOSE_DOORS

    def execute(self, executor, target):
        character = executor.character

        if not target.doors_closed:
            if executor.is_player:
                executor.action_progress.start("Closing doors", target.close_doors)
            else:
                target.close_doors()
            character.lose_ap(1)
            self.success = True
            self.message = "You close the doors of the building."
            self.sfx = 'door_close'


class OpenDoors(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.OPEN_DOORS

    def execute(self, executor, target):
        character = executor.character

        if target.doors_closed:
            if executor.is_player:
                executor.action_progress.start("Opening doors", target.open_doors)
            else:
                target.open_doors()
            character.lose_ap(1)
            self.success = True
            self.message = "You open the doors of the building."
            self.sfx = 'door_open'    


class AddBarricades(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.BARRICADE

    def execute(self, executor, target):
        character = executor.character
        x, y = character.location
        block_npcs = character.state.filter_characters_at_location(x, y, inside=True)

        success_chances = [1.0, 1.0, 1.0, 1.0, 0.8, 0.6, 0.4, 0.2]
        if len(block_npcs.living_zombies) > 1:
            modifier = 0.5
        else:
            modifier = 1
        
        if target.ransack_level > 0:
            self.message = "You have to repair the building before you can add barricades."
            return
        elif target.barricade.level >= 7 and target.barricade.sublevel >= 4:
            self.message = "You can't add more barricades."
            return
        
        success_chance = success_chances[target.barricade.level]
        success = random.random() < success_chance * modifier
        if success:
            
            if executor.is_player:
                executor.action_progress.start("Barricading", target.barricade.adjust_sublevel, 1)
            else:
                target.barricade.adjust_sublevel(1)
           
            if target.barricade.level == 4 and target.barricade.sublevel == 2:
                self.message = "You reinforce the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in."
                self.witness = f"{character.current_name} reinforced the barricade. It's looking very strong, now - any further barricading will prevent survivors from climbing in."
            
            elif self.barricade.sublevel == 0:
                barricade_description = target.barricade.get_barricade_description()
                self.message = f"You reinforce the barricade. The building is now {barricade_description}."   
                self.witness = f"{character.current_name} reinforced the barricade. The building is now {barricade_description}."
            
            elif self.barricade.sublevel > 0:
                self.message = "You reinforce the barricade."
                self.witness = f"{character.current_name} reinforced the barricade."

            character.lose_ap(1)
            self.success = True                
            self.sfx='barricade'
                   
        else:
            self.message = "You can't find anything to reinforce the barricade."
            
class Decade(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.DECADE

    def execute(self, executor, target):
        character = executor.character

        if target.barricade.level > 0:
            target.barricade.register_hit()
            character.lose_ap(1)

            if self.barricade.level == 0:
                self.message = "You smash at the barricades. The last piece of it falls away."
                self.witness = "Something smashes through the last of the barricades."

            else:
                self.message = "You smash at the barricades."
                self.witness = "Something smashes at the barricades."

            self.success = True
            self.sfx='decade'
              

class Ransack(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.RANSACK

    def execute(self, executor, target):
        character = executor.character

        if not target.ruined:
            target.ransack()

            if target.ransack_level == 6:
                target.ruin()
                self.message = "You ransack further rooms of the buildling. The building is now ruined."
            else:
                if target.ransack_level == 1:
                    self.message = "You ransack the building."
                else:
                    self.message = "You ransack further rooms of the building."
            self.success = True
            character.lose_ap(1)

        else:
            self.message = "This building is already ruined."


class InstallGenerator(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.USE

    def execute(self, executor, target):
        character = executor.character

        if character.inside:
            if target.generator_installed:
                self.message = "A generator is already installed."
            else:
                character.lose_ap(1)
                self.success = True
                self.message = "You install a generator. It needs fuel to operate."
            
        else:
            self.message = "Generators need to be installed inside buildings."


class FuelGenerator(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.USE

    def execute(self, executor, target):
        character = executor.character        

        if character.inside:

            if target.lights_on:
                self.message = "Generator already has fuel."
            elif not target.generator_installed:
                self.message = "You need to install a generator first."
            else:
                character.lose_ap(1)
                target.fuel_expiration = executor.game.ticker + FUEL_DURATION
                target.lights_on = True
                self.success = True
                self.message = "You fuel the generator. The lights are now on."

        else:
            self.message = "You have to be inside a building to use this."


class RepairBuilding(ActionCommand):
    def __init__(self):
        super().__init__()
        self.action = Action.USE

    def execute(self, executor, target):
        character = executor.character  

        if character.inside:

            if target.ransack_level == 0:
                self.message = "This building does not need repairs."

            if self.ruined:
                if not self.lights_on:
                    self.message =  "Ruined buildings need to be powered in order to be repaired."
                elif not SkillType.CONSTRUCTION in character.human_skills:
                    self.message =  "You need the Construction skill to repair ruins."
                else:
                    self.message = "You repair the damage to the building, clearing the rubble and cleaning up the mess."
                    character.lose_ap(1)
                    target.repair()        
                    self.success = True
            else:
                self.message = "You repaired the interior of the building and cleaned up the mess."
                character.lose_ap(1)
                target.repair()        
                self.success = True
        else:
            self.message = "You have to be inside a building to use this."



class Dump(ActionCommand):
    """Dump a body outside the building."""
    def __init__(self):
        super().__init__()
        self.action = Action.DUMP

    def execute(self, executor, target):
        character = executor.character
        x, y = character.location
        block_npcs = character.state.filter_characters_at_location(x, y, character.inside, include_player=True)

        if block_npcs.dead_bodies:
            dead_body = random.choice(block_npcs.dead_bodies)
            dead_body.inside = False
            character.lose_ap(1)
            self.message = "You dump a body outside."
            self.witness = f"{character.current_name} dumps a body outside."
            self.success = True


class EnvironmentHandler:

    @staticmethod
    def close_doors(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_close"])                
            executor.action_progress.start("Closing doors", executor.block.close_doors, executor.actor)
        else:
            return executor.block.close_doors(executor.actor)
            
    @staticmethod
    def open_doors(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_open"])                
            executor.action_progress.start("Opening doors", executor.block.open_doors, executor.actor)
        else:
            return executor.block.open_doors(executor.actor)

    @staticmethod
    def barricade(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["barricade"])                
            executor.action_progress.start("Barricading", executor.block.add_barricades, executor.actor)
        else:
            return executor.block.add_barricades(executor.actor)

    @staticmethod
    def search(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["search"])                
            executor.action_progress.start("Searching", executor.block.search, executor.actor)
        else:
            return executor.block.search(executor.actor)

    @staticmethod
    def repair_building(executor, target):
        if executor.is_player:
            executor.action_progress.start("Repairing", executor.block.repair_building, executor.actor)
        else:
            return executor.block.repair_building(executor.actor)

    @staticmethod
    def decade(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["decade"])                
            executor.action_progress.start("Smashing", executor.block.decade, executor.actor)
        else:
            return executor.block.decade(executor.actor)
        
    @staticmethod
    def ransack(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["decade"])                
            executor.action_progress.start("Ransacking", executor.block.ransack, executor.actor)
        else:
            return executor.block.ransack(executor.actor)        
        
    @staticmethod
    def dump(executor, target):
        if executor.is_player:
            pygame.mixer.Sound.play(executor.game.sounds["door_close"])                
            executor.action_progress.start("Dumping body", executor.block.dump, executor.actor)
        else:
            return executor.block.dump(executor.actor)