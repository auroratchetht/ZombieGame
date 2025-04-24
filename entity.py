import config, pygame, random, math
from Frame_lists import zombie
from Frame_lists import player



#------------PLAYER CLASS------------
class Player:
    def __init__(self):
        self.sprite = config.PLAYER_IMAGE
        self.rect = self.sprite.get_rect()
        self.rect.center = (config.WIDTH // 2 - self.sprite.get_width(), config.HEIGHT // 2 - self.sprite.get_height())
        self.mask = pygame.mask.from_surface(self.sprite)
        self.alive = True
        self.dead_sound = config.PLAYER_DEATH
        self.hurt_sound = config.PLAYER_HURT
        self.shoot_sound = config.PLAYER_SHOOT
        self.reload_sound = config.PLAYER_RELOAD
        self.coin_sound = config.COIN_PICKUP_SOUND
        self.speed = config.PLAYER_SPEED
        self.fire_rate = config.FIRE_RATE
        self.coins = 0
        self.kills = 0
        self.direction = "front"
        self.moving = True
        self.shooting = False
        self.reloading = False
        self.can_shoot = True
        self.walk_count = 0
        self.attack_count = 0
        self.reload_cooldown = 0
        self.ammo = config.BASE_AMMO_COUNT
        self.max_ammo = config.BASE_AMMO_COUNT
        self.reload_speed = config.BASE_RELOAD_SPEED

    #------PLAYER MOVE FUNCTION------
    def move(self, keys):
        change_x, change_y = 0, 0
        if keys[pygame.K_a]:
            change_x -= 1
            self.direction = "left"
        if keys[pygame.K_d]:
            change_x += 1
            self.direction = "right"
        if keys[pygame.K_w]:
            change_y -= 1
            self.direction = "back"
        if keys[pygame.K_s]:
            change_y += 1
            self.direction = "front"
        # Check for movement
        if change_x == 0 and change_y == 0:
            self.moving = False
        else:
            self.moving = True
            # Normalize diagonal movement
            if change_x != 0 and change_y != 0:
                magnitude = math.sqrt(2) # Aprox. 1.4 | hypotenouse value of right triangle with two sides of length 1 (change_x, change_y)
                change_x /= magnitude
                change_y /= magnitude
                # Diagnal movement animation handling
                if self.direction == "back":
                    self.direction = "back-left" if change_x < 0 else "back-right"
                elif self.direction == "front":
                    self.direction = "front-left" if change_x < 0 else "front-right"

            # Move player by player-speed pixels every frame
            if self.alive:
                self.rect.move_ip(change_x * self.speed, change_y * self.speed)

            # Keep player in window
            self.rect.center = (int(max(self.rect.w/2, min(self.rect.centerx, config.WIDTH - self.rect.w/2))), # Defines horizontal boundary
                                int(max(self.rect.h/2, min(self.rect.centery, config.HEIGHT - self.rect.h/2)))) # Defines vertical boundary


    #------PLAYER DRAW FUNCTION------
    def draw(self, target_surface, direction):
        shooting_direction = "shoot " + direction
        moving_shooting_direction = "run shoot " + direction
        reloading_direction = "reload " + direction
        if not self.alive:
            # Andrew: in main loop when player dies set player.walk_count to 0
            # Andrew: don't have dying function in this version of the game so hopefully this works
            if self.direction == "front-left" or self.direction == "front-right":
                self.direction = "front"
            death_direction = "death " + self.direction
            target_surface.blit(player[4][death_direction][int(self.walk_count)], self.rect)
            if self.walk_count < 7.8:
                self.walk_count += 0.2
            else:
                self.walk_count = 7.8
            return
        if self.reloading and not self.can_shoot:
            # Andrew: This can def go somewhere else, but it works here so I left it here
            if reloading_direction == "reload down" or reloading_direction == "reload down-left" or reloading_direction == "reload down-right":
                reloading_direction = "reload front"
            if reloading_direction == "reload up":
                reloading_direction = "reload back"
            if reloading_direction == "reload up-left":
                reloading_direction = "reload back-left"
            if reloading_direction == "reload up-right":
                reloading_direction = "reload back-right"
            if reloading_direction in player[3]:
                target_surface.blit(player[3][reloading_direction][int(self.walk_count)], self.rect)
                if self.walk_count < 7.9:
                    self.walk_count += 0.1
                else:
                    self.walk_count = 7.9
        if self.shooting and self.can_shoot:
            if shooting_direction in player[2] and not self.moving:
                target_surface.blit(player[2][shooting_direction][int(self.attack_count)], self.rect)
                self.attack_count = (self.attack_count + 0.2) % 8
            elif moving_shooting_direction in player[1] and self.moving:
                target_surface.blit(player[1][moving_shooting_direction][int(self.attack_count)], self.rect)
                self.attack_count = (self.attack_count + 0.2) % 8
        elif self.moving and self.can_shoot:
            walking_direction = "walk " + self.direction
            if walking_direction in player[0] and self.moving:
                target_surface.blit(player[0][walking_direction][int(self.walk_count)], self.rect)
                self.walk_count = (self.walk_count + 0.2) % 8
        else:
            if not self.moving and not self.reloading:
                target_surface.blit(player[0]["walk front"][0], self.rect)
                self.walk_count = 0

    
    #-----PLAYER RELOAD FUNCTION-----
    # Andrew: New function for reloading checks a bunch of bools and ticks down the cooldown
    def check_reload(self):
        if self.reloading:
            self.can_shoot = False
            if self.reload_cooldown > 0:
                self.reload_cooldown -=1
                self.reloading = True
            else:
                self.reloading = False
                self.can_shoot = True


    #------PLAYER COIN FUNCTION------
    def pickup_coin(self):
        self.coins += 1
#------------PLAYER CLASS------------



#------------BULLET CLASS------------
class Bullet:
    def __init__(self, player, angle):
        self.rect = pygame.Rect(player.rect.centerx, player.rect.centery, 4, 4)
        self.surface = pygame.Surface((self.rect.w, self.rect.h))
        self.surface.fill((255, 0, 0))
        self.angle = angle # Angle of bullet trajectory; determined when fired from player
        self.speed = config.BULLET_SPEED



    #-----BULLET MOVE FUNCTION-----
    def move(self):
        # Move bullet along bullet path (angle from player to mouse when shot) by bullet-speed pixels every frame
        self.rect.move_ip(math.cos(self.angle) * self.speed, # x-axis movement (horizontal)
                          math.sin(self.angle) * self.speed) # y-axis movement (vertical)


    #-----BULLET DRAW FUNCTION-----
    def draw(self, target_surface):
        target_surface.blit(self.surface, self.rect)
#------------BULLET CLASS------------



#------------ENEMY CLASS------------
class Enemy:
    def __init__(self):
        self.sprite = config.ENEMY_IMAGE
        self.rect = self.sprite.get_rect()
        self.mask = pygame.mask.from_surface(self.sprite)
        self.spawn_sound = pygame.mixer.Sound(random.choice(config.ENEMY_SOUNDS))
        self.speed = config.ENEMY_SPEED
        self.dead_sound = config.ENEMY_DEATH
        self.direction = "front"
        self.walk_count = 0
        self.attack_count = 0
        self.spawn()
        self.holding_coin = False
        if random.random() >= 0.6: self.holding_coin = True # 30% chance to spawn with coin


    #-----ENEMY SPAWN FUNCTION-----
    def spawn(self):
        match random.choice(["top", "bottom", "left", "right"]):
            case "top":
                self.rect.center = (int(random.uniform(0, (config.WIDTH - self.rect.w))), 0)

            case "bottom":
                self.rect.center = (int(random.uniform(0, (config.WIDTH - self.rect.w))), config.HEIGHT)

            case "left":
                self.rect.center = (0, int(random.uniform(0, (config.HEIGHT - self.rect.h))))

            case "right":
                self.rect.center = (config.WIDTH, int(random.uniform(0, (config.HEIGHT - self.rect.h))))


    #-----ENEMY CHASE FUNCTION-----
    def chase(self, target):
        change_x, change_y = 0, 0
        if abs(target.rect.centerx - self.rect.centerx) > abs(target.rect.centery - self.rect.centery):  # Move horizontally
            if target.rect.centerx < self.rect.centerx:
                change_x -= 1
                self.direction = "left"
            if target.rect.centerx > self.rect.centerx:
                change_x += 1
                self.direction = "right"
        elif abs(target.rect.centerx - self.rect.centerx) < abs(target.rect.centery - self.rect.centery):  # Move vertically
            if target.rect.centery < self.rect.centery:
                change_y -= 1
                self.direction = "back"
            if target.rect.centery > self.rect.centery:
                change_y += 1
                self.direction = "front"
        elif abs(target.rect.centerx - self.rect.centerx) == abs(target.rect.centery - self.rect.centery):  # If both distances are equal, move diagonally
            if target.rect.centerx < self.rect.centerx:
                change_x -= 1
                self.direction = "left"
            if target.rect.centerx > self.rect.centerx:
                change_x += 1
                self.direction = "right"
            if target.rect.centery < self.rect.centery:
                change_y -= 1
                self.direction = "back"
            if target.rect.centery > self.rect.centery:
                change_y += 1
                self.direction = "front"
            # Normalize diagonal movement
            magnitude = math.sqrt(2) # Aprox. 1.4 | hypotenouse value of right triangle with two sides of length 1 (change_x, change_y)
            if magnitude != 0:
                change_x /= magnitude
                change_y /= magnitude

        # Move player by player-speed pixels every frame
        self.rect.move_ip(change_x * self.speed, change_y * self.speed)


    #------ENEMY DRAW FUNCTION------
    def draw(self, target_surface, target_rect):
        walking_direction = "walk " + self.direction
        attack_direction = "attack " + self.direction
        if self.rect.colliderect(target_rect) and attack_direction in zombie[1]:
            target_surface.blit(zombie[1][attack_direction][int(self.attack_count)], self.rect)
            self.attack_count = (self.attack_count + 0.2) % 8 if self.attack_count <= 8 else 0
            #self.zombie_count = 0
        elif walking_direction in zombie[0]:
            target_surface.blit(zombie[0][walking_direction][int(self.walk_count)], self.rect)
            self.walk_count = (self.walk_count + 0.2) % 10

        else:
            target_surface.blit(zombie[0][walking_direction][0], self.rect)
            self.walk_count = 0
#------------ENEMY CLASS------------



#------------COIN CLASS------------
class Coin:
    def __init__(self, enemy):
        self.sprite = config.COIN_IMAGE
        self.rect = self.sprite.get_rect()
        self.rect.center = enemy.rect.center

    #------COIN DRAW FUNCTION------
    def draw(self, target_surface):
        target_surface.blit(self.sprite, self.rect)
#------------COIN CLASS------------
