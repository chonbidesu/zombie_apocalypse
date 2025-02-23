# character.py

import random

from actions.base_command import ActionCommand
from data import BLOCKS, SkillType
from core.settings import *
             

class Use(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        self.success, self.message = target.item.use()


class Drop(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        self.success, self.message = target.drop()        


class Move(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target=None):
        city = self.character.game.state.city        
        x, y = self.character.location
        if target:
            dx, dy = target.dx, target.dy
        else: # If no target to move towards, wander
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)])
        new_x, new_y = dx + x, dy + y

        # Check if the new coordinates are valid within the grid
        if 0 <= new_x < CITY_SIZE and 0 <= new_y < CITY_SIZE:   
            new_block = city.block(new_x, new_y)
            block_properties = BLOCKS[new_block.type]

            if self.character.is_human:
                if block_properties.is_building:
                    if self.character.has_skill(SkillType.FREE_RUNNING):
                        if new_block.ruined:
                            self.character.inside = False
                            self.character.fall()                    
                    else:
                        self.character.inside = False                        
                else:
                    self.inside = False

                self.success = True
                self.character.lose_ap(1)

            else:
                self.character.inside = False
                if self.character.has_skill(SkillType.LURCHING_GAIT):
                    self.character.lose_ap(1)
                else:
                    self.character.lose_ap(2)
                self.success = True
        
        if self.success:
            self.character.move(new_x, new_y)


class Enter(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        building = self.get_block()

        if building.barricade.level == 0:
            if self.character.is_human:
                self.character.lose_ap(1)
                self.message = "You entered the building."
                self.witness = f"{self.character.current_name} entered the building."
                self.success = True
                self.sfx = 'footsteps'

            else:
                if building.doors_closed:
                    if self.character.has_skill(SkillType.MEMORIES_OF_LIFE):
                        building.open_doors()
                        self.character.lose_ap(1)
                        self.success = True
                        self.message = "You enter the building, leaving the doors wide open."
                        self.witness = f"{self.character.current_name} entered the building, leaving the doors wide open."
                        self.sfx = 'footsteps'
                    else:
                        self.message = "You need the MEMORIES OF LIFE skill in order to open doors."
                    
                else:
                    self.character.lose_ap(1)
                    self.message = "You enter the building."
                    self.witness = f"{self.character.current_name} entered the building."
                    self.success = True
                    self.sfx = 'footsteps'
                
        elif building.barricade.level > 0 and not self.character.is_human:
            self.message = "You have to break through the barricades first."

        elif building.barricade.level <= 4:
            self.character.lose_ap(1)
            self.message = "You climb through the barricades and are now inside."
            self.witness = f"{self.character.current_name} climbed through the barricades and is now inside."
            self.success = True
            self.sfx = 'footsteps'
        else:
            self.message = "You can't find a way through the barricades."

        if self.success:
            if self.is_player:
                screen_transition = self.character.game.game_ui.screen_transition
                screen_transition.circle_wipe(self.character.enter, self.character.game.chat_history)
            else:
                self.character.enter()


class Leave(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        building = self.get_block()

        if building.barricade.level == 0:
            if self.character.is_human:
                self.character.leave()
                self.character.lose_ap(1)
                self.message = "You left the building."
                self.witness = f"{self.character.current_name} left the building."
                self.success = True
                self.sfx = 'footsteps'
            else:
                if building.doors_closed:
                    if self.character.has_skill(SkillType.MEMORIES_OF_LIFE):
                        building.open_doors()
                        self.character.leave()
                        self.character.lose_ap(1)
                        self.message = "You left the building, leaving the doors wide open."
                        self.witness = f"{self.character.current_name} left the building, leaving the doors wide open."
                        self.success = True
                        self.sfx = 'footsteps'
                    else:
                        self.message = "You need the MEMORIES OF LIFE skill in order to open doors."                      
                else:
                    self.character.leave()
                    self.character.lose_ap(1)
                    self.message = "You left the building."
                    self.witness = f"{self.character.current_name} left the building."
                    self.success = True
                    self.sfx = 'footsteps'

        elif building.barricade.level > 0 and not self.character.is_human:
            self.message = "You have to break through the barricades first."

        elif building.barricade.level <= 4:
            self.character.lose_ap(1)
            self.message = "You climb through the barricades and are now outside."
            self.witness = f"{self.character.current_name} climbed through the barricades and is now outside."
            self.success = True
            self.sfx = 'footsteps'
        else:
            self.message = "The building has been so heavily barricaded that you cannot leave through the main doors."

        if self.success:
            if self.is_player:
                screen_transition = self.character.game.game_ui.screen_transition
                screen_transition.circle_wipe(self.character.leave, self.character.game.chat_history)
            else:
                self.character.leave()

       
class Stand(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self):
        """Character stands up at half health."""
        if not self.character.permadeath:
            self.success = True
            self.character.heal(self.character.max_hp // 2)
            if self.character.has_skill(SkillType.ANKLE_GRAB):
                self.character.lose_ap(1)
            else:
                self.character.lose_ap(STAND_AP)    

        if self.success:
            if self.is_player:
                action_progress = self.character.game.game_ui.action_progress
                action_progress.start("Standing", self.character.stand, duration=10000)
            else:
                self.character.stand()
        