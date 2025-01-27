import pygame
from settings import *

class Viewport:
    def __init__(self, game, screen):
        self.game = game
        self.screen = screen
        self.frame = pygame.image.load('assets/viewport_frame.png').convert_alpha()

    def draw(self):
        scaled_viewport_frame = pygame.transform.scale(self.frame, (SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(scaled_viewport_frame, (10, 10))

class ViewportNPC:
    """Handles drawing NPCs inside the viewport."""
    def __init__(self, npc, index, total_npcs, row=0):
        self.npc = npc
        self.size = BLOCK_SIZE // 6  
        
        # Adjust positions based on row (row=0 for zombies, row=1 for humans)
        col = index % 3  
        x = (BLOCK_SIZE // 2) - ((total_npcs - 1) * (self.size + 2)) // 2 + col * (self.size + 2)
        y = (BLOCK_SIZE // 2) + row * (self.size + 2)

        self.position = (x, y)
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.image.fill((255, 0, 0) if not npc.is_human else (128, 128, 128))  # Red for zombies, gray for humans
