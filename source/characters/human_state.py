# human_state.py

from dataclasses import dataclass

from settings import *
from data import Action, BLOCKS, Occupation, ItemType, MILITARY_OCCUPATIONS, SCIENCE_OCCUPATIONS, CIVILIAN_OCCUPATIONS


@dataclass
class Result:
    action: Action
    target: object = None


class Human:
    """Represents the human state."""
    def __init__(self, game, character):
        self.game = game
        self.character = character # Reference the parent character

    def act(self):
        """Execute AI behaviour."""
        # Only act if action points are available
        if self.character.ap < 1:
            return False
        
        # Get block object at current location
        block = self.game.city.block(self.character.location[0], self.character.location[1])

        # Determine behaviour
        result = self._determine_behaviour(block)

        # Execute action
        if result:
            self.character.action.execute(result.action, result.target)

    def _determine_behaviour(self, block):
        """Determine the priority for the NPC."""
        properties = BLOCKS[block.type]
        occupation = self.character.occupation
        inventory = self.character.inventory
        living_zombies, living_humans, dead_bodies = self._filter_npcs_at_npc_location()

        # Stand up if dead and have enough action points
        if self.character.is_dead:
            return Result(Action.STAND) if self.character.ap >= STAND_AP else False

        # Relocate if the block is overcrowded
        if len(living_zombies + living_humans) > BLOCK_CAPACITY:
            return Result(Action.RELOCATE)
        
        elif occupation == Occupation.CONSUMER:
            if len(living_zombies) > 0:
                return Result(Action.FIND_TARGET) # Flee to another building
            elif self.character.location == self.game.player.location and self.character.inside == self.game.player.inside:
                return Result(Action.GIVE_QUEST)
            elif not self.character.inside and properties.is_building:
                return Result(Action.ENTER)
            elif not self.character.inside and not properties.is_building:
                return Result(Action.WANDER)
            
        elif occupation in CIVILIAN_OCCUPATIONS:
            if properties.is_building and not self.character.inside:
                return Result(Action.ENTER)
            elif self.character.inside:
                if living_zombies:
                    return Result(Action.ATTACK, living_zombies[0])
                elif block.ransack_level > 0:
                    for item in inventory:
                        if item.type == ItemType.TOOLBOX:
                            return Result(Action.USE, item)
                elif block.barricade.level <= 4:
                    return Result(Action.BARRICADE)
                else:
                    return Result(Action.SEARCH)
        
        elif occupation in SCIENCE_OCCUPATIONS:
            if properties.is_building and not self.character.inside:
                return Result(Action.ENTER)
            elif self.character.inside:
                if living_zombies:
                    return Result(Action.ATTACK, living_zombies[0])
                elif block.ransack_level > 0:
                    for item in inventory:
                        if item.type == ItemType.TOOLBOX:
                            return Result(Action.USE, item)
                elif block.barricade.level <= 4:
                    return Result(Action.BARRICADE)
                else:
                    return Result(Action.SEARCH)
                
        elif occupation in MILITARY_OCCUPATIONS:
            if living_zombies:
                return Result(Action.ATTACK, living_zombies[0])
            else:
                return Result(Action.WANDER)

        return None # No behaviour determined
    
    def _filter_npcs_at_npc_location(self):
        """Retrieve other NPCs currently at the NPC's location and categorize them."""
        npcs_here = [
            npc for npc in self.game.npcs.list
            if npc.location == self.character.location and npc.inside == self.character.inside
        ]

        zombies_here = [npc for npc in npcs_here if not npc.is_human]
        humans_here = [npc for npc in npcs_here if npc.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [npc for npc in npcs_here if npc.is_dead]

        return living_zombies, living_humans, dead_bodies    