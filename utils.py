# utils.py

from settings import *

# Get (x, y) of a specific sprite
def get_sprite_coordinates(sprite, x_groups, y_groups):
    for x, group in enumerate(x_groups):
        if sprite in group:
            x_coordinate = x
            break

    for y, group in y_groups.items():
        if sprite in group:
            y_coordinate = y
            break

    return x_coordinate, y_coordinate
 
# Get the target of the mouse click
def get_click_target(mouse_pos, player, viewport_group):
    current_block = get_block_at_player(player)
    if current_block.rect.collidepoint(mouse_pos):
        return 'current block', current_block
    for sprite in player.inventory:
        if sprite.rect.collidepoint(mouse_pos):
            return 'item', sprite
    for sprite in viewport_group:
        if sprite.rect.collidepoint(mouse_pos):
            return 'block', sprite
    return 'screen', None

# Get all sprites at (x, y)
def get_sprites_at(x, y, x_groups, y_groups):
    sprites_x = x_groups[x]
    sprites_y = y_groups[y]
    return set(sprites_x) & set(sprites_y)

# Get filtered sprites at (x, y)
def get_filtered_sprites_at(x, y, group, x_groups, y_groups):
    all_sprites = get_sprites_at(x, y, x_groups, y_groups)
    filtered_sprites = []
    for sprite in all_sprites:
        if sprite in group:
            filtered_sprites.append(sprite)
    
    return filtered_sprites

# Get the city block at player's current location
def get_block_at_player(player, city):
    block_list = get_filtered_sprites_at(
        player.location[0], player.location[1], city.cityblock_group, 
        player.x_groups, player.y_groups
        )
    for block in block_list:
        return block
    
