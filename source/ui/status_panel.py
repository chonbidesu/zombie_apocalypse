# status_panel.py

from settings import *
from ui.utils import SpriteSheet
from ui.widgets import Button
from data import ResourcePath


class StatusPanel:
    """Display player portrait, HP and other status information."""
    def __init__(self, game, screen, portrait):
        self.game = game
        self.screen = screen
        self.portrait_path = portrait
        self.x, self.y = SCREEN_WIDTH // 3 + 10, SCREEN_HEIGHT * 25 // 32 + 10
        self.width, self.height = SCREEN_WIDTH // 4 - 10, SCREEN_HEIGHT * 31 // 160
        self.portrait_size = self.height - 20
        self.hp_bar = pygame.image.load(ResourcePath("panels/hp_bar.png").path).convert_alpha()
        self.hp_bar = pygame.transform.scale(self.hp_bar, (self.portrait_size, 20))
        self.portrait_frame = pygame.image.load(ResourcePath("panels/player_frame.png").path).convert_alpha()
        self.portrait_frame = pygame.transform.scale(self.portrait_frame, (self.portrait_size, self.portrait_size))
        self.player_sprite_sheet_image = pygame.image.load(ResourcePath(self.portrait_path).path).convert_alpha()
        self.player_info = pygame.image.load(ResourcePath("panels/player_info.png").path).convert_alpha()
        self.player_info = pygame.transform.scale(self.player_info, (self.width - self.height + 20, self.height))

        # Set up player portrait
        self.player_portrait_scale = (SCREEN_HEIGHT * 31 // 160 - 20) // 66
        self.player_sprite_sheet = SpriteSheet(self.player_sprite_sheet_image)
        self.player_sprite = PlayerSprite(
            self.screen, self.game.state.player, self.player_sprite_sheet, 6, 66, 66, self.player_portrait_scale, self.x, self.y
        )
        self.player_sprite_group = pygame.sprite.GroupSingle()
        self.player_sprite_group.add(self.player_sprite)
        self.skills_button = Button('skills', (self.width - self.height) // 2, 25)
        self.skills_button.update(self.x + (self.width + self.portrait_size) // 2 - (self.width - self.height) // 4, self.y + self.height - 35)
        self.button_group = pygame.sprite.GroupSingle()
        self.button_group.add(self.skills_button)

    def draw(self):
        # Draw player portrait
        self.player_sprite_group.update()
        self.player_sprite_group.draw(self.screen)
        self.screen.blit(self.portrait_frame, (self.x, self.y))

        # Draw HP bar
        max_hp = self.game.state.player.max_hp
        current_hp = self.game.state.player.hp
        hp_ratio = max(current_hp / max_hp, 0)
        hp_bar_x, hp_bar_y = self.x, self.y + self.height - 20
        pygame.draw.rect(self.screen, RED, (hp_bar_x, hp_bar_y, self.portrait_size, 20))
        pygame.draw.rect(self.screen, GREEN, (hp_bar_x, hp_bar_y, self.portrait_size * hp_ratio, 20))
        self.screen.blit(self.hp_bar, (hp_bar_x, hp_bar_y))

        # Draw player status
        self.screen.blit(self.player_info, (self.x + self.portrait_size, self.y))
        self._render_player_status()
        self.button_group.draw(self.screen)

    def _render_player_status(self):
        y_offset = 30
        status_text = []

        for status_type, status in self.game.state.player.status().items():
            if status_type == 'Occupation':
                line = status
            else:
                line = f"{status_type}: {status}"
            status_text.append(line)

        for line in status_text:
            text = font_small.render(line, True, BLACK)
            self.screen.blit(text, (self.x + self.height, self.y + y_offset))
            y_offset += 20        

class PlayerSprite(pygame.sprite.Sprite):
    """A player sprite for the status panel."""
    def __init__(self, screen, player, sprite_sheet, frame_count, frame_width, frame_height, scale, x, y):
        super().__init__()
        self.screen = screen
        self.player = player
        self.sprite_sheet = sprite_sheet
        self.frame_count = frame_count
        self.frame_height = frame_height
        self.frame_width = frame_width
        self.scale = scale
        self.colour = (0, 0, 0)
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
        self.rect = self.image.get_rect(topleft=(x, y))

    def update_animation_set(self):
        """Update the animation frame range based on player's HP."""
        previous_start_frame = self.start_frame

        if self.player.hp > self.player.max_hp * 0.7:
            self.start_frame = 0  # Normal animation
        elif self.player.hp > self.player.max_hp * 0.3:
            self.start_frame = self.frame_count  # Use the second set of frames
        else:
            self.start_frame = self.frame_count * 2  # Use the third set of frames

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