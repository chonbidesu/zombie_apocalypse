import pygame
import random

from settings import *
from ui.utils import WrapText, SpriteSheet
from ui.widgets import Button
from data import BLOCKS, BlockType, ITEMS, ItemFunction, NEIGHBOURHOODS

class ActionsPanel:
    """Draw the actions panel and buttons."""
    def __init__(self, game, screen):
        self.screen = screen
        self.game = game
        self.width = SCREEN_HEIGHT // 2
        self.height = SCREEN_HEIGHT * 3 // 20 - 10
        self.button_group = self._create_button_group()
        self.enter_button = Button('enter', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)
        self.leave_button = Button('leave', x=40 + 2 * 120, y=(SCREEN_HEIGHT // 2) + 80)        

    def draw(self):
        x, y = 10, (SCREEN_HEIGHT // 2) + 40     
        # Draw the panel background and border
        pygame.draw.rect(self.screen, WHITE, (x, y, self.width, self.height))
        pygame.draw.rect(self.screen, BLACK, (x, y, self.width, self.height), 2)

        # Render the title
        title_text = font_large.render("Available Actions", True, BLACK)
        title_rect = title_text.get_rect(center=(x + self.width // 2, y + 30))
        self.screen.blit(title_text, title_rect)
        self.button_group.draw(self.screen)        

    # Set up action button group
    def _create_button_group(self):
        button_group = pygame.sprite.Group()

        buttons = ['barricade', 'search', 'enter']
        for i, button_name in enumerate(buttons):
            button = Button(button_name, x=40 + i * 120, y=(SCREEN_HEIGHT // 2) + 80)
            button_group.add(button)
        return button_group        

    # Update action buttons according to player status
    def update(self):
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


class StatusPanel:
    """Display player portrait, HP and other status information."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.width, self.height = SCREEN_WIDTH // 4 - 10, SCREEN_HEIGHT * 31 // 160
        self.portrait_size = self.height - 20
        self.original_hp_bar = pygame.image.load(ResourcePath("assets/hp_bar.png").path).convert_alpha()
        self.hp_bar = pygame.transform.scale(self.original_hp_bar, (self.portrait_size, 20))
        self.original_portrait_frame = pygame.image.load(ResourcePath("assets/player_frame.png").path).convert_alpha()
        self.portrait_frame = pygame.transform.scale(self.original_portrait_frame, (self.portrait_size, self.portrait_size))
        self.player_sprite_sheet_image = pygame.image.load(ResourcePath("assets/male1_sprite_sheet.png").path).convert_alpha()
        self.original_player_info = pygame.image.load(ResourcePath("assets/player_info.png").path).convert_alpha()
        self.player_info = pygame.transform.scale(self.original_player_info, (self.width - self.height + 20, self.height))

        # Set up player portrait
        self.player_portrait_scale = (SCREEN_HEIGHT * 31 // 160 - 20) // 66
        self.player_sprite_sheet = SpriteSheet(self.player_sprite_sheet_image)
        self.player_sprite = PlayerSprite(
            self.screen, self.game.player, self.player_sprite_sheet, 6, 66, 66, self.player_portrait_scale, (0, 0, 0)
        )
        self.player_sprite_group = pygame.sprite.GroupSingle()
        self.player_sprite_group.add(self.player_sprite)

    def draw(self):
        x, y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT * 25 // 32 + 10
        status_panel = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Draw player portrait
        self.player_sprite_group.update()
        self.player_sprite_group.draw(status_panel)
        status_panel.blit(self.portrait_frame, (0, 0))

        # Draw HP bar
        max_hp = self.game.player.max_hp
        current_hp = self.game.player.hp
        hp_ratio = max(current_hp / max_hp, 0)
        pygame.draw.rect(status_panel, (255, 0, 0), (0, self.height - 20, self.portrait_size, 20))
        pygame.draw.rect(status_panel, (0, 255, 0), (0, self.height - 20, self.portrait_size * hp_ratio, 20))
        status_panel.blit(self.hp_bar, (0, self.height - 20))


        # Draw player status
        status_panel.blit(self.player_info, (self.portrait_size, 0))
        self._render_player_status(status_panel)

        # Blit to screen
        self.screen.blit(status_panel, (x, y))

    def _render_player_status(self, status_panel):
        y_offset = 30
        status_text = []
        for status_type, status in self.game.player.status().items():
            line = f"{status_type}: {status}"
            status_text.append(line)

        for line in status_text:
            text = font_small.render(line, True, BLACK)
            status_panel.blit(text, (self.height, y_offset))
            y_offset += 20        


class ChatPanel:
    def __init__(self, screen):
        self.screen = screen
        self.original_image = pygame.image.load(ResourcePath("assets/chat_panel.png").path).convert_alpha()
        self.width, self.height = SCREEN_HEIGHT // 2, SCREEN_HEIGHT * 3 // 10
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))

    def draw(self, chat_history):
        x, y = 10, SCREEN_HEIGHT * 13 // 20 + 30
        self.screen.blit(self.image, (x, y))

        # Render chat messages
        wrapped_history = []
        for message in chat_history:
            wrapped_message = WrapText(f">> {message}", font_chat, self.width - 50)
            wrapped_history.extend(wrapped_message.lines)

        y_offset = y + self.height - 40
        for message in reversed(wrapped_history[-10:]):  # Show last 10 messages
            text = font_chat.render(message, True, WHITE)
            self.screen.blit(text, (x + 30, y_offset))
            y_offset -= font_chat.get_linesize()


class InventoryPanel:
    """Draw the inventory panel, items and weapon."""
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.width, self.height = (SCREEN_WIDTH * 7 // 16) + (SCREEN_HEIGHT * -7 // 32) - 20, SCREEN_HEIGHT * 31 // 160
        self.weapon_size = self.height
        self.original_image = pygame.image.load(ResourcePath("assets/inventory_panel.png").path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))
        self.original_weapon_image = pygame.image.load(ResourcePath("assets/equipped_panel.png").path).convert_alpha()
        self.weapon_image = pygame.transform.scale(self.original_weapon_image, (self.weapon_size, self.weapon_size))
        self.inventory_group = pygame.sprite.Group()

    def draw(self):
        """Draw the inventory panel."""
        x, y = SCREEN_WIDTH - self.width - 10, SCREEN_HEIGHT * 25 // 32 + 10
        weapon_x, weapon_y = x - self.weapon_size, y

        # Blit the panel backgrounds
        self.screen.blit(self.image, (x, y))
        self.screen.blit(self.weapon_image, (weapon_x, weapon_y))

        # Draw inventory items and weapon
        self._draw_items(x, y)

    def _draw_items(self, x, y):
        """Inventory item scaling, positioning and drawing."""
        item_width = int(self.width * 0.14)
        item_height = int(self.height * 0.32)
        highlight = pygame.Surface((item_width, item_height), pygame.SRCALPHA)

        # Position offsets for rows
        start_x = x + int(self.width * 0.06)
        first_row_y = y + int(self.height * 0.13)
        second_row_y = first_row_y + item_height + int(self.height * 0.11)

        # Keep track of items to update
        updated_sprites = []

        # Scale each inventory item image before drawing
        for index, item in enumerate(list(self.game.player.inventory)[:MAX_ITEMS]):
            row = index // MAX_ITEMS_PER_ROW
            col = index % MAX_ITEMS_PER_ROW

            item_x = start_x + col * (item_width + int(self.width * 0.05))
            item_y = first_row_y if row == 0 else second_row_y

            # Check if an InventorySprite for this item already exists
            existing_sprite = next((sprite for sprite in self.inventory_group if sprite.item == item), None)

            if existing_sprite:
                existing_sprite.update_position(item_x, item_y)
                updated_sprites.append(existing_sprite)
                sprite = existing_sprite
            else:
                new_sprite = InventorySprite(item, item_x, item_y, item_width, item_height)
                self.inventory_group.add(new_sprite)
                updated_sprites.append(new_sprite)
                sprite = new_sprite

            # Highlight the item's slot if the item is equipped
            if item == self.game.player.weapon:
                highlight.fill((TRANS_YELLOW))
                self.screen.blit(highlight, sprite.rect.topleft)

                # Draw enlarged equipped item
                weapon_properties = ITEMS[item.type]
                weapon_item_size = self.weapon_size * 3 // 5
                enlarged_weapon_image = pygame.transform.scale(sprite.image, (weapon_item_size, weapon_item_size))
                weapon_item_x = x - (self.weapon_size // 2) - (weapon_item_size // 2)
                weapon_item_y = y + (self.weapon_size // 2) - (weapon_item_size // 2)
                self.screen.blit(enlarged_weapon_image, (weapon_item_x, weapon_item_y))

                # Draw equipped item label
                weapon_text = font_large.render(weapon_properties.item_type, True, ORANGE)
                weapon_text_shadow = font_large.render(weapon_properties.item_type, True, BLACK)                
                text_width = weapon_text.get_width()
                self.screen.blit(weapon_text_shadow, (weapon_item_x + (weapon_item_size // 2) - (text_width // 2) + 1, weapon_item_y + weapon_item_size + 8))                
                self.screen.blit(weapon_text, (weapon_item_x + (weapon_item_size // 2) - (text_width // 2), weapon_item_y + weapon_item_size + 7))

                # Draw currently loaded ammo
                if weapon_properties.item_function == ItemFunction.FIREARM:
                    label_x = weapon_item_x + weapon_item_size - 20
                    label_y = weapon_item_y + weapon_item_size - 20
                    pygame.draw.rect(self.screen, WHITE, (label_x, label_y, 20, 20))
                    loaded_ammo = font_large.render(str(item.loaded_ammo), True, BLACK)
                    self.screen.blit(loaded_ammo, (label_x + 5, label_y + 2))

            else:
                highlight.fill((0, 0, 0, 0))

        # Remove any sprites that are no longer in the inventory
        for sprite in list(self.inventory_group):
            if sprite not in updated_sprites:
                sprite.kill()

        # Draw the inventory group to screen
        self.inventory_group.draw(self.screen)


class DescriptionPanel:
    """Draw the description panel on the right side of the screen."""
    def __init__(self, game, screen):
        self.screen = screen
        self.game = game
        self.width = SCREEN_WIDTH - (SCREEN_HEIGHT // 2) - 20
        self.height = SCREEN_HEIGHT * 25 // 32
        self.x = SCREEN_HEIGHT // 2 + 10
        
        self.original_image = pygame.image.load(ResourcePath("assets/description_panel.png").path).convert_alpha()
        self.image = pygame.transform.scale(self.original_image, (self.width, self.height))

        self.setting_width = self.width * 5 // 6
        self.setting_height = self.setting_width * 4 // 9  # 9:4 aspect ratio
        self.setting_image_x = self.x + (self.width - self.setting_width) // 2
        self.setting_image_y = 50

        # Set up sprite elements
        self.zombie_sprite_group = pygame.sprite.Group()
        self.zombie_sprite_sheet_image = pygame.image.load(ResourcePath("assets/zombie_spritesheet.png").path).convert_alpha()
        self.zombie_sprite_sheet = SpriteSheet(self.zombie_sprite_sheet_image)

        self.human_sprite_group = pygame.sprite.Group()      
        self.human_sprite_sheet_image = pygame.image.load(ResourcePath("assets/human_spritesheet.png").path).convert_alpha()
        self.human_sprite_sheet = SpriteSheet(self.human_sprite_sheet_image)        

        # Store current description and setting image data
        self.current_description = []
        self.setting_image = None

    def draw(self):
        # Blit the panel background
        self.screen.blit(self.image, (self.x, 10))

        # Blit the setting image at the top of the panel
        self.screen.blit(self.setting_image, (self.setting_image_x, self.setting_image_y)) 

        # Draw NPC sprites
        self.zombie_sprite_group.update()
        self.human_sprite_group.update()
        self.zombie_sprite_group.draw(self.screen)
        self.human_sprite_group.draw(self.screen) 

        # Render each paragraph inside the description panel
        text_start_y = self.setting_image_y + self.setting_height + 20
        for line in self.current_description:
            text = font_large.render(line, True, BLACK)
            text_rect = text.get_rect(x=self.x + 50, y=text_start_y)  # Padding of 50px on the left
            self.screen.blit(text, text_rect)
            text_start_y += font_large.size(line)[1]  # Move down for the next line        

    def update(self):
        self._update_observations()
        self._update_npc_sprites()
        self.setting_image = self._get_setting_image()
        self.current_description = self._get_formatted_description()
        self.zombie_sprite_group.update()
        self._position_npc_sprites(self.zombie_sprite_group, 'right')
        self.human_sprite_group.update()
        self._position_npc_sprites(self.human_sprite_group, 'left')    


    def _get_setting_image(self):
        """Determine the setting image."""
        x, y = self.game.player.location
        current_block = self.game.city.block(x, y)        
        image_suffix = "inside" if self.game.player.inside else "outside"
        image_path = ResourcePath(f"assets/{current_block.type.name.lower()}_{image_suffix}.png").path

        try:
            setting_image = pygame.image.load(image_path)
        except FileNotFoundError:
            setting_image = pygame.Surface((1, 1))  # Fallback if image not found
            setting_image.fill((0, 0, 0))

        # Scale the setting image
        return pygame.transform.scale(setting_image, (self.setting_width, self.setting_height))

    def _position_npc_sprites(self, sprite_group, alignment):
        # Arrange sprite groups in a row, aligning their bottom edges
        sprite_width = 50  # Define the width for each zombie sprite
        sprite_spacing = 20  # Define the spacing between sprites

        if alignment == 'left':
            row_x = self.setting_image_x + 20
        elif alignment == 'right':
            row_x = self.setting_image_x + self.setting_width - len(self.zombie_sprite_group) * (sprite_width + sprite_spacing) - 10
        row_y = self.setting_image_y + self.setting_height  # Align with bottom edge of setting image

        for index, sprite in enumerate(sprite_group):
            # Calculate position for each sprite
            sprite.rect.midbottom = (
                row_x + index * (sprite_width + sprite_spacing) + sprite_width // 2,
                row_y
            )
       
    def _get_formatted_description(self):
        """Get the description text and wrap it to fit within the panel"""
        paragraphs = []
        for observation in self._description():
            wrapped_text = WrapText(observation, font_large, self.width - 100)  # 50px padding on each side
            for line in wrapped_text.lines:
                paragraphs.append(line)
            paragraphs.append(" ")

        return paragraphs

    def _get_current_observations(self):
        """Get the current observations based on the player's surroundings."""
        x, y = self.game.player.location
        current_block = self.game.city.block(x, y)        
        current_observations = ""

        # Inside building observations
        if self.game.player.inside:
            current_observations += f'You are standing inside {current_block.name}. '
            if not current_block.lights_on:
                current_observations += 'With the lights out, you can hardly see anything. '
            current_observations += f"The building is {current_block.barricade.get_barricade_description()}. "

            # Check if the building has been ransacked or ruined:
            if current_block.ruined:
                current_observations += "The interior has been completely ruined and needs major repairs. "
            elif current_block.ransack_level > 0:
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

        # Add observations for NPCs and dead bodies
        living_zombies, living_humans, dead_bodies = self._filter_npcs_at_player_location()

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

    def _update_observations(self):
        """Update the observations list based on the player's current state."""
        x, y = self.game.player.location
        current_block = self.game.city.block(x, y)        
        current_block.observations.clear()  # Clear existing observations
        if self.game.player.inside:
            current_block.observations.append(self._get_current_observations())
            current_block.observations.append(current_block.block_inside_desc)
        else:
            current_block.observations.append(self._get_current_observations())
            current_block.observations.append(current_block.block_outside_desc)

    def _description(self):
        """Return the current list of observations as a list."""
        x, y = self.game.player.location
        current_block = self.game.city.block(x, y)        
        self._update_observations()  # Ensure observations are current
        return current_block.observations

    def _filter_npcs_at_player_location(self):
        """Retrieve NPCs currently at the player's location and categorize them."""
        npcs_here = [
            npc for npc in self.game.npcs.list
            if npc.location == self.game.player.location and npc.inside == self.game.player.inside
        ]

        zombies_here = [npc for npc in npcs_here if not npc.is_human]
        humans_here = [npc for npc in npcs_here if npc.is_human]

        living_zombies = [z for z in zombies_here if not z.is_dead]
        living_humans = [h for h in humans_here if not h.is_dead]
        dead_bodies = [npc for npc in npcs_here if npc.is_dead]

        return living_zombies, living_humans, dead_bodies

    def _update_npc_sprites(self):
        """Update NPC sprites' visibility."""

        # Keep track of NPCs currently at the player's location
        zombies_here, humans_here, dead_npcs = self._filter_npcs_at_player_location()

        # Update existing sprites or create new ones if necessary
        updated_sprites = []

        for zombie in zombies_here:
            # Check if a sprite for this zombie already exists
            existing_sprite = next(
                (sprite for sprite in self.zombie_sprite_group if sprite.npc == zombie), None
            )
            if existing_sprite:
                updated_sprites.append(existing_sprite)
            else:
                # Create a new sprite for the zombie
                new_sprite = NPCSprite(
                    self.screen, zombie, self.zombie_sprite_sheet, 8, 44, 54, 2.5, (0, 0, 0)
                )
                self.zombie_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)

        # Remove sprites for zombies that are no longer here
        for sprite in list(self.zombie_sprite_group):
            if sprite not in updated_sprites or sprite.npc in dead_npcs:
                sprite.kill()

        for human in humans_here:
            # Check if a sprite for this human already exists
            existing_sprite = next(
                (sprite for sprite in self.human_sprite_group if sprite.npc == human), None
            )
            if existing_sprite:
                updated_sprites.append(existing_sprite)
            else:
                # Create a new sprite for the human
                new_sprite = NPCSprite(
                    self.screen, human, self.human_sprite_sheet, 8, 44, 64, 2.5, (0, 0, 0)
                )
                self.human_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)                

        # Remove sprites for humans that are no longer here
        for sprite in list(self.human_sprite_group):
            if sprite not in updated_sprites or sprite.npc in dead_npcs:
                sprite.kill()

class InventorySprite(pygame.sprite.Sprite):
    """An item sprite for the inventory panel."""
    def __init__(self, item, x, y, width, height):
        super().__init__()
        self.item = item  # Reference to the actual item object
        self.image = pygame.image.load(item.image_file).convert_alpha()  # Load item image
        self.image = pygame.transform.scale(self.image, (width, height))  # Scale to fit inventory
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_position(self, x, y):
        """Update sprite position when inventory layout changes."""
        self.rect.topleft = (x, y)    

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
        max_hp = self.npc.max_hp
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


class Map:
    def __init__(self, screen, player):
        self.screen = screen
        self.player = player
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
        label_text = WrapText(label_name, font_xs, self.block_size - 2)
        text_height = sum(font_xs.size(line)[1] for line in label_text.lines)

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