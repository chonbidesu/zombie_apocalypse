# description_panel.py

import random

from settings import *
from ui.utils import WrapText, SpriteSheet
from data import BLOCKS


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

    def draw_name(self):
        """Draw the NPC's name above the sprite."""
        name = self.npc.current_name
        name_text = font_xs.render(name, True, BLACK)
        name_y = self.rect.y + self.rect.height
        name_rect = name_text.get_rect(centerx=self.rect.centerx, y=name_y)
        self.screen.blit(name_text, name_rect)

    def draw_hp_bar(self):
        max_hp = self.npc.max_hp
        current_hp = self.npc.hp
        bar_width = self.rect.width - 50
        hp_ratio = max(current_hp / max_hp, 0)

        bar_x = self.rect.x + 25
        bar_y = self.rect.y + self.rect.height + 15
    
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
        self.draw_name()
        self.draw_hp_bar()