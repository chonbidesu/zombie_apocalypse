# character.py

import random
from dataclasses import dataclass

from actions.base_command import ActionCommand
from data import BLOCKS, SkillType, ItemType
from core.settings import *
from items import Weapon, ItemFunction
             

@dataclass
class MoveTarget:
    dx: int = 0
    dy: int = 0


class Use(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        self.success, self.message = target.item.use()
        
        if self.success and self.is_player and \
            not (issubclass(type(target.item), Weapon) or \
                 target.item.type == ItemType.FIRST_AID_KIT or \
                    target.item.item_function == ItemFunction.SCIENCE):
            self.character.game.tick()

class Drop(ActionCommand):
    def __init__(self, character):
        super().__init__(character)

    def execute(self, target):
        self.success, self.message = target.item.drop()        


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
                    if self.character.helper.has_skill(SkillType.FREE_RUNNING):
                        if new_block.ruined:
                            self.character.inside = False
                            self.character.fall()                    
                    else:
                        self.character.inside = False                        
                else:
                    self.character.inside = False

                self.success = True
                self.character.lose_ap(1)

            else:
                self.character.inside = False
                if self.character.helper.has_skill(SkillType.LURCHING_GAIT):
                    self.character.lose_ap(1)
                else:
                    self.character.lose_ap(2)
                self.success = True
        
        if self.success:
            if self.is_player:
                game = self.character.game
                if self.character.is_human:
                    ap_cost = 1
                else:
                    if self.character.helper.has_skill(SkillType.LURCHING_GAIT):
                        ap_cost = 1
                    else:
                        ap_cost = 2
                game.tick(ap_cost)
                screen_transition = game.game_ui.screen_transition
                screen_transition.dissolve_scene(self.character.move, game.chat_history, new_x, new_y)                
            else:
                self.character.move(new_x, new_y)

            # Resolve line of sight for nearby zombies
            if self.character.is_human:
                watching_zombies = self.character.goal_manager.find_watching_zombies()
                if watching_zombies:
                    last_known_target = (self.character, self.character.location)                    
                    for zombie in watching_zombies:
                        if zombie.goal_manager.current_goal:
                            zombie.goal_manager.current_goal.last_known_target = last_known_target

            else:
                current_goal = self.character.goal_manager.current_goal
                if current_goal and current_goal.last_known_target:
                    return


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
                    if self.character.helper.has_skill(SkillType.MEMORIES_OF_LIFE):
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
                self.character.game.tick()
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
                    if self.character.helper.has_skill(SkillType.MEMORIES_OF_LIFE):
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
                self.character.game.tick()                
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
            self.message = "You stand up, feeling weak."
            self.witness = f"{self.character.current_name} stands up!"
            self.character.heal(self.character.max_hp // 2)
            if self.character.helper.has_skill(SkillType.ANKLE_GRAB):
                self.character.lose_ap(1)
            else:
                self.character.lose_ap(STAND_AP)    

        if self.success:
            if self.is_player:
                stand_ap = 1 if self.character.helper.has_skill(SkillType.ANKLE_GRAB) else STAND_AP
                self.character.game.tick(stand_ap)                
                action_progress = self.character.game.game_ui.action_progress
                action_progress.start("Standing", self.character.stand, duration=10000)
            else:
                self.character.stand()
        