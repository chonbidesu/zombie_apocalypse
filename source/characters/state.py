# state.py

from dataclasses import dataclass
import random

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
    inside: bool
    living_humans: list
    living_zombies: list
    dead_bodies: list
    revivifying_bodies: list


class State:
    """Represents an NPC state."""
    def __init__(self, game, character):
        self.game = game
        self.character = character # Reference the parent character
        self.current_target = None
        self.next_action = None

    def get_action(self):
        """Determines next behaviour and stores the action."""
        self.next_action = self._determine_behaviour()

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

    def filter_characters_at_location(self, x, y, inside=False):
        """Retrieve all characters at a given location and categorize them."""
        player = self.game.state.player
        characters_here = [
            npc for npc in self.game.state.npcs.list
            if npc.location == (x, y) and npc.inside == inside
        ]

        # Add the player to the list if they are at location
        if player.location == (x, y) and player.inside == inside:
            characters_here.append(player)

        zombies_here = [character for character in characters_here if not character.is_human]
        humans_here = [character for character in characters_here if character.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [c for c in characters_here if c.is_dead]
        revivifying_bodies = [h for h in humans_here if h.is_dead]

        return BlockNPCs(x, y, inside, living_humans, living_zombies, dead_bodies, revivifying_bodies)                      
    
    def get_adjacent_locations(self):
        """Returns a list of (x, y) coordinates for the 8 adjacent blocks."""
        x, y = self.character.location
        adjacent_locations = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1), # Top row
            (x - 1, y),                 (x + 1, y),     # Middle row
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)  # Bottom row
        ]
        return adjacent_locations
    
    def _make_choice(self, actions):
        """Choose an action based on weighted probabilities."""
        valid_actions = [(action, weight) for action, weight in actions.items() if weight > 0]
        if not valid_actions:
            return None # No valid actions
        
        choices, weights = zip(*valid_actions)
        return random.choices(choices, weights=weights, k=1)[0] # Select an action    