# main.py

import pygame
import sys
from collections import deque

from settings import *
from game import GameInitializer

# Main game loop
def main():

    # Initialize Pygame
    pygame.init()

    # Create screen and clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Apocalypse")
    clock = pygame.time.Clock()

    # Set up AI action queue
    action_interval = ACTION_INTERVAL
    action_timer = 0
    action_queue = deque()
    actions_per_frame = 20

    # Start the game
    game = GameInitializer(screen)
    running = True

    while running:

        # Get events
        events = pygame.event.get()

        # Title screen
        if game.title_screen:
            game.title_event_handler.handle_events(events)
            if game.load_menu:
                game.menu.load_menu.draw(screen)
            elif game.start_new_game:
                game.initialize_game()
                game.title_screen = False
            else:
                game.menu.title_menu.draw(screen)

        else:

            # Handle pause menu
            if game.paused:
                game.menu_event_handler.handle_events(events)
                if game.save_menu:
                    game.menu.save_menu.draw(screen)
                elif game.load_menu:             
                    game.menu.load_menu.draw(screen)
                else:
                    game.menu.pause_menu.draw(screen)

            # Handle opening the map
            elif game.reading_map:
                game.map_event_handler.handle_events(events)
                game.game_ui.map.draw()

            else:
                # Handle events
                game.event_handler.handle_events(events)

                # Draw game elements to screen
                game.game_ui.update()
                game.game_ui.draw(game.chat_history)

                # Handle right-click menu
                if game.popup_menu:
                    game.popup_menu.handle_events(events)
                    game.popup_menu.draw()

                # Restart NPC action queue every action interval
                action_timer += clock.get_time()
                if action_timer >= action_interval:
                    game.state.npcs.gain_ap() # Grant AP to all NPCs
                    action_queue = deque(game.state.npcs.list) # Load all NPCs into the queue
                    action_timer = 0
                    game.ticker += 1
                    
                    # Check buildings for fuel expiry
                    for row in game.state.city.grid:
                        for block in row:
                            if hasattr(block, 'fuel_expiration') and block.fuel_expiration < game.ticker:
                                if block.lights_on:
                                    block.lights_on = False         

                # Process the action queue in batches
                for _ in range(min(actions_per_frame, len(action_queue))):
                    npc = action_queue.popleft() # Get next npc
                    npc.state.get_action()
                    npc.state.act()

                # Handle player death
                if game.state.player.is_dead:
                    game.game_ui.death_screen.handle_events(events)
                    game.game_ui.death_screen.draw()
                    if game.game_ui.death_screen.restart:
                        game = GameInitializer(screen)  # Reinitialize the game
                        game.game_ui.death_screen.restart = False                                              

            # Update the cursor
            game.cursor.update(game.game_ui)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
