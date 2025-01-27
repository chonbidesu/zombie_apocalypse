# ui.py

import pygame
import random

from settings import *
from widgets import Button
import spritesheet

class DrawUI:
    """A class to draw the ui panel to the screen."""
    def __init__(self, game, screen):
        self.game = game#
        self.screen = screen#
        self.map = self.Map(screen, game.player, self.wrap_text)

        # Load images
        self.player_frame = pygame.image.load("assets/player_frame.png").convert_alpha()
        self.hp_bar = pygame.image.load("assets/hp_bar.png").convert_alpha()
        self.player_portrait = pygame.image.load("assets/male1.png").convert_alpha()
        self.player_sprite_sheet_image = pygame.image.load("assets/male1_sprite_sheet.png").convert_alpha()
        self.player_info = pygame.image.load("assets/player_info.png").convert_alpha()
        
        self.chat_panel_image = pygame.image.load("assets/chat_panel.png").convert_alpha()
        self.inventory_panel_image = pygame.image.load("assets/inventory_panel.png").convert_alpha()
        self.equipped_image = pygame.image.load("assets/equipped_panel.png").convert_alpha()
        self.zombie_sprite_sheet_image = pygame.image.load("assets/zombie_spritesheet.png").convert_alpha()
        self.human_sprite_sheet_image = pygame.image.load("assets/human_spritesheet.png").convert_alpha()

        # Set up ui elements
        self.zombie_sprite_group = pygame.sprite.Group()
        self.human_sprite_group = pygame.sprite.Group()

        self.zombie_sprite_sheet = spritesheet.SpriteSheet(self.zombie_sprite_sheet_image)
        self.human_sprite_sheet = spritesheet.SpriteSheet(self.human_sprite_sheet_image)

        # Set up player portrait
        self.player_portrait_scale = (SCREEN_HEIGHT * 31 // 160 - 20) // 66
        self.player_sprite_sheet = spritesheet.SpriteSheet(self.player_sprite_sheet_image)
        self.player_sprite = self.PlayerSprite(
            self.screen, self.game.player, self.player_sprite_sheet, 6, 66, 66, self.player_portrait_scale, (0, 0, 0)
        )
        self.player_sprite_group = pygame.sprite.GroupSingle()
        self.player_sprite_group.add(self.player_sprite)

    # Draw all ui elements to the screen
    def draw(self, chat_history):
        self.draw_viewport_frame()
        self.draw_neighbourhood_name()
        self.update_action_buttons()
        self.draw_actions_panel()
        self.draw_chat(chat_history)
        self.draw_description_panel()
        self.draw_status()
        self.draw_inventory_panel()
        self.update_viewport()
        self.viewport_group.draw(self.screen)






    def get_current_observations(self):
        """Get the current observations based on the player's surroundings."""
        current_x, current_y = self.game.player.location
        current_block = self.game.city.block(current_x, current_y)        
        current_observations = ""

        # Inside building observations
        if self.game.player.inside:
            current_observations += f'You are standing inside {current_block.name}. '
            if not current_block.lights_on:
                current_observations += 'With the lights out, you can hardly see anything. '
            current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "

            # Check if the building has been ransacked
            if current_block.is_ransacked:
                current_observations += "The interior has been ransacked and needs repairs. "

            # Check if the building has a running generator
            if current_block.generator_installed:
                current_observations += "A portable generator has been set up here. "
                if current_block.lights_on:
                    current_observations += "It is running. "
                else:
                    current_observations += "It is out of fuel. "
        # Outside building observations
        else:
            properties = BLOCKS[current_block.type]
            if properties.is_building:
                current_observations += f'You are standing outside {properties.description}. A sign reads "{current_block.name}". '
                current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "
                if current_block.lights_on:
                    current_observations += "Lights are on inside. "
            else:
                current_observations += f'You are standing in {properties.description}. '

        # Add observations for zombies and dead bodies
        zombies_here = [
            zombie for zombie in self.game.zombies.list
            if zombie.location == self.game.player.location and zombie.inside == self.game.player.inside
        ]
        humans_here = [
            human for human in self.game.humans.list
            if human.location == self.game.player.location and human.inside == self.game.player.inside
        ]
        living_zombies = [zombie for zombie in zombies_here if not zombie.is_dead]
        living_humans = [human for human in humans_here if not human.is_dead]
        dead_bodies = [npc for npc in zombies_here + humans_here if npc.is_dead]

        if living_zombies:
            if len(living_zombies) == 1:
                current_observations += "There is a lone zombie here. "
            else:
                current_observations += f"There are {len(living_zombies)} zombies here. "

        if living_humans:
            if len(living_humans) == 1:
                current_observations += "There is another survivor here. "
            else:
                current_observations += f"There are {len(living_humans)} other survivors here. "

        if dead_bodies:
            if len(dead_bodies) == 1:
                current_observations += "You see a dead body. "
            else:
                current_observations += f"You see {len(dead_bodies)} dead bodies. "

        return current_observations


    def update_observations(self):
        """Update the observations list based on the player's current state."""
        current_x, current_y = self.game.player.location
        current_block = self.game.city.block(current_x, current_y)        
        current_block.observations.clear()  # Clear existing observations
        if self.game.player.inside:
            current_block.observations.append(self.get_current_observations())
            current_block.observations.append(current_block.block_inside_desc)
        else:
            current_block.observations.append(self.get_current_observations())
            current_block.observations.append(current_block.block_outside_desc)

    def description(self):
        """Return the current list of observations as a list."""
        current_x, current_y = self.game.player.location
        current_block = self.game.city.block(current_x, current_y)        
        self.update_observations()  # Ensure observations are current
        return current_block.observations

    def update_npc_sprites(self):
        """
        Update NPC sprites' visibility and position.
        """
        # Keep track of NPCs currently at the player's location
        zombies_here = [
            zombie for zombie in self.game.zombies.list
            if zombie.location == self.game.player.location and zombie.inside == self.game.player.inside
        ]
        humans_here = [
            human for human in self.game.humans.list
            if human.location == self.game.player.location and human.inside == self.game.player.inside
        ]        

        # Update existing sprites or create new ones if necessary
        updated_sprites = []

        for zombie in zombies_here:
            # Check if a sprite for this zombie already exists
            existing_sprite = next(
                (sprite for sprite in self.zombie_sprite_group if sprite.npc == zombie), None
            )
            if existing_sprite:
                updated_sprites.append(existing_sprite)
            elif not zombie.is_dead:
                # Create a new sprite for the zombie
                new_sprite = self.NPCSprite(
                    self.screen, zombie, self.zombie_sprite_sheet, 8, 44, 54, 2.5, (0, 0, 0)
                )
                self.zombie_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)

        # Remove sprites for zombies that are no longer here
        for sprite in list(self.zombie_sprite_group):
            if sprite not in updated_sprites or sprite.npc.is_dead:
                sprite.kill()

        for human in humans_here:
            # Check if a sprite for this human already exists
            existing_sprite = next(
                (sprite for sprite in self.human_sprite_group if sprite.npc == human), None
            )
            if existing_sprite:
                updated_sprites.append(existing_sprite)
            elif not human.is_dead:
                # Create a new sprite for the human
                new_sprite = self.NPCSprite(
                    self.screen, human, self.human_sprite_sheet, 8, 44, 64, 2.5, (0, 0, 0)
                )
                self.human_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)                

        # Remove sprites for humans that are no longer here
        for sprite in list(self.human_sprite_group):
            if sprite not in updated_sprites or sprite.npc.is_dead:
                sprite.kill()



    # Draw the chat panel
    def draw_chat(self, chat_history):

        """Draw the chat window with scrolling support and text wrapping."""
        chat_width, chat_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT * 3 // 10
        chat_start_x, chat_start_y = 10, SCREEN_HEIGHT * 13 // 20 + 30

        scaled_panel_image = pygame.transform.scale(self.chat_panel_image, (chat_width, chat_height))
        self.screen.blit(scaled_panel_image, (chat_start_x, chat_start_y))

        # Draw messages starting from the bottom of the chat area
        # Calculate the max number of visible lines.
        line_height = font_chat.get_linesize()
        max_visible_lines = (chat_height - 50) // line_height
        wrapped_history = []
        for message in chat_history:
            wrapped_history.extend(self.wrap_text(f">> {message}", font_chat, chat_width - 50))

        # Determine which messages to display
        visible_history = wrapped_history[-max_visible_lines:]
        y_offset = chat_start_y + chat_height - 40
    
        for message in reversed(visible_history):
                text = font_chat.render(message, True, WHITE)
                self.screen.blit(text, (chat_start_x + 30, y_offset))
                y_offset -= line_height

    # Draw the player status panel
    def draw_status(self):
        """Draw the player status panel."""
        status_start_x, status_start_y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT * 25 // 32 + 10
        status_width, status_height = SCREEN_WIDTH // 4 - 10, SCREEN_HEIGHT * 31 // 160
        status_panel = pygame.Surface((status_width, status_height), pygame.SRCALPHA)

        self.player_sprite_group.update()
        self.player_sprite_group.draw(status_panel)

        scaled_portrait_frame = pygame.transform.scale(self.player_frame, (status_height - 20, status_height - 20))
        status_panel.blit(scaled_portrait_frame, (0, 0))

        max_hp = self.game.player.max_hp
        current_hp = self.game.player.hp
        hp_ratio = max(current_hp / max_hp, 0)

        pygame.draw.rect(status_panel, (255, 0, 0), (0, status_height - 20, status_height - 20, 20))
        pygame.draw.rect(status_panel, (0, 255, 0), (0, status_height - 20, (status_height - 20) * hp_ratio, 20))

        scaled_hp_bar = pygame.transform.scale(self.hp_bar, (status_height - 20, 20))
        status_panel.blit(scaled_hp_bar, (0, status_height - 20))

        scaled_player_info = pygame.transform.scale(self.player_info, (status_width - status_height + 20, status_height))
        status_panel.blit(scaled_player_info, (status_height - 20, 0))

        y_offset = 30
        status_text = []
        for status_type, status in self.game.player.status().items():
            line = f"{status_type}: {status}"
            status_text.append(line)

        for line in status_text:
            text = font_small.render(line, True, BLACK)
            status_panel.blit(text, (status_height, y_offset))
            y_offset += 20
        
        self.screen.blit(status_panel, (status_start_x, status_start_y))

    # Draw the inventory panel
    def draw_inventory_panel(self):
        """Render the inventory panel in the bottom-right corner of the screen."""
        # Panel dimensionss
        panel_width = (SCREEN_WIDTH * 7 // 16) + (SCREEN_HEIGHT * -7 // 32) - 20
        panel_height = SCREEN_HEIGHT * 31 // 160
        panel_x = SCREEN_WIDTH - panel_width - 10
        panel_y = SCREEN_HEIGHT * 25 // 32 + 10

        scaled_panel_image = pygame.transform.scale(self.inventory_panel_image, (panel_width, panel_height))
        self.screen.blit(scaled_panel_image, (panel_x, panel_y))

        equipped_width = panel_height
        equipped_height = panel_height
        equipped_x = panel_x - equipped_width
        equipped_y = panel_y

        scaled_equipped_image = pygame.transform.scale(self.equipped_image, (equipped_width, equipped_height))
        self.screen.blit(scaled_equipped_image, (equipped_x, equipped_y))      

        # Define the maximum number of items
        MAX_ITEMS = 10
        MAX_ITEMS_PER_ROW = 5

        # Inventory panel positioning and scaling
        item_width = int(panel_width * 0.14)
        item_height = int(panel_height * 0.32)
        highlight = pygame.Surface((item_width, item_height), pygame.SRCALPHA)

        # Position offsets for rows
        start_x = panel_x + int(panel_width * 0.06)
        first_row_y = panel_y + int(panel_height * 0.13)
        second_row_y = first_row_y + item_height + int(panel_height * 0.11)

        # Scale each inventory item image before drawing
        for index, item in enumerate(list(self.game.player.inventory)[:MAX_ITEMS]):
            row = index // MAX_ITEMS_PER_ROW
            col = index % MAX_ITEMS_PER_ROW

            item_x = start_x + col * (item_width + int(panel_width * 0.05))
            item_y = first_row_y if row == 0 else second_row_y

            # Update item rect position
            item.rect.topleft = (item_x, item_y)

            # Scale the item image to the desired size for consistent drawing
            if item.image.get_size() != (item_width, item_height):
                item.scale_image(item_width, item_height)

            # Highlight the item's slot if the item is equipped
            if item in self.game.player.weapon:
                equipped_properties = ITEMS[item.type]
                highlight.fill((TRANS_YELLOW))
                self.screen.blit(highlight, item.rect.topleft)

                # Draw enlarged equipped item
                equipped_item_width = equipped_width * 3 // 5
                equipped_item_height = equipped_height * 3 // 5
                enlarged_image = pygame.transform.scale(self.game.player.weapon.sprite.image, (equipped_item_width, equipped_item_height))
                equipped_item_x = equipped_x + equipped_width // 2 - (equipped_item_width // 2)
                equipped_item_y = equipped_y + equipped_height // 2 - (equipped_item_height // 2)
                self.screen.blit(enlarged_image, (equipped_item_x, equipped_item_y))

                # Draw equipped item label
                equipped_text = font_large.render(equipped_properties.item_type, True, ORANGE)
                equipped_text_shadow = font_large.render(equipped_properties.item_type, True, BLACK)                
                text_width = equipped_text.get_width()
                self.screen.blit(equipped_text_shadow, (equipped_item_x + (equipped_item_width // 2) - (text_width // 2) + 1, equipped_item_y + equipped_item_height + 8))                
                self.screen.blit(equipped_text, (equipped_item_x + (equipped_item_width // 2) - (text_width // 2), equipped_item_y + equipped_item_height + 7))

                # Draw currently loaded ammo
                if equipped_properties.item_function == ItemFunction.FIREARM:
                    label_x = equipped_item_x + equipped_item_width - 20
                    label_y = equipped_item_y + equipped_item_height - 20
                    pygame.draw.rect(self.screen, WHITE, (label_x, label_y, 20, 20))
                    loaded_ammo = font_large.render(str(item.loaded_ammo), True, BLACK)
                    self.screen.blit(loaded_ammo, (label_x + 5, label_y + 2))

            else:
                highlight.fill((0, 0, 0, 0))

        # Draw the inventory group to screen
        self.game.player.inventory.draw(self.screen)

    def circle_wipe(self, target_function, chat_history, duration=1.0):
        """Perform a circle wipe transition effect and call the target_function to change game state."""
        max_radius = int((SCREEN_WIDTH**2 + SCREEN_HEIGHT**2)**0.5) # Cover the screen
        clock = pygame.time.Clock()
        steps = int(duration * 30)
        increment = max_radius // steps

        # Create surface for the mask effect
        mask_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

        # Circle wipe to black
        for radius in range(max_radius, 0, -increment):
            self.draw(chat_history)
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            clock.tick(30)

        # Execute the target function
        result = target_function()
        self.update_npc_sprites()

        # Reverse circle wipe to reveal new state
        for radius in range(0, max_radius, increment):
            self.draw(chat_history)
            mask_surface.fill((0, 0, 0, 255))
            pygame.draw.circle(mask_surface, (0, 0, 0, 0), (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2), radius)
            self.screen.blit(mask_surface, (0, 0))
            pygame.display.flip()
            clock.tick(60)

        return result

    def action_progress(self, message, chat_history, duration=6.0):
        """Display a 'Searching...' message with incrementing dots, or a similar message."""
        clock = pygame.time.Clock()
        steps = int(duration * 2)
        dot_limit = 6

        def draw_message(message):
            self.draw(chat_history)
            text_surface = font_xl.render(message, True, (255, 255, 255))
            # Check if text_rect has been cached
            if not hasattr(self, 'text_rect'):
                self.text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(text_surface, self.text_rect)
            pygame.display.flip()

        # Display the message and increment dots
        for i in range(steps):
            if i // 2 < dot_limit:
                current_message = message + " ." * (i // 2)
            draw_message(current_message)
            clock.tick(20)

        # Reset the text_rect after we are done with it
        del self.text_rect

    class PlayerSprite(pygame.sprite.Sprite):
        """A player sprite for the status panel."""
        def __init__(self, screen, player, sprite_sheet, frame_count, frame_width, frame_height, scale, colour):
            super().__init__()
            self.screen = screen
            self.player = player
            self.sprite_sheet = sprite_sheet
            self.frame_count = frame_count
            self.frame_height = frame_height
            self.frame_width = frame_width
            self.scale = scale
            self.colour = colour
            self.current_frame = 0
            self.animation_speed = 0.35
            self.last_update_time = pygame.time.get_ticks()

            self.start_frame = 0
            self.current_frame = 0

            self.update_animation_set()
            self.image = self.sprite_sheet.get_image(
                frame=self.current_frame,
                width=self.frame_width,
                height=self.frame_height,
                scale=self.scale,
                colour=self.colour,
            )
            self.rect = self.image.get_rect()

        def update_animation_set(self):
            """Update the animation frame range based on player's HP."""
            previous_start_frame = self.start_frame

            if self.player.hp > self.player.max_hp * 0.5:
                self.start_frame = 0  # Normal animation
            else:
                self.start_frame = self.frame_count  # Use the second set of frames

            if self.start_frame != previous_start_frame:
                self.current_frame = self.start_frame

        def update(self):
            """Update the sprite's animation frame."""
            now = pygame.time.get_ticks()
            self.update_animation_set()

            if now - self.last_update_time > self.animation_speed * 1000:
                self.last_update_time = now
                self.current_frame = self.start_frame + ((self.current_frame - self.start_frame - 1) % self.frame_count)
                self.image = self.sprite_sheet.get_image(
                    frame=self.current_frame,
                    width=self.frame_width,
                    height=self.frame_height,
                    scale=self.scale,
                    colour=self.colour,
                )

    




    class NPCSprite(pygame.sprite.Sprite):
        """An NPC sprite for the description panel."""
        def __init__(self, screen, npc, sprite_sheet, frame_count, frame_width, frame_height, scale, colour):
            super().__init__()
            self.screen = screen
            self.npc = npc  # Reference to the parent NPC
            self.sprite_sheet = sprite_sheet
            self.frame_count = frame_count  # Total number of frames
            self.frame_width = frame_width  # Width of each frame
            self.frame_height = frame_height  # Height of each frame
            self.scale = scale  # Scale factor for the frames
            self.colour = colour  # Transparent color for the frames
            self.current_frame = random.randint(0, 7)  # Current frame index
            self.animation_speed = 0.15  # Animation speed (seconds per frame)
            self.last_update_time = pygame.time.get_ticks()  # Time since the last frame update
            self.hp_bar_height = 10

            # Set the initial image and rect
            self.image = self.sprite_sheet.get_image(
                frame=self.current_frame,
                width=self.frame_width,
                height=self.frame_height,
                scale=self.scale,
                colour=self.colour,
            )
            self.rect = self.image.get_rect()

        def draw_hp_bar(self):
            max_hp = NPC_MAX_HP
            current_hp = self.npc.hp
            bar_width = self.rect.width - 50
            hp_ratio = max(current_hp / max_hp, 0)

            bar_x = self.rect.x + 25
            bar_y = self.rect.y + self.rect.height + 5

            pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, bar_y, bar_width, self.hp_bar_height))
            pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, self.hp_bar_height))

        def update(self):
            """Update the sprite's animation frame."""
            now = pygame.time.get_ticks()
            if now - self.last_update_time > self.animation_speed * 1000:  # Convert to milliseconds
                self.last_update_time = now
                self.current_frame = (self.current_frame + 1) % self.frame_count  # Loop through frames
                self.image = self.sprite_sheet.get_image(
                    frame=self.current_frame,
                    width=self.frame_width,
                    height=self.frame_height,
                    scale=self.scale,
                    colour=self.colour,
                )
            self.draw_hp_bar()







