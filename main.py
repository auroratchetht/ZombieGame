# Register imports
import pygame, config, sys, math, random
from entity import Player, Bullet, Enemy, Coin
from waves import Wave



#------------Initialization------------

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Create and start enemy spawn event
spawn_enemy_event = config.ENEMY_EVENT
pygame.time.set_timer(spawn_enemy_event, 1000) # Start enemy spawn event after 1 second

# Initialize screen
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.SCALED | pygame.RESIZABLE) # Create game window
clock = pygame.time.Clock()
background_image = pygame.image.load("img/bg.png")
background_image = pygame.transform.scale(background_image, (500, 500))

# Register base text settings
font = pygame.font.Font(None, 16)

# Define variables
frame = 0
wave = Wave()
player = Player()
fire_cooldown = 0
bullet_count = 0 # Andrew: New variable
bullets = []
enemies = []
coins = []
kills = 0
end_round_timer = 4
frames_since_death = 0

# Define game states
running = True
game_state = "start" # Game States: start, game, paused, intermission, end
current_game_state = "start"
debug_menu = False
fullscreen = False

# Start Menu variables
sm_font_large = pygame.font.SysFont('courier', 24, bold=True)
sm_font_small = pygame.font.SysFont('courier', 16, bold=True)

sm_start_button_text = sm_font_large.render("START GAME", True, config.WHITE)
sm_exit_button_text = sm_font_large.render("EXIT", True, config.WHITE)
prompt_text = sm_font_small.render("Select Mode with 1, 2 or Click", True, config.WHITE)

sm_start_button_rect = sm_start_button_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 50))
sm_exit_button_rect = sm_exit_button_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 + 50))

# End Screen variables
font_big = pygame.font.SysFont("courier", 36, bold=True)
font_small = pygame.font.SysFont("courier", 18, bold=True)

dots = [(random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT), random.randint(2, 6)) for _ in range(150)]

splatters = [(random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT)) for _ in range(15)]

shade_surf = pygame.Surface((config.WIDTH, config.HEIGHT))
shade_surf.fill(color = config.BLACK)
shade_surf_lite = shade_surf
shade_surf_lite_lite = shade_surf
shade_surf.set_alpha(75)
shade_surf_lite.set_alpha(10)
shade_surf_lite_lite.set_alpha(7)


#------------FUNCTIONS------------

# Find the angle of mouse cursor relative to player for bullet path calculation
def get_angle_to_mouse(player_pos, mouse_pos):
    # Calculates the angle in radians from the player to the mouse.
    player_x, player_y = player_pos
    mouse_x, mouse_y = mouse_pos
    diff_x = mouse_x - player_x
    diff_y = mouse_y - player_y
    return math.atan2(diff_y, diff_x) # Return the arc tangent of y/x in radians

# Determines the direction of player shooting for shooting animation
# Andrew: Changed some of these to inequalities bc it was buggy at those specific values
def shooting_direction(angle):
    current_angle = math.degrees(angle)
    character_facing = "down"
    if -22.5 <= current_angle < 22.5:
        character_facing = "right"
    elif 22.5 <= current_angle < 67.5:
        character_facing = "down-right"
    elif 67.5 <= current_angle < 112.5:
        character_facing = "down"
    elif 112.5 <= current_angle < 157.5:
        character_facing = "down-left"
    elif 157.5 <= current_angle < 180 or -157.5 > current_angle >= -180:
        character_facing = "left"
    elif -112.5 > current_angle >= -157.5:
        character_facing = "up-left"
    elif -67.5 > current_angle >= -112.5:
        character_facing = "up"
    elif -22.5 > current_angle >= -67.5:
        character_facing = "up-right"
    return character_facing

# Debug menu shows UI elements for testing purposes
def debug():
    pygame.draw.line(screen, (255,0,0), player.rect.center, mouse_pos) # Draws line from player to cursor

    fps = clock.get_fps()
    # Define debug information
    fps_text = font.render(f"FPS: {round(fps, 2)}", True, (255,255,255)) # FPS counter
    enemies_alive = font.render(f"Enemies alive: {len(enemies)}", True, (255,255,255)) # Enemies alive counter
    enemies_remaining = font.render(f"Enemies remaining: {wave.enemies_remaining}", True, (255, 255, 255)) # Enemies remaining counter
    current_cooldown = font.render(f"Fire cooldown: {round(fire_cooldown / config.FPS, 2)}", True, (255, 255, 255)) # Shooting cooldown timer
    current_angle_text = font.render(f"Angle: {math.degrees(angle)}", True, (255,255,255))
    character_facing_text = font.render(f"Facing: {character_facing}", True, (255, 255, 255))
    current_wave_text = font.render(f"Wave: {wave.current_wave}", True, (255, 255, 255))
    # Draw debug information onto screen
    screen.blit(fps_text, (10, 10))
    screen.blit(enemies_alive, (10, 40))
    screen.blit(enemies_remaining, (10, 70))
    screen.blit(current_cooldown, (10, 100))
    screen.blit(current_angle_text, (10, 130))
    screen.blit(character_facing_text, (10, 160))
    screen.blit(current_wave_text, (10, 190))



#------------PROGRAM RUNNING------------

while running: # There should be no code here - Treat each game state below as a different function
    # Keep track of frame for effects that happen x times per second
    frame += 1
    if frame == config.FPS + 1:
        frame = 1
    if current_game_state != game_state:
        print(f"Game state has been changed to {current_game_state} from {game_state}")
        current_game_state = game_state
    if frame == 0:
        print(f"Game state {game_state} initializing...")

    #------------GAME LOOP------------
    if game_state == "game":
        screen.blit(background_image, (0, 0)) # Draw background

        # Event checks
        for event in pygame.event.get():
            
            if event.type == pygame.QUIT: # Exit game with window X
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE: # Exit game with Del key
                    running = False
                # 
                # if event.key == pygame.K_f: # Fullscreen game with F key
                #     fullscreen = not fullscreen
                #     if fullscreen:
                #         screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.SCALED | pygame.FULLSCREEN)
                #     else:
                #         screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.SCALED | pygame.RESIZABLE)

            if event.type == spawn_enemy_event and wave.enemies_remaining != 0: # Spawn enemies during wave
                new_enemy = Enemy()
                enemies.append(new_enemy)
                new_enemy.spawn_sound.play()
                wave.enemies_alive += 1
                wave.enemies_remaining -= 1
                pygame.time.set_timer(spawn_enemy_event, wave.spawn_delay)

        # Keyboard checks
        keys = pygame.key.get_pressed()  # get all pressed keys.
        if keys[pygame.K_TAB]:
            debug_menu = True if debug_menu == False else False

        # Reloading controller
        if keys[pygame.K_r] and not player.reloading:
            bullet_count = 0
            player.reloading = True
            player.reload_sound.play()
            player.walk_count = 0
            player.reload_cooldown = config.FPS * 1.5
            player.shooting = False

        # Mouse checks
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()
        angle = get_angle_to_mouse(player.rect.center, mouse_pos)
        character_facing = shooting_direction(angle)

        # Player controller
        # Andrew: Added parameter to draw
        if player.alive:
            if not player.reloading:
                player.move(keys)
            player.check_reload() # Andrew: New function for reloading
            player.draw(screen, character_facing)

        else:
            player.can_shoot = False
            # Fade out on player death
            frames_since_death += 1
            for frame in range(int(frames_since_death / 4)):
                screen.blit(shade_surf_lite, (0, 0))
            if frames_since_death % 50 == 0:
                print(f"Frames since death: {frames_since_death}")
            if frames_since_death == 250:
                frame = -1
                game_state = "end"
            

        # Shooting bullet
        if fire_cooldown <= 0 and player.can_shoot:
            if mouse_buttons[0] == 1:
                if bullet_count < player.ammo: # Player has enough ammo to shoot
                    player.shoot_sound.play()
                    new_bullet = Bullet(player, angle)
                    bullets.append(new_bullet)
                    fire_cooldown = config.FIRE_RATE * config.FPS
                    player.shooting = True
                    player.reloading = False
                    bullet_count += 1
                    print(f"Bullet count: {bullet_count}")
                else: # Player does not have enough ammo to shoot
                    if not player.reloading:
                        player.reload_sound.play()
                        bullet_count = 0
                        player.reloading = True
                        player.walk_count = 0
                        player.reload_cooldown = config.FPS * player.reload_speed
                        player.shooting = False
            else:
                player.shooting = False
        else:
            fire_cooldown -= 1

        # Bullet controller
        for bullet in bullets:
            bullet.move()
            bullet.draw(screen)
            # Delete bullet if it goes out of bounds
            if not 0 < bullet.rect.centerx < config.WIDTH or not 0 < bullet.rect.centery < config.HEIGHT:
                    bullets.remove(bullet)

        # Enemy controller
        for enemy in enemies:
            enemy.draw(screen, player)
            enemy.chase(player)
            # Enemy attack player collision check
            if enemy.mask.overlap(player.mask,(enemy.rect.x - player.rect.x, enemy.rect.y - player.rect.y)) and player.alive:
                player.dead_sound.play()
                player.hurt_sound.play()
                player.alive = False
                end_round_timer = 3
                # frame = -1
                # game_state = "end"
            # Bullet hit enemy collision check
            for bullet in bullets:
                if enemy.rect.colliderect(bullet):
                    if enemy.holding_coin:
                        new_coin = Coin(enemy)
                        coins.append(new_coin)
                    if random.random() > 0.25:
                        enemy.dead_sound.play()
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    wave.enemies_alive -= 1
                    player.kills += 1
                    print(f"Player killed enemy | Player kills: {player.kills} | Enemies left this round: {wave.enemies_remaining + wave.enemies_alive}")

        # Coin controller
        for coin in coins:
            coin.draw(screen)
            if coin.rect.colliderect(player.rect):
                player.coin_sound.play()
                coins.remove(coin)
                player.pickup_coin()
        
        if not player.alive:
            for frame in range(int(frames_since_death / 4)):
                screen.blit(shade_surf_lite_lite, (0, 0))
            player.draw(screen, character_facing)

        if debug_menu:
            debug() # Show debug utils
        else:
            debug_button = font.render(f"Press TAB to open debug menu", True, (255, 255, 255))
            screen.blit(debug_button, (10, 10))

        # End round timer
        if wave.enemies_remaining + wave.enemies_alive == 0:
            if frame == 60:
                end_round_timer -= 1
                loading_dots = 3
                if end_round_timer == 0:
                        print("Setting game state to: intermission")
                        frame = -1
                        end_round_timer = 4
                        game_state = "intermission"
            elif frame == 20:
                loading_dots = 2
            elif frame == 40:
                loading_dots = 1

            if end_round_timer < 4:
                end_round_timer_text = sm_font_small.render(f"Round ending in {end_round_timer} seconds{''.join('.' for _ in range(loading_dots))}", True, config.WHITE)
                screen.blit(end_round_timer_text, (config.WIDTH // 2 - end_round_timer_text.get_width() // 2, config.HEIGHT // 2 + 120))


        # Refresh display
        pygame.display.flip()
        clock.tick(config.FPS)
    #------------GAME LOOP------------



    #------------PAUSE MENU------------
    # Displays game instructions showing keybinds (Should we add this to the start menu too?)
    # Features a resume button, SFX/music volume up/down buttons, fullscreen button, and exit game button
    elif game_state == "paused":
        pass
    #------------PAUSE MENU------------



    #------------INTERMISSION MENU------------
    # Displays the next round number, your current amount of coins, stat levels and upgrade costs
    # Features a button upgrade stats with coins, and a button to procede to next round
    elif game_state == "intermission":

        # Initialize game state variables
        if frame == 0:
            screen.fill((10, 10, 10))  # dark gray background

            for _ in range(100):
                pygame.draw.circle(screen, (50, 255, 50), (random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT)), random.randint(2, 4))

            background = screen.copy()  # snapshot current screen

            splatters = [(random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT)) for _ in range(15)]

            next_wave_button_text = font_small.render("PROCEED TO NEXT WAVE", True, config.WHITE)
            next_wave_button_rect = next_wave_button_text.get_rect(center=(config.WIDTH // 2, config.HEIGHT // 2 - 50))

        # Event checks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.blit(background, (0, 0))  # restore game screen snapshot

        pulse = 0.8 + 0.2 * abs(pygame.math.Vector2(1, 1).rotate(pygame.time.get_ticks() / 50).x)

        for x, y in splatters:
            pygame.draw.circle(screen, config.BLOOD_RED, (x, y), random.randint(5, 15))

        screen.blit(shade_surf, (0, 0))

        text = pygame.transform.scale_by(font_big.render("ROUND CLEARED!", True, config.CRT_GREEN), pulse)
        screen.blit(text, (config.WIDTH // 2 - text.get_width() // 2, 100))

        stats = [
            f"ROUND: {wave.current_wave}",
            f"ZOMBIES KILLED: {player.kills}",
            f"COINS: {player.coins}"
        ]
        for i, text in enumerate(stats):
            color = config.CRT_GLOW if i >= 3 else config.CRT_GREEN
            rendered = font_small.render(text, True, color)
            screen.blit(rendered, (config.WIDTH//2 - rendered.get_width() // 2, 220 + i * 40))
        
        # Create button text
        button_text = "PROCEED TO THE NEXT ROUND"
        button_render = font_small.render(button_text, True, config.CRT_GLOW)
        button_rect = button_render.get_rect(center=(config.WIDTH//2, 340))
        
        # Add a background rectangle for the button
        button_bg = pygame.Rect(button_rect.left - 20, button_rect.top - 10, 
                            button_rect.width + 40, button_rect.height + 20)
        
        # Check if mouse is over the button
        mouse_pos = pygame.mouse.get_pos()
        mouse_hovering_next_wave = button_bg.collidepoint(mouse_pos)
        
        # Draw button with hover effect
        if mouse_hovering_next_wave:
            pygame.draw.rect(screen, config.CRT_GREEN, button_bg, border_radius=5)
            button_render = font_small.render(button_text, True, (0, 0, 0))  # Black text when hovering
        else:
            pygame.draw.rect(screen, (0, 50, 0), button_bg, border_radius=5)
        
        # Draw the button text
        screen.blit(button_render, button_rect)
        
        # Check for clicks
        if mouse_hovering_next_wave and pygame.mouse.get_pressed()[0]:  # Left mouse click
            game_state = "game"
            wave.start_wave()
            bullet_count = 0
            player.ammo = player.max_ammo

        # mouse_pos = pygame.mouse.get_pos()
        # mouse_buttons = pygame.mouse.get_pressed()

        # Highlight hovered options
        # if next_wave_button_rect.collidepoint(mouse_pos):
        #     pygame.draw.rect(screen, (0, 0, 255), sm_start_button_rect.inflate(20, 20), 2)
        #     if mouse_buttons[0] == 1:
        #         wave.start_wave()
        #         print("Setting game state to: game")
        #         game_state = "game"

        for y in range(0, config.HEIGHT, 3):
            pygame.draw.line(screen, (0, 10, 0), (0, y), (config.HEIGHT, y), 1)

        # Refresh display
        pygame.display.flip()
        clock.tick(config.FPS)
    #------------INTERMISSION MENU------------



    #------------START MENU------------
    # Displays an eerie screensplash of some kind
    # Features a button to start the game and exit the game
    elif game_state == "start":

        # Event checks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        screen.fill(config.BLACK)
        mouse_pos = pygame.mouse.get_pos()
        mouse_buttons = pygame.mouse.get_pressed()

        # Highlight hovered options
        if sm_start_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (0, 0, 255), sm_start_button_rect.inflate(20, 20), 2)
            if mouse_buttons[0] == 1:
                wave.start_wave()
                print("Setting game state to: game")
                game_state = "game"
        if sm_exit_button_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (0, 0, 255), sm_exit_button_rect.inflate(20, 20), 2)
            if mouse_buttons[0] == 1:
                running = False

        screen.blit(sm_start_button_text, sm_start_button_rect)
        screen.blit(sm_exit_button_text, sm_exit_button_rect)
        # screen.blit(prompt_text, (config.WIDTH // 2 - prompt_text.get_width() // 2, config.HEIGHT // 2 + 120))
        # Refresh display
        pygame.display.flip()
        clock.tick(config.FPS)
    #------------START MENU------------



    #------------END SCREEN------------
    # Displays rounds survived, stat levels, and leaderboard
    # Features the ability to enter username if your score is leaderboard-worthy
    elif game_state == "end":
        if frame == 0:
            splatters = [(random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT)) for _ in range(15)]

        # Event checks
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE:
                    running = False
        
        screen.fill((10,10,10))

        # Small circles
        if frame % 20 == 0:
            dots = [(random.randint(0, config.WIDTH), random.randint(0, config.HEIGHT), random.randint(2, 5)) for _ in range(150)]
        if frame % 2 == 0:
            for x, y, radius in dots:
                pygame.draw.circle(screen, config.BLOOD_RED, (x, y), radius)

        # Big circles
        for x, y in splatters:
            pygame.draw.circle(screen, config.BLOOD_RED, (x, y), random.randint(5, 15))
            
        if random.random() > 0.1:
            screen.blit(shade_surf, (0, 0))

        pulse = 0.8 + 0.2 * abs(pygame.math.Vector2(1, 1).rotate(pygame.time.get_ticks() / 50).x)
        text = pygame.transform.scale_by(font_big.render("GAME OVER", True, config.CRT_GREEN), pulse)
        screen.blit(text, (config.WIDTH // 2 - text.get_width() // 2, 100))

        stats = [
            f"ROUND REACHED: {wave.current_wave}",
            f"ZOMBIES KILLED: {kills}",
            "",
            "",
            "PRESS DELETE TO QUIT"
        ]

        # Display text in stats list
        for i, text in enumerate(stats):
            color = config.CRT_GLOW if i >= 3 else config.CRT_GREEN
            rendered = font_small.render(text, True, color)
            screen.blit(rendered, (config.WIDTH // 2 - rendered.get_width() // 2, 220 + i * 40))

        # CRT scanlines effect
        for y in range(0, config.WIDTH, 3):
            pygame.draw.line(screen, (0, 10, 0), (0, y), (800, y), 1)

        # Refresh display
        pygame.display.flip()
        clock.tick(config.FPS)
    #------------END SCREEN------------

pygame.quit()
