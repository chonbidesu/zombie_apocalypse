# ui.py

import pygame
import random

from settings import *
from button import Button
import spritesheet

class DrawUI:
    """A class to draw the ui panel to the screen."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.map = self.Map(screen, game.player, self.wrap_text)

        # Load images
        self.player_frame = pygame.image.load("assets/player_frame.png").convert_alpha()
        self.hp_bar = pygame.image.load("assets/hp_bar.png").convert_alpha()
        self.player_portrait = pygame.image.load("assets/male1.png").convert_alpha()
        self.player_sprite_sheet_image = pygame.image.load("assets/male1_sprite_sheet.png").convert_alpha()
        self.player_info = pygame.image.load("assets/player_info.png").convert_alpha()
        self.viewport_frame = pygame.image.load('assets/viewport_frame.png').convert_alpha()
        self.description_panel_image = pygame.image.load("assets/description_panel.png").convert_alpha()
        self.chat_panel_image = pygame.image.load("assets/chat_panel.png").convert_alpha()
        self.inventory_panel_image = pygame.image.load("assets/inventory_panel.png").convert_alpha()
        self.equipped_image = pygame.image.load("assets/equipped_panel.png").convert_alpha()
        self.zombie_sprite_sheet_image = pygame.image.load("assets/zombie_spritesheet.png").convert_alpha()
        self.human_sprite_image = pygame.image.load("assets/human_character.png").convert_alpha()

        # Set up ui elements
        self.viewport_frame_width, self.viewport_frame_height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2
        self.grid_start_x, self.grid_start_y = (self.viewport_frame_width // 9) + 12, (self.viewport_frame_height // 9) + 12
        self.viewport_group = self.create_viewport_group()
        self.button_group = self.create_button_group()
        self.zombie_sprite_group = pygame.sprite.Group()
        self.human_sprite_group = pygame.sprite.Group()
        self.enter_button = Button('enter', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
        self.leave_button = Button('leave', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
        self.zombie_sprite_sheet = spritesheet.SpriteSheet(self.zombie_sprite_sheet_image)
        self.human_sprite_sheet = spritesheet.SpriteSheet(self.human_sprite_image)

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

    #  Set up viewport group
    def create_viewport_group(self):
        viewport_group = pygame.sprite.Group()

        for dy in range(-1, 2):
            for dx in range(-1, 2):
                block_sprite = self.BlockSprite(dx, dy, self.game, self.grid_start_x, self.grid_start_y, self.wrap_text)
                viewport_group.add(block_sprite)
        return viewport_group

    def update_viewport(self):

        for sprite in self.viewport_group:
            sprite.update_data()
            sprite.block.is_known = True

    # Set up action button group
    def create_button_group(self):
        button_group = pygame.sprite.Group()

        buttons = ['barricade', 'search', 'enter']
        for i, button_name in enumerate(buttons):
            button = Button(button_name, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
            button_group.add(button)
        return button_group

    # Handle text wrapping
    def wrap_text(self, text, font, max_width):
        """Wrap the text to fit inside a given width."""
        lines = []
        words = text.split(" ")
        current_line = ""

        for word in words:
            # Check if adding the word exceeds the width
            test_line = current_line + (word if current_line == "" else " " + word)
            test_width, _ = font.size(test_line)

            if test_width <= max_width:
                current_line = test_line  # Add the word to the current line
            else:
                if current_line != "":
                    lines.append(current_line)  # Append the current line if it's not empty
                current_line = word  # Start a new line with the current word

        if current_line != "":  # Append the last line if it has any content
            lines.append(current_line)

        return lines

    def draw_viewport_frame(self):
        """Draw the 3x3 viewport representing the player's surroundings."""
        scaled_viewport_frame = pygame.transform.scale(self.viewport_frame, (self.viewport_frame_width, self.viewport_frame_height))
        self.screen.blit(scaled_viewport_frame, (10, 10))

    def draw_neighbourhood_name(self):
        # Draw neighbourhood name
        current_x, current_y = self.game.player.location
        current_block = self.game.city.block(current_x, current_y)
        pygame.draw.rect(self.screen, ORANGE, (10, self.viewport_frame_height + 10, self.viewport_frame_width, 30))
        text = font_large.render(current_block.neighbourhood, True, WHITE)
        self.screen.blit(text, ((self.viewport_frame_width // 2) - (text.get_width() // 2), self.viewport_frame_height + 15))

    # Update action buttons according to player status
    def update_action_buttons(self):
        if self.game.player.inside:
            for button in self.button_group:
                if button.name == 'enter':
                    self.button_group.remove(button)
                    self.button_group.add(self.leave_button)
        else:
            for button in self.button_group:
                if button.name == 'leave':
                    self.button_group.remove(button)
                    self.button_group.add(self.enter_button)

    # Draw actions panel
    def draw_actions_panel(self):
        """Draw the Available Actions panel with button sprites."""

        # Panel dimensions
        panel_x = 10
        panel_y = (SCREEN_HEIGHT // 2) + 40
        panel_width = SCREEN_HEIGHT // 2
        panel_height = SCREEN_HEIGHT * 3 // 20 - 10

        # Draw the panel background and border
        pygame.draw.rect(self.screen, WHITE, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(self.screen, BLACK, (panel_x, panel_y, panel_width, panel_height), 2)

        # Render the title
        title_text = font_large.render("Available Actions", True, BLACK)
        title_rect = title_text.get_rect(center=(panel_x + panel_width // 2, panel_y + 30))
        self.screen.blit(title_text, title_rect)
        self.button_group.draw(self.screen)

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
                current_observations += f'You are standing in {properties.description}.'

        # Add observations for zombies and dead bodies
        zombies_here = [
            zombie for zombie in self.game.zombies.list
            if zombie.location == self.game.player.location and zombie.inside == self.game.player.inside
        ]
        living_zombies = [zombie for zombie in zombies_here if not zombie.is_dead]
        dead_zombies = [zombie for zombie in zombies_here if zombie.is_dead]

        if living_zombies:
            if len(living_zombies) == 1:
                current_observations += "There is a lone zombie here. "
            else:
                current_observations += f"There are {len(living_zombies)} zombies here. "

        if dead_zombies:
            if len(dead_zombies) == 1:
                current_observations += "You see a dead body."
            else:
                current_observations += f"You see {len(dead_zombies)} dead bodies."

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
                    self.screen, zombie, self.zombie_sprite_sheet, 8, 264, 390, 0.4, (0, 0, 0)
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
                    self.screen, human, self.human_sprite_sheet, 1, 264, 390, 0.4, (0, 0, 0)
                )
                self.human_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)                

        # Remove sprites for humans that are no longer here
        for sprite in list(self.human_sprite_group):
            if sprite not in updated_sprites or sprite.npc.is_dead:
                sprite.kill()

    def draw_description_panel(self):
        """Draw the description panel on the right side of the screen."""

        description_start_x = SCREEN_HEIGHT // 2 + 10
        description_width = SCREEN_WIDTH - (SCREEN_HEIGHT // 2) - 20
        description_height = SCREEN_HEIGHT * 25 // 32

        scaled_panel_image = pygame.transform.scale(self.description_panel_image, (description_width, description_height))
        self.screen.blit(scaled_panel_image, (description_start_x, 10))

        # Determine the setting image
        current_x, current_y = self.game.player.location
        current_block = self.game.city.block(current_x, current_y)        
        image_suffix = "inside" if self.game.player.inside else "outside"
        image_path = f"assets/{current_block.type.name.lower()}_{image_suffix}.png"

        try:
            setting_image = pygame.image.load(image_path)
        except FileNotFoundError:
            setting_image = pygame.Surface((1, 1))  # Fallback if image not found
            setting_image.fill((0, 0, 0))

        # Scale the setting image
        setting_image_width = description_width * 5 // 6
        setting_image_height = setting_image_width * 4 // 9  # 9:4 aspect ratio
        scaled_setting_image = pygame.transform.scale(setting_image, (setting_image_width, setting_image_height))

        # Blit the setting image at the top of the panel
        setting_image_x = description_start_x + (description_width - setting_image_width) // 2
        setting_image_y = 50
        self.screen.blit(scaled_setting_image, (setting_image_x, setting_image_y))

        # Arrange sprite groups in a row, aligning their bottom edges
        sprite_width = 50  # Define the width for each zombie sprite
        sprite_spacing = 20  # Define the spacing between sprites
        zombie_row_start_x = setting_image_x + setting_image_width - len(self.zombie_sprite_group) * (sprite_width + sprite_spacing) - 10
        human_row_start_x = setting_image_x + 10
        row_start_y = setting_image_y + setting_image_height + 20  # Align with bottom edge of setting image

        for index, sprite in enumerate(self.zombie_sprite_group):
            # Calculate position for each zombie sprite
            sprite.rect.midbottom = (
                zombie_row_start_x + index * (sprite_width + sprite_spacing) + sprite_width // 2,
                row_start_y
            )

        for index, sprite in enumerate(self.human_sprite_group):
            # Calculate position for each zombie sprite
            sprite.rect.midbottom = (
                human_row_start_x + index * (sprite_width + sprite_spacing) + sprite_width // 2,
                row_start_y
            )

        self.zombie_sprite_group.update()
        self.zombie_sprite_group.draw(self.screen)

        self.human_sprite_group.update()
        self.human_sprite_group.draw(self.screen)        

        # Get the description text and wrap it to fit within the panel
        text_start_y = setting_image_y + setting_image_height + 20
        paragraphs = []
        current_observations = self.description()
        for observation in current_observations:
            wrapped_text = self.wrap_text(observation, font_large, description_width - 100)  # 50px padding on each side
            for line in wrapped_text:
                paragraphs.append(line)
            paragraphs.append(" ")

        # Render each paragraph inside the description panel
        for line in paragraphs:
            text = font_large.render(line, True, BLACK)
            text_rect = text.get_rect(x=description_start_x + 50, y=text_start_y)  # Padding of 50px on the left
            self.screen.blit(text, text_rect)
            text_start_y += font_large.size(line)[1]  # Move down for the next line

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

    class BlockSprite(pygame.sprite.Sprite):
        """Represents a visual sprite for a CityBlock in the viewport."""
        def __init__(self, dx, dy, game, grid_start_x, grid_start_y, wrap_text):
            super().__init__()
            self.dx = dx
            self.dy = dy
            self.game = game
            self.block = None # The block this sprite represents
            self.properties = None # Properties of the block
            self.wrap_text = wrap_text
            self.viewport_x = grid_start_x + (dx + 1) * BLOCK_SIZE  # Translate relative dx to viewport position
            self.viewport_y = grid_start_y + (dy + 1) * BLOCK_SIZE  # Translate relative dy to viewport position
            self.image = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
            self.rect = self.image.get_rect(topleft=(self.viewport_x, self.viewport_y))
            self.viewport_npcs = []


        def update_data(self):
            """
            Update the sprite's data based on the player's current location and CityBlock objects.
            """
            # Determine the target block coordinates based on player location and dx, dy offsets
            target_x = self.game.player.location[0] + self.dx
            target_y = self.game.player.location[1] + self.dy

            # Check if the target coordinates are within city bounds
            if 0 <= target_x < CITY_SIZE and 0 <= target_y < CITY_SIZE:
                self.block = self.game.city.block(target_x, target_y)  # Retrieve the CityBlock at (x, y)
                self.properties = BLOCKS[self.block.type]

                # Load the block image
                image_filename = self.properties.image_file
                self.image = pygame.image.load(image_filename).convert_alpha()
                self.image = pygame.transform.scale(self.image, (BLOCK_SIZE, BLOCK_SIZE))

                # Apply zoom effect for street blocks
                if self.block.type == BlockType.STREET:
                    self.apply_zoomed_image()

                # Update the block label
                self.draw_block_label()

                # Clear the current list of viewport zombies
                self.viewport_npcs.clear()

                # Add ViewportNPCs if they are present in this block
                matching_zombies = [
                    zombie for zombie in self.game.zombies.list if zombie.location[0] == target_x and zombie.location[1] == target_y and not zombie.is_dead
                ]
                zombie_count = len(matching_zombies)
                for index, zombie in enumerate(matching_zombies):
                    viewport_zombie = self.ViewportNPC(zombie, index, zombie_count)
                    self.viewport_npcs.append(viewport_zombie)

                matching_humans = [
                    human for human in self.game.humans.list if human.location[0] == target_x and human.location[1] == target_y and not human.is_dead
                ]
                human_count = len(matching_humans)
                for index, human in enumerate(matching_humans):
                    viewport_human = self.ViewportNPC(human, index, human_count, row_offset=2)
                    self.viewport_npcs.append(viewport_human)

                # Draw the zombies onto the block image
                self.draw_npcs()

            else:
                self.image.set_alpha(0)

                          
        def draw_npcs(self):
            """Draw NPC sprites onto the block."""
            for viewport_npc in self.viewport_npcs:
                npc_image = viewport_npc.image
                npc_rect = npc_image.get_rect(center=viewport_npc.position)                
                if viewport_npc.npc.inside and self.game.player.inside and viewport_npc.npc.location == self.game.player.location:
                    self.image.blit(npc_image, npc_rect)
                elif not viewport_npc.npc.inside and not self.game.player.inside:
                    self.image.blit(npc_image, npc_rect)

        def draw_block_label(self):
            """Render the block label onto the block's surface."""
            block_text = self.wrap_text(self.block.name, font_small, BLOCK_SIZE - 2)
            text_height = sum(font_small.size(line)[1] for line in block_text)

            image_copy = self.image.copy()

            label_rect = pygame.Rect(
                0, BLOCK_SIZE - text_height - 2, BLOCK_SIZE, text_height + 2
            )
            if self.properties.is_building:
                if self.block.lights_on:
                    pygame.draw.rect(image_copy, PALE_YELLOW, label_rect)
                else:
                    pygame.draw.rect(image_copy, WHITE, label_rect)
            else:
                pygame.draw.rect(image_copy, WHITE, label_rect)

            # Draw text onto the block surface
            y_offset = label_rect.top + 5
            for line in block_text:
                text_surface = font_small.render(line, True, BLACK)
                text_rect = text_surface.get_rect(center=(BLOCK_SIZE // 2, y_offset))
                image_copy.blit(text_surface, text_rect)
                y_offset += font_small.size(line)[1]

            self.image = image_copy

        def apply_zoomed_image(self):
            """Apply a zoomed-in portion of the block image for street appearance."""
            image_width, image_height = self.image.get_width(), self.image.get_height()

            # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
            zoom_factor = 2
            zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

            # Check if zoom coordinates are already set
            if not hasattr(self, "zoom_x") or not hasattr(self, "zoom_y"):
                # Generate random top-left coordinates for the zoomed-in area
                self.zoom_x = random.randint(0, image_width - zoom_width)
                self.zoom_y = random.randint(0, image_height - zoom_height)

            # Extract the zoomed-in portion
            zoomed_surface = self.image.subsurface((self.zoom_x, self.zoom_y, zoom_width, zoom_height))

            # Scale it to the target block size and assign it to the sprite
            self.image = pygame.transform.scale(zoomed_surface, (BLOCK_SIZE, BLOCK_SIZE))


        class ViewportNPC:
            """A NPC representation for drawing in the viewport."""
            def __init__(self, npc, index, total_npcs, row_offset=0):
                self.npc = npc
                self.size = BLOCK_SIZE // 6  # NPC size as a fraction of the block size

                # Determine row and column for this NPC
                row = index // 3  # Row 0 or 1 plus row offset
                col = index % 3   # Column 0, 1, or 2

                # Calculate horizontal positioning for each column
                row_width = min(total_npcs - row * 3, 3) * (self.size + 2)  # Width of the row
                row_start_x = (BLOCK_SIZE - row_width) // 2  # Center the row horizontally
                x = row_start_x + col * (self.size + 2) + self.size // 2

                # Calculate vertical positioning for each row
                row_height = self.size + 2
                y = (BLOCK_SIZE // 3) + (row + row_offset - 0.5) * row_height  # Row 0 above, row 1 below

                self.position = (x, y)

                # Determine colour based on NPC type
                if npc.is_human:
                    if hasattr(npc, "hostile") and npc.hostile:
                        colour = (255, 0, 0)
                    elif hasattr(npc, "hostile") and not npc.hostile:
                        colour = (0, 0, 255)
                    else:
                        colour = (128, 128, 128)
                else:
                    colour = (0, 255, 0)

                # Create the zombie image
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                self.image.fill(colour)

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
            bar_y = self.rect.y + self.rect.height - 15

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

    class Map:
        def __init__(self, screen, player, wrap_text):
            self.screen = screen
            self.player = player
            self.wrap_text = wrap_text
            self.GRID_ROWS = 10
            self.GRID_COLS = 10
            self.BLOCK_PADDING = 2
            self.zoom_in = True
            self.cached_zoom = {}

            self.MAP_SIZE = SCREEN_HEIGHT - 50
            self.block_size = (self.MAP_SIZE - (self.GRID_ROWS + 1) * self.BLOCK_PADDING) // self.GRID_ROWS
            self.map_surface = pygame.Surface((SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))
            self.map_surface.fill((255, 255, 255))
            self.city_map = pygame.Surface((self.MAP_SIZE, self.MAP_SIZE))
            self.city_map.fill((0, 0, 0))

            self.block_images = {
                block_type: pygame.transform.scale(
                    pygame.image.load(properties.image_file).convert_alpha(), 
                    (self.block_size, self.block_size)
                ) 
                for block_type, properties in BLOCKS.items()
            }

        def draw(self):
            blink_state = pygame.time.get_ticks() // 500 % 2 == 0
            player_block = self.player.city.block(self.player.location[0], self.player.location[1])

            self.screen.blit(self.map_surface, (10, 10))

            map_data = self._get_map_data(player_block)
            self._draw_map(map_data)
            if blink_state:
                self._draw_player_location(map_data)  
            
            self.screen.blit(self.city_map, (25, 25))

            self._draw_map_info()

        def _draw_map(self, map_data): 
            index = 0
            for row in range(self.GRID_ROWS):
                for col in range(self.GRID_COLS):
                    # Calculate top-left corner of the block
                    x = self.BLOCK_PADDING + col * (self.block_size + self.BLOCK_PADDING) + 4
                    y = self.BLOCK_PADDING + row * (self.block_size + self.BLOCK_PADDING) + 4

                    if self.zoom_in:
                        player_block = self.player.city.block(self.player.location[0], self.player.location[1])
                        neighbourhood_index = NEIGHBOURHOODS.index(player_block.neighbourhood)
                        col_offset = neighbourhood_index % 10 * 10
                        row_offset = int(neighbourhood_index // 10) * 10
                        current_block = self.player.city.block(col + col_offset, row + row_offset)
    
                        # Check if the player has seen the block before
                        if current_block.is_known:
                            # Draw block
                            block_image = self.block_images[current_block.type]
                            if current_block.type == BlockType.STREET:
                                image_width, image_height = block_image.get_width(), block_image.get_height()

                                # Define the zoom-in factor (e.g., 2x zoom = 50% of the original size)
                                zoom_factor = 2
                                zoom_width, zoom_height = image_width // zoom_factor, image_height // zoom_factor

                                # Check if zoom coordinates are cached
                                if (col, row) in self.cached_zoom:
                                    (zoom_x, zoom_y) = self.cached_zoom[(col, row)]
                                else:
                                    zoom_x = random.randint(0, image_width - zoom_width)
                                    zoom_y = random.randint(0, image_height - zoom_height)

                                    self.cached_zoom[(col, row)] = (zoom_x, zoom_y)

                                # Extract the zoomed-in portion
                                zoomed_surface = block_image.subsurface((zoom_x, zoom_y, zoom_width, zoom_height))

                                # Scale it to the target block size and assign it to the sprite
                                block_image = pygame.transform.scale(zoomed_surface, (self.block_size, self.block_size))

                            label_name = map_data[index]
                            block_image = self._draw_block_label(block_image, label_name)

                            self.city_map.blit(block_image, (x, y))

                        else:
                            # Draw fog of war block
                            pygame.draw.rect(self.city_map, (125, 125, 125), (x, y, self.block_size, self.block_size))

                    else:
                        # Draw neighbourhood
                        neighbourhood_block = pygame.Surface((self.block_size, self.block_size))
                        neighbourhood_block.fill((255, 255, 255))
                        label_name = map_data[index]
                        neighbourhood_block = self._draw_block_label(neighbourhood_block, label_name)
                        self.city_map.blit(neighbourhood_block, (x, y))

                    index += 1

        def _draw_block_label(self, block_image, label_name):
            """Render the block label onto the block's surface."""
            label_text = self.wrap_text(label_name, font_xs, self.block_size - 2)
            text_height = sum(font_xs.size(line)[1] for line in label_text)

            image_copy = block_image.copy()
            label_rect = pygame.Rect(
                0, self.block_size - text_height - 2, self.block_size, text_height + 2
            )

            if self.zoom_in:
                pygame.draw.rect(image_copy, WHITE, label_rect)
            else:
                pygame.draw.rect(image_copy, ORANGE, label_rect)

            # Draw text onto the block surface
            y_offset = label_rect.top + 5
            for line in label_text:
                text_surface = font_xs.render(line, True, BLACK)
                text_rect = text_surface.get_rect(center=(self.block_size // 2, y_offset))
                image_copy.blit(text_surface, text_rect)
                y_offset += font_xs.size(line)[1]

            return image_copy

        def _get_map_data(self, player_block):
            if self.zoom_in:
                map_data = []
                neighbourhood_index = NEIGHBOURHOODS.index(player_block.neighbourhood)
                neighbourhood_x = neighbourhood_index % 10 * 10
                neighbourhood_y = int(neighbourhood_index // 10) * 10

                for y in range(neighbourhood_y, neighbourhood_y + 10):
                    for x in range(neighbourhood_x, neighbourhood_x + 10):
                        block = self.player.city.block(x, y)
                        map_data.append(block.name)
                return map_data
            
            else:
                return NEIGHBOURHOODS
                        

        def _draw_player_location(self, map_data):
            (player_x, player_y) = self.player.location
            current_block = self.player.city.block(player_x, player_y)
            for index, datum in enumerate(map_data):
                if self.zoom_in:
                    if datum == current_block.name:
                        player_index = index
                else:
                    if datum == current_block.neighbourhood:
                        player_index = index
            
            # Count the city blocks until player location is reached
            index = 0
            for row in range(self.GRID_ROWS):
                for col in range(self.GRID_COLS):
                    if index == player_index:                    
                        # Calculate top-left corner of the city block
                        x = self.BLOCK_PADDING + col * (self.block_size + self.BLOCK_PADDING) + 4
                        y = self.BLOCK_PADDING + row * (self.block_size + self.BLOCK_PADDING) + 4

                        pygame.draw.circle(self.city_map, (255, 0, 0), (x + self.block_size // 2, y + self.block_size // 2 - 10), 10)
                    
                    index += 1

        def _draw_map_info(self):
            map_info_width = SCREEN_WIDTH - self.MAP_SIZE - 30
            self.map_info = pygame.Surface((map_info_width, self.MAP_SIZE))
            self.map_info.fill((255, 255, 255))
            map_info_text = {
                'preheader': 'The City of',
                'header': 'MALTON',
                'body_1': 'Press ESC to exit map.',
                'body_2': 'Use PAGE UP and PAGE DOWN to zoom.',
            }
            y_offset = 50
            for format, text in map_info_text.items():
                if format == 'header':
                    line_size = font_xl.size(text)[1]
                    line_surface = font_xl.render(text, True, BLACK)
                    line_rect = line_surface.get_rect(midtop=(map_info_width // 2, y_offset))
                    self.map_info.blit(line_surface, line_rect)
                    y_offset += line_size
                else:
                    line_size = font_large.size(text)[1]
                    line_surface = font_large.render(text, True, BLACK)
                    line_rect = line_surface.get_rect(midtop=(map_info_width // 2, y_offset))
                    self.map_info.blit(line_surface, line_rect)
                    y_offset += line_size                    

            self.map_surface.blit(self.map_info, (self.MAP_SIZE + 20, 20))




class Cursor(object):
    def __init__(self):
        self.default_image = pygame.image.load('assets/zombie_hand.png').convert_alpha()
        self.attack_image = pygame.image.load('assets/crosshair.png').convert_alpha()
        self.image = self.default_image
        self.rect = self.image.get_rect(center=(0,0))
        pygame.mouse.set_visible(False)
    
    def update(self, game_ui):
        self.image = self.default_image
        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.rect.topleft = (mouse_x, mouse_y)        
        for zombie in game_ui.zombie_sprite_group:
            if zombie.rect.collidepoint((mouse_x, mouse_y)):
                self.image = self.attack_image
                self.rect.center = (mouse_x, mouse_y)

    def draw(self):
        pygame.display.get_surface().blit(self.image, self.rect)


