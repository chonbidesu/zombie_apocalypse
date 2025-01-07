# utils.py

from settings import *

# Get the target of the mouse click
def get_click_target(mouse_pos, player, viewport_group):
    for sprite in viewport_group:
        if sprite.dx == 0 and sprite.dy == 0 and sprite.rect.collidepoint(mouse_pos):
            return 'center block', sprite
        elif sprite.rect.collidepoint(mouse_pos):
            return 'block', sprite
    for sprite in player.inventory:
        if sprite.rect.collidepoint(mouse_pos):
            return 'item', sprite
    return 'screen', None
 
def increment_ticker(player, city, zombies):
    """Increments the ticker to track player actions."""
    player.ticker += 1

    # Check buildings for fuel expiry
    for row in city.grid:
        for block in row:
            if hasattr(block, 'fuel_expiration') and block.fuel_expiration < player.ticker:
                if block.lights_on:
                    block.lights_on = False

    # Each zombie gains an action point
    for zombie in zombies.list:
        zombie.action_points += 1
        zombie.take_action()