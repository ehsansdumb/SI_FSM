# spaceship_game_with_fsm.py

import pygame
import random
import math
from pygame import mixer
from fsm import FSM

# initializing pygame
pygame.init()

# creating screen
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# caption and icon
pygame.display.set_caption("Welcome to Space Invaders Game by:- styles")

# Score variables
score_val = 0  # The player's current score
scoreX = 5  # X-coordinate for score display
scoreY = 5  # Y-coordinate for score display
font = pygame.font.Font('freesansbold.ttf', 20)  # Font for score

# Game Over font
game_over_font = pygame.font.Font('freesansbold.ttf', 64)

def show_score(x, y):
    """Displays the player's current score on the screen."""
    score = font.render("Points: " + str(score_val), True, (255, 255, 255))
    screen.blit(score, (x, y))

def game_over():
    """Displays the 'GAME OVER' message when the player loses."""
    game_over_text = game_over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(game_over_text, (190, 250))

# Background sound setup
mixer.music.load('background.mp3')  # Load background music
mixer.music.play(-1)  # Play background music in a loop

# Player setup
playerImage = pygame.transform.scale(pygame.image.load('spaceship.png'), (50, 50))  # Load and scale player sprite
player_X = 370  # Initial X position of the player
player_Y = 523  # Fixed Y position of the player
player_Xchange = 0  # Change in X position per frame

# Invader setup
invaderImage = []  # List of invader sprites
invader_X = []  # X positions of invaders
invader_Y = []  # Y positions of invaders
invader_Xchange = []  # Change in X positions per frame
invader_Ychange = []  # Change in Y positions after boundary collision
invaderFSM = []  # FSM objects for invaders
invader_bullets = []  # List to store bullets fired by invaders
invader_fire_timers = []  # Cooldown timers for invader bullets
no_of_invaders = 8  # Number of invaders
invaders_shooting = 0  # Number of invaders allowed to shoot initially

# Initialize invaders
for num in range(no_of_invaders):
    invaderImage.append(pygame.transform.scale(pygame.image.load('alien.png'), (40, 40)))
    invader_X.append(random.randint(64, 737))  # Random initial X position
    invader_Y.append(random.randint(30, 180))  # Random initial Y position
    invader_Xchange.append(0.5)  # Initial horizontal speed
    invader_Ychange.append(30)  # Vertical shift on boundary hit
    invaderFSM.append(FSM("Patrolling"))  # Start invaders in "Patrolling" state
    invader_bullets.append({"x": 0, "y": 0, "state": "rest"})  # Initialize invader bullet state
    invader_fire_timers.append(0)  # Initialize cooldown timers for firing

# Bullet setup (player)
bulletImage = pygame.transform.scale(pygame.image.load('bullet.png'), (10, 20))  # Load and scale bullet sprite
bullet_X = 0  # Initial X position of the bullet
bullet_Y = 500  # Initial Y position of the bullet
bullet_Xchange = 0  # No horizontal change for the bullet
bullet_Ychange = 3  # Bullet speed
bullet_state = "rest"  # Initial state of the bullet ("rest" or "fire")

# Invader bullet setup
invader_bullet_image = pygame.transform.scale(pygame.image.load('enemy_bullet.png'), (10, 20))  # Load and scale invader bullet sprite
invader_bullet_speed = 0.4  # Slower speed for invader bullets

# Collision detection
def isCollision(x1, x2, y1, y2):
    """Checks if two objects (e.g., bullet and invader) are colliding."""
    distance = math.sqrt((math.pow(x1 - x2, 2)) + (math.pow(y1 - y2, 2)))
    return distance <= 50

def player(x, y):
    """Draws the player sprite at the given (x, y) coordinates."""
    screen.blit(playerImage, (x - 16, y + 10))

def invader(x, y, i):
    """Draws the invader sprite for a specific invader at (x, y)."""
    screen.blit(invaderImage[i], (x, y))

def bullet(x, y):
    """Fires a bullet from the player's current position."""
    global bullet_state
    screen.blit(bulletImage, (x, y))
    bullet_state = "fire"

def fire_invader_bullet(x, y):
    """Fires a bullet from the invader's position."""
    screen.blit(invader_bullet_image, (x, y))

# Main game loop
running = True

while running:

    # Fill the screen with black (background)
    screen.fill((0, 0, 0))

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Handle player input for movement and shooting
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                player_Xchange = -1.7  # Move left
            if event.key == pygame.K_RIGHT:
                player_Xchange = 1.7  # Move right
            if event.key == pygame.K_SPACE:
                if bullet_state == "rest":
                    bullet_X = player_X  # Align bullet with player's position
                    bullet(bullet_X, bullet_Y)
                    bullet_sound = mixer.Sound('bullet.wav')
                    bullet_sound.play()
        if event.type == pygame.KEYUP:
            player_Xchange = 0  # Stop movement when key is released

    # Update player position
    player_X += player_Xchange
    player_X = max(16, min(player_X, 750))  # Restrict movement within screen bounds

    # Update bullet position
    if bullet_Y <= 0:
        bullet_Y = 600
        bullet_state = "rest"
    if bullet_state == "fire":
        bullet(bullet_X, bullet_Y)
        bullet_Y -= bullet_Ychange

    # Update invader positions and states
    for i in range(no_of_invaders):

        # Check if invader reaches the player
        if invader_Y[i] >= 450:
            if abs(player_X - invader_X[i]) < 80:
                for j in range(no_of_invaders):
                    invader_Y[j] = 2000  # Move all invaders off-screen
                    explosion_sound = mixer.Sound('explosion.wav')
                    explosion_sound.play()
                game_over()
                break

        # Handle FSM states for each invader
        if invaderFSM[i].state == "Patrolling":
            invader_X[i] += invader_Xchange[i]  # Move horizontally
            if invader_X[i] >= 735 or invader_X[i] <= 0:
                invader_Xchange[i] *= -1  # Reverse direction on screen edge
                invader_Y[i] += invader_Ychange[i]  # Move down
            if random.random() < 0.02 and i < invaders_shooting:  # Limit attackers at start
                invaderFSM[i].change_state("Attacking")

        elif invaderFSM[i].state == "Attacking":
            # Handle attacking behavior (firing projectiles)
            if invader_bullets[i]["state"] == "rest" and invader_fire_timers[i] <= 0:
                invader_bullets[i]["x"] = invader_X[i]
                invader_bullets[i]["y"] = invader_Y[i]
                invader_bullets[i]["state"] = "fire"
                invader_fire_timers[i] = 100  # Set cooldown timer
            if random.random() < 0.1:  # Random chance to return to patrolling
                invaderFSM[i].change_state("Patrolling")

        # Decrease cooldown timer
        if invader_fire_timers[i] > 0:
            invader_fire_timers[i] -= 1

        # Check for collisions
        collision = isCollision(bullet_X, invader_X[i], bullet_Y, invader_Y[i])
        if collision:
            score_val += 1  # Increment score
            bullet_Y = 600
            bullet_state = "rest"  # Reset bullet state
            invader_X[i] = random.randint(64, 736)  # Respawn invader
            invader_Y[i] = random.randint(30, 200)
            invaderFSM[i].change_state("Patrolling")  # Reset state

        # Draw the invader
        invader(invader_X[i], invader_Y[i], i)

        # Update invader bullet position
        if invader_bullets[i]["state"] == "fire":
            fire_invader_bullet(invader_bullets[i]["x"], invader_bullets[i]["y"])
            invader_bullets[i]["y"] += invader_bullet_speed  # Move bullet downward
            if invader_bullets[i]["y"] >= 600:  # Reset if bullet leaves screen
                invader_bullets[i]["state"] = "rest"

        # Check if invader bullet hits the player
        if invader_bullets[i]["state"] == "fire" and isCollision(invader_bullets[i]["x"], player_X, invader_bullets[i]["y"], player_Y):
            for j in range(no_of_invaders):
                invader_Y[j] = 2000  # Move all invaders off-screen
            explosion_sound = mixer.Sound('explosion.wav')
            explosion_sound.play()
            game_over()
            running = False

    # Gradually increase the number of shooting invaders based on score
    if score_val >= invaders_shooting * 10:  # Increase every 10 points
        invaders_shooting = min(invaders_shooting + 1, no_of_invaders)

    # Draw the player and score
    player(player_X, player_Y)
    show_score(scoreX, scoreY)

    # Update the display
    pygame.display.update()
