# main.py

import pygame
import sys

from core.settings import *
from core import GameInitializer

# Main game loop
def main():

    # Initialize Pygame
    pygame.init()

    # Create screen and clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Apocalypse")
    clock = pygame.time.Clock()

    # Start the game
    debug = False
    game = GameInitializer(screen, clock, debug=debug)
    running = True

    while running:
        
        # Get events
        events = pygame.event.get()

        game.handle_events(events)
        game.update_game_state()  
        game.update_screen()        

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
