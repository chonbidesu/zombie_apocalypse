# simulate.py


import logging
import pygame

from main import GameInitializer  # Import the game setup
from settings import *

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Configure logging
logging.basicConfig(filename="balance_test.log", level=logging.INFO, format="%(message)s")

def run_simulation(rounds=500):
    """Runs the AI balance test without opening the game window."""
    
    # Initialize game (without rendering)
    game = GameInitializer(screen)
    game.initialize_game()
    
    # If you want to load a save file, do this:
    # game_state = Gamestate.load_game("savegame.pkl")
    # game_state.reconstruct_game(game, Character, City, GenerateNPCs, BuildingBlock, CityBlock)

    logging.info("Starting AI balance test...")
    logging.info("Round, Living Humans, Living Zombies, Dead Bodies")

    for round_number in range(1, rounds + 1):
        game.ticker += 1  # Advance game time

        # NPCs gain action points and act
        for npc in game.state.npcs.list:
            npc.ap += 1  # Gain 1 AP per round
            if npc.ap >= 1:
                npc.state.act()

        # Count populations
        living_humans = sum(1 for npc in game.state.npcs.list if npc.is_human and not npc.is_dead)
        living_zombies = sum(1 for npc in game.state.npcs.list if not npc.is_human and not npc.is_dead)
        dead_bodies = sum(1 for npc in game.state.npcs.list if npc.is_dead)

        # Log results
        logging.info(f"{round_number}, {living_humans}, {living_zombies}, {dead_bodies}")

        # Stop if one faction is eliminated
        if living_humans == 0 or living_zombies == 0:
            logging.info("Simulation ended early: One faction was eliminated.")
            break

    logging.info("Simulation completed.")
    print("AI simulation finished. Check 'balance_test.log' for results.")

if __name__ == "__main__":
    run_simulation(rounds=500)
