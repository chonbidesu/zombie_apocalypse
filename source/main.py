# main.py

import pygame
import sys

from settings import *
from game import GameInitializer
import menus

# Main game loop
def main():
    running = True

    # Initialize Pygame
    pygame.init()

    # Create screen and clock
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Zombie Apocalypse")
    clock = pygame.time.Clock()
    action_interval = ACTION_INTERVAL
    action_timer = 0

    # Initialize game
    game = GameInitializer(screen)

    while running:

        # Handle events
        events = pygame.event.get()
        game.event_handler.handle_events(events, menus.ContextMenu)

        # Handle pause menu
        if game.paused:
            game.pause_menu.draw_pause_menu(screen)

        # Handle opening the map
        elif game.reading_map:
            game.game_ui.map.draw()

        else:
            # Draw game elements to screen
            game.game_ui.update()
            game.game_ui.draw(game.chat_history)

            # Handle right-click menu
            if game.popup_menu:
                game.popup_menu.handle_events(events)
                game.popup_menu.draw()

        # Draw the cursor
        game.cursor.update(game.game_ui)
        game.cursor.draw()

        # Handle player death
        if game.player.is_dead:
            game.game_ui.death_screen.handle_events(events)
            game.game_ui.death_screen.draw()
            if game.game_ui.death_screen.restart:
                game = GameInitializer(screen)  # Reinitialize the game
                game.game_ui.death_screen.restart = False

        # Update NPC actions every half-second
        action_timer += clock.get_time()
        if action_timer >= action_interval:
            game.npcs.gain_ap()
            game.npcs.take_action()
            action_timer = 0
            game.ticker += 1
            
            # Check buildings for fuel expiry
            for row in game.city.grid:
                for block in row:
                    if hasattr(block, 'fuel_expiration') and block.fuel_expiration < game.ticker:
                        if block.lights_on:
                            block.lights_on = False

        pygame.display.flip()
        clock.tick(FPS)

    game.cursor.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
