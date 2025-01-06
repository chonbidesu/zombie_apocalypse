# logic.py

from collections import defaultdict
import pygame

from settings import *

# Create dictionaries to manage the x, y coordinate groups
def create_xy_groups():
    x_groups = []
    y_groups = []
    for _ in range(100):
        x_groups.append(pygame.sprite.Group())
        y_groups.append(pygame.sprite.Group())
    return x_groups, y_groups

# Create zombie groups
def create_zombie_groups():
    zombie_group = pygame.sprite.Group()
    zombie_display_group = pygame.sprite.Group()
    return zombie_group, zombie_display_group

# Zombie population management
#def populate_city_with_zombies(city, count):
#    """Populates the city with an initial zombie population."""
#    zombies = []
#    for _ in range(count):
#        while True:
#            x = random.randint(0, 99)
#            y = random.randint(0, 99)
#            if not hasattr(city[y][x], 'zombies'):  # Ensure block can have zombies
#                city[y][x].zombies = []
#
#            if len(city[y][x].zombies) < 5:  # Limit zombies per block
#                zombie = Zombie(x, y, city)
#                city[y][x].zombies.append(zombie)
#                zombies.append(zombie)
#                break
#    return zombies    

# Calculate the topleft of the 3x3 viewport grid
def calculate_grid_start():
    grid_start_x = (SCREEN_HEIGHT // 5)
    grid_start_y = (SCREEN_HEIGHT // 5)
    return grid_start_x, grid_start_y

# Update viewport centered on player
viewport_group = pygame.sprite.Group()
def update_viewport(player, zombie_display_group):
    viewport_group.empty()
    player_x, player_y = player.location

    grid_start_x, grid_start_y = calculate_grid_start()

    # Collect blocks in a 3x3 grid around the player
    for row_offset in range(-1, 2):
        for col_offset in range(-1, 2):
            block_x, block_y = player_x + col_offset, player_y + row_offset

            #Ensure block coordinates are within city bounds
            if 0 <= block_x < len(player.x_groups) and 0 <= block_y < len(player.y_groups):
                blocks = set(player.x_groups[block_x]) & set(player.y_groups[block_y]) & set(player.city.cityblock_group)
                if blocks:
                    block = next(iter(blocks))

                    # Load the block's image if not already loaded
                    if block.image is None:
                        block.render_label()
                        block.image # Trigger lazy load

                    block.rect = pygame.Rect(
                        grid_start_x + col_offset * BLOCK_SIZE,
                        grid_start_y + row_offset * BLOCK_SIZE,
                        BLOCK_SIZE,
                        BLOCK_SIZE
                    )
                    viewport_group.add(block)

    for block in player.city.cityblock_group:
        if block not in viewport_group:
            block.unload_image()

    # Update zombies in the viewport
    zombies_at_coordinates = defaultdict(list)
    zombie_display_group.empty()
    for zombie in player.zombie_group:
        zombie_x, zombie_y = zombie.get_coordinates()
        zombies_at_coordinates[(zombie_x, zombie_y)].append(zombie)
    
    for (zombie_x, zombie_y), zombies in zombies_at_coordinates.items():
        if player.inside:
            if zombie_x == player_x and zombie_y == player_y:
                for zombie in zombies:
                    if zombie.inside:
                        zombie.rect = pygame.Rect(
                            grid_start_x + BLOCK_SIZE,
                            grid_start_y + BLOCK_SIZE,
                            BLOCK_SIZE // 2,
                            BLOCK_SIZE // 2
                        )
                        viewport_group.add(zombie)

        else:    
            # Check if the zombie is within the 3x3 viewport
            if player_x - 1 <= zombie_x <= player_x + 1 and player_y - 1 <= zombie_y <= player_y + 1:
                for index, zombie in enumerate(zombies):
                    if not zombie.inside:

                        # Update zombie rect to align with its block's position
                        col_offset = zombie_x - player_x
                        row_offset = zombie_y - player_y
                        base_x = grid_start_x + col_offset * BLOCK_SIZE
                        base_y = grid_start_y + row_offset * BLOCK_SIZE

                        zombie_width = BLOCK_SIZE // 6
                        total_zombie_width = len(zombies) * zombie_width
                        row_start_x = base_x + (BLOCK_SIZE - total_zombie_width) // 2

                        # Get your zombies in a row
                        zombie.rect = pygame.Rect(
                            row_start_x + index * zombie_width,
                            base_y + (BLOCK_SIZE - zombie_width) // 2,
                            zombie_width,
                            zombie_width
                        )
                        viewport_group.add(zombie)

        # Update zombie characters in the description panel
        for index, zombie in enumerate(zombies_at_coordinates[zombie_x, zombie_y]):
            character_sprite = zombie.update_character_sprite(player, index, len(zombies_at_coordinates[zombie_x, zombie_y]))
            if character_sprite:
                zombie_display_group.add(character_sprite)
