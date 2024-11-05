import pygame
from random import randint
from os.path import join

# General setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
clock = pygame.time.Clock()

# Loaded assets
player_direction = pygame.math.Vector2()
player_speed = 800
player_surf = pygame.image.load('images/player.png')
player_rect = player_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
player_star = pygame.image.load('images/star.png')
player_meteor = pygame.image.load('images/meteor.png')
laser_surf = pygame.image.load('images/laser.png')
laser_speed = 1000
meteor_speed = 600

# Load sounds
laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.play(-1)  # Play the game music in a loop

# Font for score display
font = pygame.font.Font(None, 36)

# Initializing game variables
score = 0
game_over = False
collision_threshold = 50  # A distance threshold for collisions

def reset_game():
    # Reset the game variables to start a new game.
    global score, game_over, lasers, meteors, player_rect
    score = 0
    game_over = False
    lasers.clear()
    meteors.clear()
    player_rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50)
    game_music.stop()  # Stopping the music before restarting
    game_music.play(-1)  # Restarting the game music

# Star positions
star_position = [(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)) for _ in range(40)]

# Lists to store active lasers and meteors
lasers = []
meteors = []

# Custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 900)  # Spawn a meteor every 0.9 seconds

while True:
    dt = clock.tick() / 1000

    # Event loop
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()  # Exit the game
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                # Creating a new laser rect at the player's position and add to lasers list
                new_laser_rect = laser_surf.get_rect(midbottom=player_rect.midtop)
                lasers.append(new_laser_rect)
                laser_sound.play()  # Playing laser sound when firing a laser
            elif event.key == pygame.K_r and game_over:
                reset_game()  # Restarting the game if 'R' is pressed
                game_music.play(-1)  # Restarting the game music

        if event.type == meteor_event and not game_over:
            for _ in range(4):  # Spawning 4 meteors at a time
                new_meteor_rect = player_meteor.get_rect(midtop=(randint(0, WINDOW_WIDTH), 0))
                meteors.append(new_meteor_rect)

    if not game_over:
        # Player input for movement
        keys = pygame.key.get_pressed()
        player_direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        player_direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        player_rect.center += player_direction * player_speed * dt

        # Restricting the player to stay within the screen
        player_rect.clamp_ip(display_surface.get_rect())

        # Update laser positions and remove off-screen lasers
        for laser in lasers[:]:
            laser.y -= laser_speed * dt
            if laser.bottom < 0:
                lasers.remove(laser)

        # Update meteor positions and remove off-screen meteors
        for meteor in meteors[:]:
            meteor.y += meteor_speed * dt
            if meteor.top > WINDOW_HEIGHT:
                meteors.remove(meteor)

        # Checking for collisions between lasers and meteors
        for laser in lasers[:]:
            for meteor in meteors[:]:
                if laser.colliderect(meteor):
                    lasers.remove(laser)
                    meteors.remove(meteor)
                    score += 1  # Increment score when a meteor is hit
                    explosion_sound.play()  # Playing explosion sound on hit
                    break  # Stop checking this laser once it collides

        # Checking for collisions between player and meteors using the threshold
        for meteor in meteors:
            if (player_rect.centerx - meteor.centerx) ** 2 + (player_rect.centery - meteor.centery) ** 2 < collision_threshold ** 2:
                explosion_sound.play()  # Play explosion sound on player hit
                game_over = True  # Set game over flag if player is too close to a meteor
                break

    # Draw game elements
    display_surface.fill('gray38')

    # Display stars
    for pos in star_position:
        display_surface.blit(player_star, pos)
    
    # Display meteors
    for meteor in meteors:
        display_surface.blit(player_meteor, meteor)

    # Display player and lasers
    display_surface.blit(player_surf, player_rect.topleft)
    for laser in lasers:
        display_surface.blit(laser_surf, laser)

    # Display score in the top-right corner
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    display_surface.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, 10))

    # Display restart message if game is over
    if game_over:
        restart_text = font.render('Game Over! Press R to Restart', True, (255, 0, 0))
        display_surface.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2))

    pygame.display.update()

pygame.quit()
