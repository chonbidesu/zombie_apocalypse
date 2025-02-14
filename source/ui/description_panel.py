# description_panel.py

import random

from settings import *
from ui.utils import WrapText, SpriteSheet
from data import BLOCKS, BlockType, SkillType, OCCUPATIONS
from ui.widgets import ClockHUD


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
        self._create_sprite_elements()  

        # Store current description and setting image data
        self.current_description = []
        self.setting_image = None

        # Set up Clock HUD
        self.clock = ClockHUD(self.game)        

    def draw(self):
        # Blit the panel background
        self.screen.blit(self.image, (self.x, 10))

        # Blit the setting image at the top of the panel
        self.screen.blit(self.setting_image, (self.setting_image_x, self.setting_image_y)) 

        # Draw the Clock HUD
        self.clock_x = self.setting_image_x + 5
        self.clock_y = self.setting_image_y + 5
        self.clock.draw(self.screen, self.clock_x, self.clock_y)

        # Draw NPC sprites
        self.zombie_sprite_group.update(self.game)
        self.human_sprite_group.update(self.game)
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
        self.clock.update()
        self.setting_image = self._get_setting_image()
        self.current_description = self._get_formatted_description()
        self.zombie_sprite_group.update(self.game)
        self._position_npc_sprites(self.zombie_sprite_group, 'right')
        self.human_sprite_group.update(self.game)
        self._position_npc_sprites(self.human_sprite_group, 'left')    

    def _create_sprite_elements(self):
        self.zombie_sprite_group = pygame.sprite.Group()
        self.zombie_sprite_sheet_image = pygame.image.load(ResourcePath("assets/sprite_sheets/zombie_sprite_sheet.png").path).convert_alpha()
        self.zombie_sprite_sheet = SpriteSheet(self.zombie_sprite_sheet_image)

        self.human_sprite_group = pygame.sprite.Group()      
        self.consumer_sprite_sheet_image = pygame.image.load(ResourcePath("assets/sprite_sheets/consumer_sprite_sheet.png").path).convert_alpha()
        self.consumer_sprite_sheet = SpriteSheet(self.consumer_sprite_sheet_image)
        self.civilian_sprite_sheet_image = pygame.image.load(ResourcePath("assets/sprite_sheets/civilian_sprite_sheet.png").path).convert_alpha()
        self.civilian_sprite_sheet = SpriteSheet(self.civilian_sprite_sheet_image)
        self.military_sprite_sheet_image = pygame.image.load(ResourcePath("assets/sprite_sheets/military_sprite_sheet.png").path).convert_alpha()
        self.military_sprite_sheet = SpriteSheet(self.military_sprite_sheet_image)
        self.science_sprite_sheet_image = pygame.image.load(ResourcePath("assets/sprite_sheets/science_sprite_sheet.png").path).convert_alpha()
        self.science_sprite_sheet = SpriteSheet(self.science_sprite_sheet_image)                             

    def _get_setting_image(self):
        """Determine the setting image."""
        x, y = self.game.state.player.location
        current_block = self.game.state.city.block(x, y)        
        image_suffix = "inside" if self.game.state.player.inside else "outside"
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
        player = self.game.state.player
        x, y = player.location
        current_block = self.game.state.city.block(x, y)        
        current_observations = ""

        # Inside building observations
        if player.inside:
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
            if current_block.type == BlockType.NECROTECH_LAB and SkillType.NECROTECH_EMPLOYMENT not in player.human_skills:
                properties = BLOCKS[BlockType.OFFICE]
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
        block_characters = player.state.filter_characters_at_location(x, y, player.inside, include_player=False)

        if block_characters.living_zombies:
            if len(block_characters.living_zombies) == 1:
                current_observations += "There is a lone zombie here. "
            else:
                current_observations += f"There are {len(block_characters.living_zombies)} zombies here. "

        if block_characters.living_humans:
            if len(block_characters.living_humans) == 1:
                current_observations += "There is another survivor here. "
            else:
                current_observations += f"There are {len(block_characters.living_humans)} other survivors here. "

        if block_characters.dead_bodies:
            if len(block_characters.dead_bodies) == 1:
                current_observations += "You see a dead body. "
            else:
                current_observations += f"You see {len(block_characters.dead_bodies)} dead bodies. "
            for body in block_characters.dead_bodies:
                print(f"{body.current_name} has {body.ap} AP.")

        return current_observations

    def _update_observations(self):
        """Update the observations list based on the player's current state."""
        player = self.game.state.player
        x, y = player.location
        current_block = self.game.state.city.block(x, y)        
        current_block.observations.clear()  # Clear existing observations
        if self.game.state.player.inside:
            current_block.observations.append(self._get_current_observations())
            current_block.observations.append(current_block.block_inside_desc)
        else:
            current_block.observations.append(self._get_current_observations())
            current_block.observations.append(current_block.block_outside_desc)

    def _description(self):
        """Return the current list of observations as a list."""
        player = self.game.state.player
        x, y = player.location
        current_block = self.game.state.city.block(x, y)        
        self._update_observations()  # Ensure observations are current
        return current_block.observations

    def _update_npc_sprites(self):
        """Update NPC sprites' visibility."""
        player = self.game.state.player
        x, y = player.location        

        # Keep track of NPCs currently at the player's location
        block_characters = player.state.filter_characters_at_location(x, y, player.inside, include_player=False)

        # Update existing sprites or create new ones if necessary
        updated_sprites = []

        for zombie in block_characters.living_zombies:
            # Check if a sprite for this zombie already exists
            existing_sprite = next(
                (sprite for sprite in self.zombie_sprite_group if sprite.npc == zombie), None
            )
            if existing_sprite:
                updated_sprites.append(existing_sprite)
            else:
                # Create a new sprite for the zombie
                new_sprite = NPCSprite(
                    self.screen, zombie, self.zombie_sprite_sheet, 2.5, (0, 0, 0)
                )
                self.zombie_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)

        # Remove sprites for zombies that are no longer here
        for sprite in list(self.zombie_sprite_group):
            if sprite not in updated_sprites:
                sprite.kill()

        for human in block_characters.living_humans:
            # Check if a sprite for this human already exists
            existing_sprite = next(
                (sprite for sprite in self.human_sprite_group if sprite.npc == human), None
            )
            if existing_sprite:
                updated_sprites.append(existing_sprite)
            else:
                # Create a new sprite for the human
                occupation = human.occupation
                sprite_sheet_name = OCCUPATIONS[occupation].sprite_sheet
                sprite_sheet = getattr(self, sprite_sheet_name)

                new_sprite = NPCSprite(
                    self.screen, human, sprite_sheet, 2.5, (0, 0, 0)
                )
                self.human_sprite_group.add(new_sprite)
                updated_sprites.append(new_sprite)                

        # Remove sprites for humans that are no longer here
        for sprite in list(self.human_sprite_group):
            if sprite not in updated_sprites:
                sprite.kill()  


class NPCSprite(pygame.sprite.Sprite):
    """An NPC sprite for the description panel."""
    def __init__(self, screen, npc, sprite_sheet, scale, colour):
        super().__init__()
        self.screen = screen
        self.npc = npc  # Reference to the parent NPC
        self.sprite_sheet = sprite_sheet
        self.frame_count = [8, 7, 6, 3]  # Total number of frames
        self.action = 0
        self.frame_width = 64  # Width of each frame
        self.frame_height = 64  # Height of each frame
        self.scale = scale  # Scale factor for the frames
        self.colour = colour  # Transparent color for the frames
        self.animation_speed = 0.15  # Animation speed (seconds per frame)
        self.last_update_time = pygame.time.get_ticks()  # Time since the last frame update
        self.hp_bar_height = 10
        self.play_once = False # For one-time animations

        # Calculate starting frames for each action
        self.action_start_frames = [
            0,  # Action 0 (Idle)
            self.frame_count[0],  # Action 1 (Attack)
            self.frame_count[0] + self.frame_count[1],  # Action 2 (Die)
            self.frame_count[0] + self.frame_count[1] + self.frame_count[2],  # Action 3 (Hurt)
        ]
        self.current_frame = self.action_start_frames[self.action] + random.randint(0, self.frame_count[0] - 1)

        # Set the initial image and rect
        self.image = self.sprite_sheet.get_image(
            frame=self.current_frame,
            width=self.frame_width,
            height=self.frame_height,
            scale=self.scale,
            colour=self.colour,
        )
        self.rect = self.image.get_rect()


    def _get_current_frame(self):
        """Retrieve the correct frame from the sprite sheet."""
        start_frame = self.action_start_frames[self.action]
        return self.sprite_sheet.get_image(
            frame=start_frame + self.current_frame,
            width=self.frame_width,
            height=self.frame_height,
            scale=self.scale,
            colour=self.colour,
        )

    def set_action(self, action):
        """
        Set the NPC action. If switching from idle (0), reset animation.
        """
        if self.action == 0 and action > 0:  # Switching from idle to action
            self.current_frame = 0
            self.play_once = True  # Ensure action plays fully
        
        self.action = action  # Update action

    def draw_name(self):
        """Draw the NPC's name above the sprite."""
        name = self.npc.current_name
        name_text = font_xs.render(name, True, BLACK)
        name_y = self.rect.y + self.rect.height
        name_rect = name_text.get_rect(centerx=self.rect.centerx, y=name_y)
        self.screen.blit(name_text, name_rect)

    def draw_hp_bar(self):
        """Draw the NPC's HP bar if the player has the necessary skill."""
        max_hp = self.npc.max_hp
        current_hp = self.npc.hp
        bar_width = self.rect.width - 50
        hp_ratio = max(current_hp / max_hp, 0)

        bar_x = self.rect.x + 25
        bar_y = self.rect.y + self.rect.height + 15
    
        pygame.draw.rect(self.screen, (255, 0, 0), (bar_x, bar_y, bar_width, self.hp_bar_height))
        pygame.draw.rect(self.screen, (0, 255, 0), (bar_x, bar_y, bar_width * hp_ratio, self.hp_bar_height))

    def draw_hp_status(self):
        """Draw the NPC's health status if the player has the necessary skill."""
        current_hp = self.npc.hp

        # Determine status text
        if current_hp < 13:
            status_text = "Dying"
            colour = (255, 0, 0)
        elif current_hp < 25:
            status_text = "Wounded"
            colour = ORANGE
        else:
            return
        
        text_surface = font_xs.render(status_text, True, colour)
        text_x = self.rect.centerx - (text_surface.get_width() // 2)
        text_y = self.rect.y - 15

        self.screen.blit(text_surface, (text_x, text_y))

    def update(self, game):
        """Update the sprite's animation frame."""
        now = pygame.time.get_ticks()
        if now - self.last_update_time > self.animation_speed * 1000:  # Convert to milliseconds
            self.last_update_time = now
            self.current_frame += 1

            # Get max frames for the current action
            max_frames = self.frame_count[self.action]

            # If the animation is complete for actions 1-3, return to idle (0)
            if self.current_frame >= max_frames:
                if self.action == 2:
                    self.kill()
                elif self.play_once:
                    self.action = 0
                    self.current_frame = self.action_start_frames[self.action]
                    self.play_once = False
                else:
                    self.current_frame = 0 # Loop if it's an idle animation

            # Update the image with the new frame
            self.image = self._get_current_frame()

        # Draw UI elements
        self.draw_name()

        if game.state.player.is_human and SkillType.DIAGNOSIS in game.state.player.human_skills:
            self.draw_hp_bar()
        elif not game.state.player.is_human and SkillType.SCENT_BLOOD in game.state.player.zombie_skills:
            self.draw_hp_bar()
        elif not game.state.player.is_human and SkillType.SCENT_FEAR in game.state.player.zombie_skills:
            self.draw_hp_status()
