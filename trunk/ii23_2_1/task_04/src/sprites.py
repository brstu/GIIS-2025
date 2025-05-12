import pygame
from constants import GRID_SIZE, SPRITE_WIDTH, SPRITE_HEIGHT, WINDOW_SIZE, BACKGROUND_COLOR

def extract_sprite(sheet, x, y, width, height):
    """Вырезает спрайт из спрайт-листа"""
    sprite = pygame.Surface((width, height), pygame.SRCALPHA)
    sprite.blit(sheet, (0, 0), (x, y, width, height))
    return sprite

def load_sprites():
    """Загружает и масштабирует все спрайты"""

    apple_sprite = pygame.image.load('images/apple.png')
    cherry_sprite = pygame.image.load('images/cherry.png')
    cookie_sprite = pygame.image.load('images/cookies.png')
    gold_apple_sprite = pygame.image.load('images/goldapple.png')
    brick_sprite = pygame.image.load('images/brick.png')

    snake_head_up = pygame.image.load('images/head_up.png')
    snake_head_down = pygame.image.load('images/head_down.png')
    snake_head_left = pygame.image.load('images/head_left.png')
    snake_head_right = pygame.image.load('images/head_right.png')
    snake_body = pygame.image.load('images/body.png')

    speed_effect = pygame.image.load('images/speed.png')
    slow_effect = pygame.image.load('images/slow.png')
    invulnerability_effect = pygame.image.load('images/invulnerability.png')

    sprites = {
        'snake_head_up': snake_head_up,
        'snake_head_down': snake_head_down,
        'snake_head_left': snake_head_left,
        'snake_head_right': snake_head_right,
        'snake_body': snake_body,
        'apple': apple_sprite,
        'cherry': cherry_sprite,
        'cookie': cookie_sprite,
        'gold_apple': gold_apple_sprite,
        'brick': brick_sprite,
        'powerup_speed': speed_effect,
        'powerup_slow': slow_effect,
        'powerup_invincible': invulnerability_effect,
    }

    for key in sprites:
        sprites[key] = pygame.transform.scale(sprites[key], (GRID_SIZE, GRID_SIZE))

    sprites['background'] = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
    sprites['background'].fill(BACKGROUND_COLOR)

    return sprites 