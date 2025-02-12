# state.py

from dataclasses import dataclass

from data import Action


@dataclass
class MoveTarget:
    dx: int = 0
    dy: int = 0


@dataclass
class Result:
    action: Action
    target: object = None


@dataclass
class BlockNPCs:
    x: int
    y: int
    living_humans: list
    living_zombies: list
    dead_bodies: list


class State:
    """Represents an NPC state."""
    def __init__(self, game, character):
        self.game = game
        self.character = character # Reference the parent character
        self.current_target = None
        self.next_action = None

    def get_action(self):
        """Determines next behaviour and stores the action."""
        # Get block object at current location
        city = self.game.state.city
        block = city.block(self.character.location[0], self.character.location[1])

        # Get the next action and store it
        self.next_action = self._determine_behaviour(block)

    def act(self):
        """Execute AI behaviour."""
        # Only act if action points are available
        if self.character.ap < 1:
            return False
        
        # Execute action if one was determined
        if self.next_action:
            action_result = self.character.action.execute(self.next_action.action, self.next_action.target)
            if action_result:
                if action_result.attacked and self.next_action.target == self.game.state.player:
                    self.game.chat_history.append(action_result.attacked)
                elif action_result.witness and self.character.location == self.game.state.player.location and self.character.inside == self.game.state.player.inside:
                    self.game.chat_history.append(action_result.witness)
                

    def _filter_npcs_at_npc_location(self):
        """Retrieve other NPCs (including the player) currently at the NPC's location and categorize them."""
        player = self.game.state.player
        npcs_here = [
            npc for npc in self.game.state.npcs.list
            if npc.location == self.character.location and npc.inside == self.character.inside
        ]

        zombies_here = [npc for npc in npcs_here if not npc.is_human]
        humans_here = [npc for npc in npcs_here if npc.is_human]

        if player.location == self.character.location and player.inside == self.character.inside:
            if player.is_human:
                humans_here.append(player)
            else:
                zombies_here.append(player)

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [npc for npc in npcs_here if npc.is_dead]

        return BlockNPCs(living_humans, living_zombies, dead_bodies)             