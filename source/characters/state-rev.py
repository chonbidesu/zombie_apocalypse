# state.py

from data import BLOCKS, BlockNPCs, Action


class State:
    """Represents an NPC state."""
    def __init__(self, character):
        self.game = character.game
        self.character = character # Reference the parent character
        self.current_target = None
        self.next_decision = None
        self.selected_skill = None

    def get_decision(self):
        """Determines next behaviour and stores the action."""
        self.next_decision = self._determine_behaviour()

    def act(self):
        """Execute AI behaviour."""
        if self.next_decision:
            action_result = self.next_decision.execute(self.character)

            if action_result:
                action = action_result.action
                target = action_result.target
                witness = action_result.witness
                attacked = action_result.attacked
                player = self.game.state.player

                if attacked and target == player:
                    self.game.chat_history.append(attacked)
                elif witness and self.character.location == player.location:
                    if self.character.inside == player.inside:
                        self.game.chat_history.append(witness)                       
                    else:
                        if action == Action.DECADE:
                            self.game.chat_history.append(witness)                            

    def filter_characters_at_location(self, x, y, inside=False, include_player=True):
        """Retrieve all characters at a given location and categorize them."""
        player = self.game.state.player
        characters_here = [
            npc for npc in self.game.state.npcs.list
            if npc.location == (x, y) and npc.inside == inside
        ]

        if include_player:
            # Add the player to the list if they are at location
            if player.location == (x, y) and player.inside == inside:
                characters_here.append(player)

        zombies_here = [character for character in characters_here if not character.is_human]
        humans_here = [character for character in characters_here if character.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [c for c in characters_here if c.is_dead]
        dead_zombies = [z for z in zombies_here if z.is_dead]
        revivifying_bodies = [h for h in humans_here if h.is_dead]

        return BlockNPCs(x, y, inside, living_humans, living_zombies, dead_bodies, dead_zombies, revivifying_bodies)                      