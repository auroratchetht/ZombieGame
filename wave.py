import pygame, config


class Wave:
    def __init__(self):
        self.current_wave = 0
        self.enemies_remaining = 0
        self.enemies_alive = 0
        self.wave_timer = 0
        self.spawn_timer = 0
        self.spawn_delay = 1000
        self.wave_enemy_count = config.WAVE_BASE_ENEMIES

    def start_wave(self):
        self.current_wave += 1
        self.wave_enemy_count = int(config.WAVE_SCALE * self.wave_enemy_count)
        self.enemies_remaining = self.wave_enemy_count
        print(f"NEW WAVE: Wave {self.current_wave} | Enemies: {self.enemies_remaining}")
        self.enemies_alive = 0
        self.spawn_delay = max(200, config.ENEMY_SPAWN_RATE - (self.current_wave * 50))
