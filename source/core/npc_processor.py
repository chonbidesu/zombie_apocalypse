# npc_processor.py

import time
from concurrent.futures import ThreadPoolExecutor
from collections import deque

from core.settings import *

class NPCProcessor:
    def __init__(self, game, actions_per_frame=100):
        self.state = game.state
        self.clock = game.clock
        self.actions_per_frame = actions_per_frame  # Number of actions processed per frame (for day)
        self.debug = game.debug
        self.action_timer = 0  # Timer to accumulate time until next action
        self.action_queue = deque()

    def process(self, time_of_day):
        """Process NPC actions based on the time of day."""
        if time_of_day == "day":
            self.process_day_cycle()
        elif time_of_day == "night":
            self.process_night_cycle()

    def process_day_cycle(self):
        """Processes NPC actions in real-time intervals during the day."""
        self.action_timer += self.clock.get_time()

        if self.action_timer >= ACTION_INTERVAL:
            # Load all NPCs into the queue
            self.action_queue = deque(self.state.npcs.list)
            self.action_timer = 0

        # Process actions for a limited number of NPCs in each frame (to avoid performance hits)
        for _ in range(min(self.actions_per_frame, len(self.action_queue))):
            npc = self.action_queue.popleft()
            if npc.ap > 0:
                self.process_npc_action(npc)
            npc.skill_manager.select_skill()
            npc.skill_manager.learn_skill()

    def process_night_cycle(self):
        """Processes all NPC actions as quickly as possible during the night."""
        # Load all NPCs into the queue and process as fast as possible
        self.action_queue = deque(npc for npc in self.state.npcs.list if npc.ap > 0)

        with ThreadPoolExecutor() as executor:
            last_ap_state = {npc: npc.ap for npc in self.state.npcs.list}

            while self.action_queue:
                batch = list(self.action_queue)[:10]
                executor.map(self.process_npc_action, batch)

                self.action_queue = deque(npc for npc in self.action_queue if npc.ap > 0)
            
                time.sleep(0.01)

                progress_made = any(npc.ap < last_ap_state[npc] for npc in self.state.npcs.list)
                last_ap_state = {npc: npc.ap for npc in self.state.npcs.list}   

                if not progress_made:
                    print("WARNING: Some NPCs are stuck with AP but unable to act.")
                    stuck_npcs = [npc for npc in self.state.npcs.list if npc.ap > 0]
                    for npc in stuck_npcs:
                        print(f"{npc.current_name} - AP: {npc.ap}")
                    break

    def process_npc_action(self, npc):
        """Helper method to process an NPC's action."""
        if npc.ap <= 0:
            return
        npc.goal_manager.evaluate_goal()
        if npc.goal_manager.current_goal:
            npc.goal_manager.current_goal.execute()
            current_goal = npc.goal_manager.current_goal
            if self.debug and current_goal and current_goal.last_known_target and current_goal.last_known_target[0] == self.state.player:
                print(f"{npc.current_name}: Goal - {type(current_goal)}")
                if current_goal.current_decision:
                    print(f"Decision - {type(current_goal.current_decision)}")
                    if current_goal.current_decision.action:
                        print(f"Action - {type(current_goal.current_decision.action)}")
