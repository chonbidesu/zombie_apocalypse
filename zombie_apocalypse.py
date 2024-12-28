import pygame
import random
from player import Player
from items import *
from settings import *

# Initialize pygame
pygame.init()

# Set up screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Post-Apocalyptic Survival Game")

# Fonts
font = pygame.font.SysFont("Arial", FONT_SIZE)

# Player Setup
player = Player(human_name="John Doe", zombie_name="Rotten John", gender="Male", age=30, occupation="Soldier", x=50, y=50)

# Chat setup
chat_messages = ["Welcome to the game!"]

# Create some sample items for the player to collect
first_aid_kit = FirstAidKit()
player.add_item(first_aid_kit)

# Game loop flag
running = True
clock = pygame.time.Clock()

def draw_grid():
    """Draws the 9x9 viewport grid on the screen."""
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            rect = pygame.Rect(i * TILE_SIZE, j * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(screen, WHITE, rect, 1)  # Draw grid tile borders

def draw_player():
    """Draw the player at their location."""
    player_rect = pygame.Rect(player.location[0] * TILE_SIZE, player.location[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, GREEN, player_rect)

def draw_chat():
    """Draws the chat area on the screen."""
    chat_rect = pygame.Rect(0, SCREEN_HEIGHT - CHAT_HEIGHT, SCREEN_WIDTH, CHAT_HEIGHT)
    pygame.draw.rect(screen, GRAY, chat_rect)
    
    # Display chat messages
    for i, message in enumerate(chat_messages[-CHAT_LINES:]):
        chat_surface = font.render(message, True, WHITE)
        screen.blit(chat_surface, (10, SCREEN_HEIGHT - CHAT_HEIGHT + (i * FONT_SIZE)))

def handle_player_input():
    """Handles the player's keyboard input."""
    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        player.move(-1, 0)
    elif keys[pygame.K_RIGHT]:
        player.move(1, 0)
    elif keys[pygame.K_UP]:
        player.move(0, -1)
    elif keys[pygame.K_DOWN]:
        player.move(0, 1)

    # Simulate using an item (e.g., First Aid Kit)
    if keys[pygame.K_SPACE]:
        if first_aid_kit in player.inventory:
            chat_messages.append("You used the First Aid Kit.")
            player.remove_item(first_aid_kit)

def game_loop():
    """Main game loop."""
    global running

    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle player input
        handle_player_input()

        # Update game state
        # (Here we can handle things like NPC movements, health regeneration, etc.)

        # Clear the screen
        screen.fill(BLACK)

        # Draw grid and player
        draw_grid()
        draw_player()

        # Draw chat
        draw_chat()

        # Update the screen
        pygame.display.flip()

        # Frame rate control
        clock.tick(FPS)

# Run the game
game_loop()

# Quit pygame
pygame.quit()
