import pygame
from enum import Enum
from constants import GRID_SIZE, GRID_COUNT

class PowerUpType(Enum):
    SPEED = 1
    SLOW = 2
    INVINCIBLE = 3

class Food:
    def __init__(self, x, y, type, sprite):
        self.x = x
        self.y = y
        self.type = type
        self.sprite = sprite

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

class PowerUp:
    def __init__(self, x, y, type, sprite):
        self.x = x
        self.y = y
        self.type = type
        self.sprite = sprite
        self.duration = 5000
        self.active = False
        self.start_time = 0
        self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def get_remaining_time(self):
        if not self.active:
            return 0
        current_time = pygame.time.get_ticks()
        remaining = self.duration - (current_time - self.start_time)
        return max(0, remaining)

    def should_disappear(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.spawn_time >= 5000

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 2
        start_x = 3
        start_y = GRID_COUNT // 2
        self.positions = [(start_x, start_y), (start_x - 1, start_y)]
        self.direction = (1, 0)
        self.score = 0
        self.speed = 10
        self.power_ups = []
        self.invincible = False
        self.is_teleporting = False

    def get_head_position(self):
        return self.positions[0]

    def update(self, portals):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_COUNT, (cur[1] + y) % GRID_COUNT)

        if new in self.positions[:-1]:
            if not self.invincible:
                return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
        return True

    def get_body_sprite(self, i, sprites):
        if i == 0:
            if self.direction == (0, -1):
                return sprites['snake_head_up']
            elif self.direction == (0, 1):
                return sprites['snake_head_down']
            elif self.direction == (-1, 0):
                return sprites['snake_head_left']
            else:
                return sprites['snake_head_right']
        else:
            return sprites['snake_body']

    def draw(self, screen, sprites):
        for i, p in enumerate(self.positions):
            sprite = self.get_body_sprite(i, sprites)
            screen.blit(sprite, (p[0] * GRID_SIZE, p[1] * GRID_SIZE))

class Portal:
    def __init__(self, x, y, is_start=True, color='blue'):
        self.x = x
        self.y = y
        self.is_start = is_start
        self.color = color
        if is_start:
            self.sprite = pygame.image.load(f'images/{color}portal_start.png').convert_alpha()
        else:
            self.sprite = pygame.image.load(f'images/{color}portal_end.png').convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (GRID_SIZE, GRID_SIZE))

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

class Brick:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE)) 