import pygame
import random

pygame.init()
pygame.mixer.init()

# General Settings
WIDTH = 500
HEIGHT = 500
FPS = 60 # Number of frames rendered per second
ENEMY_EVENT = pygame.USEREVENT + 1 # Create enemy spawn event
BUTTON_PRESS = pygame.mixer.Sound("audio/button.ogg")
GAME_END = pygame.mixer.Sound("audio/game_end.ogg")

# Player Settings
PLAYER_SPEED = 2 # How many pixels the player moves per frame
PLAYER_IMAGE = pygame.image.load("img/game_files/player_walk/player_front1.png")
PLAYER_DEATH = pygame.mixer.Sound("audio/player_dead.ogg")
PLAYER_HURT = pygame.mixer.Sound("audio/player_damage.ogg")
PLAYER_SHOOT = pygame.mixer.Sound("audio/shoot.ogg")
PLAYER_RELOAD = pygame.mixer.Sound("audio/reload.ogg")
FIRE_RATE = 0.9 # Shooting cooldown in seconds
BASE_AMMO_COUNT = 4
BASE_RELOAD_SPEED = 0.9 # Time in seconds that reloading takes

# Bullet Settings
BULLET_SPEED = 10 # Bullet velocity; How many pixels bullets move per frame

# Enemy Settings
ENEMY_SPEED = 1.5 # How many pixels the enemy moves per frame
ENEMY_IMAGE = pygame.image.load("img/enemy/zombie_sprite.png")
ENEMY_SOUNDS = ["audio/spawn_sound_1.ogg", "audio/spawn_sound_2.ogg", "audio/spawn_sound_3.ogg", "audio/spawn_sound_4.ogg", "audio/spawn_sound_5.ogg"]
ENEMY_SPAWN_RATE = int(random.uniform(0.8, 1.5) * 1000)
ENEMY_DEATH = pygame.mixer.Sound("audio/zombie_death.ogg")

# Coin Settings
COIN_IMAGE = pygame.image.load("img/coin/coin_sprite.png")
COIN_PICKUP_SOUND = pygame.mixer.Sound("audio/pickup_coin.ogg")
UPGRADE_SOUND = pygame.mixer.Sound("audio/upgrade.ogg")

# Wave Settings
WAVE_BASE_ENEMIES = 6
WAVE_SCALE = 1.25

# Colors
BLACK, WHITE, BLOOD_RED = (0, 0, 0), (255, 255, 255), (255, 40, 0, 0.5)
CRT_GREEN, CRT_GLOW = (20, 255, 20), (100, 255, 100)

# Soundtrack
INTRO_MUSIC = pygame.mixer.Sound("audio/soundtrack/zombiegameintro.wav")
OUTRO_MUSIC = pygame.mixer.Sound("audio/soundtrack/zombiegameoutro.wav")
GAME_MUSIC = pygame.mixer.Sound("audio/soundtrack/zombiegamemain.wav")
BETWEEN_MUSIC = pygame.mixer.Sound("audio/soundtrack/zombiegamemenu.wav")
