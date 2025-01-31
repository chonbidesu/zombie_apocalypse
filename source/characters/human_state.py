# human_state.py

from settings import *
from data import Action, BLOCKS

class Human:
    """Represents the human state."""
    def __init__(self, game, character):
        self.character = character # Reference the parent character

    def act(self, action_points):
        """Execute AI behaviour."""
        # Only act if action points are available
        if action_points < 1:
            return False
        
        # Get block object at current location
        current_block = self.game.city.block(self.character.location[0], self.character.location[1])

        # Determine behaviour
        action, target = self.determine_behaviour(current_block)

        # Call action function
        if action == Action.RELOCATE:
            self.actions.relocate(current_block)

        elif action == Action.ATTACK:
            self.actions.attack(target)
        
        elif action == Action.FIND_TARGET:
            self.actions.find_target()
        
        elif action == Action.PURSUE:
            self.actions.pursue(target, current_block)

        elif action == Action.BARRICADE:
            self.actions.barricade(current_block)

        elif action == Action.MOVE:
            target_dx, target_dy = self.actions.find_target_dxy(target)
            if target_dx is not None and self.action_points >= 1:
                self.actions.move(target_dx, target_dy)

        elif action == Action.ENTER:
            self.actions.enter()
        
        elif action == Action.WANDER:
            self.actions.wander()

        elif action == Action.STAND:
            self.actions.stand()

    def determine_human_behaviour(self, current_block):
        """Determine the priority for the NPC."""
        properties = BLOCKS[current_block.type]
        # Stand up if dead and have enough action points
        if self.is_dead:
            return Action.STAND if self.action_points >= STAND_AP else False

        # Relocate if the block is overcrowded
        if current_block.current_humans > HUMAN_CAPACITY:
            return Action.RELOCATE
        
        elif self.type == NPCType.SURVIVOR:
            if current_block.current_zombies > 0:
                return Action.FIND_TARGET # Flee to another building
            elif self.location == self.game.player.location and self.inside == self.game.player.inside:
                return Action.GIVE_QUEST
            elif not self.inside and properties.is_building:
                    return Action.ENTER_BUILDING
            
        elif self.type == NPCType.PREPPER:
            if properties.is_building and not self.inside:
                return Action.ENTER_BUILDING
            elif self.inside:
                for zombie in self.game.zombies.list:
                    if self.location == zombie.location and zombie.inside:
                        return Action.ATTACK_NPC
                if current_block.is_ransacked:
                    return Action.REPAIR_BUILDING
                elif current_block.barricade.level <= 4:
                    return Action.HANDLE_BARRICADE
                else:
                    return Action.FIND_TARGET
        
        elif self.type == NPCType.SCIENTIST:
            if current_block.current_zombies > 0:
                return Action.ATTACK_NPC
            else:
                return Action.FIND_TARGET
            
        return None  # No behaviour determined