# test_ai.py

import logging
import pygame
import random
from core import GameInitializer
from core.settings import *
from data import BLOCKS, SkillType

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# Configure logging
logging.basicConfig(
    filename='test_ai.log',
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def run_ai_debug(rounds=500, npc_name=None, config=None):
    """Runs AI debugging for a specific NPC"""

    # Initialize game simulation
    game = GameInitializer(screen, clock)
    game.initialize_simulation()

    if config:
        apply_config(game, config)

    # Select an NPC to debug
    debug_npc = None
    if npc_name:
        debug_npc = next((npc for npc in game.state.npcs.list if npc.current_name == npc_name), None)
    else:
        if config and "npc_is_human" in config:
            debug_npc = random.choice([npc for npc in game.state.npcs.list if npc.is_human])
        else:
            debug_npc = random.choice([npc for npc in game.state.npcs.list if not npc.is_human])

    if not debug_npc:
        print("No NPC found for debugging.")
        return

    logging.info(f"Starting AI debug simulation for {debug_npc.current_name}")

    for round_number in range(1, rounds + 1):
        game.ticker += 1
        debug_npc.ap += 1

        if debug_npc.ap > 0:
            goal = debug_npc.goal_manager.evaluate_goal()
            if goal:
                goal.execute()

            decision = goal.current_decision if goal else None
            action = decision.action if decision else None

            logging.debug(f"[Round {round_number}]")
            logging.debug(f"NPC: {debug_npc.current_name} at ({debug_npc.location})")
            logging.debug(f"Goal: {goal.__class__.__name__ if goal else 'None'}")
            logging.debug(f"Decision: {decision.__class__.__name__ if decision else 'None'}")
            logging.debug(f"Action: {action.__class__.__name__ if action else 'None'}")
            logging.debug("-" * 40)       

    logging.info("AI debug simulation completed.")
    print("AI simulation finished. Check 'ai_debug.log' for details.")

def apply_config(game, config):
    """Apply configuration settings to modify the game state."""
    city = game.state.city

    for row in city.grid:
        for block in row:
            properties = BLOCKS[block.type]

            if properties.is_building:
                # Turn on all building lights
                if config.get("lights_on", False):
                    block.lights_on = True
                
                # Close all doors
                if config.get("close_doors", False):
                    block.doors_closed = True

                # Set barricade levels
                if "barricade_level" in config:
                    block.barricade.level = config["barricade_level"]

    # Apply NPC configurations
    for npc in game.state.npcs.list:
        if "npc_skills" in config:
            npc.skill_manager.acquire_skills(config["npc_skills"])
        if "npc_ap" in config:
            npc.ap = config["npc_ap"]

if __name__ == "__main__":
    config = {
        "lights_on": True,           # Turns on all building lights
        "close_doors": True,         # Closes all doors
        "barricade_level": 7,        # Sets barricade levels to 3
        "npc_skills": [SkillType.MEMORIES_OF_LIFE, SkillType.LURCHING_GAIT],  # Gives zombies specific skills
        "npc_ap": 10,                 # Gives NPCs 10 AP to start
    }

    run_ai_debug(rounds=100, config=config)