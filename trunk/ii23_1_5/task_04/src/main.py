import pygame
import random
import os
import math
import time
from secrets import randbelow, choise

# --- Константы ---
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 7
ENEMY_DROP = 30
MAX_ENEMY_Y = 350  # Ограничение по вертикали

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (230, 230, 230)
GREEN = (0, 255, 0)
BLUE = (100, 100, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders Enhanced")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

ASSETS_DIR = "assets"

def load_sprite(name):
    path = os.path.join(ASSETS_DIR, name + ".png")
    return pygame.image.load(path).convert_alpha()

# --- Загрузка спрайтов ---
try:
    PLAYER_IMG = load_sprite("player")
    ENEMY_IMGS = [load_sprite("enemy1"), load_sprite("enemy2")]
    BULLET_IMG = load_sprite("bullet")
    SHIELD_IMG = load_sprite("shield")
    DOUBLE_IMG = load_sprite("double_shot")
except Exception as e:
    print(f"Ошибка загрузки спрайтов: {e}")
    exit()

# --- Классы ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = PLAYER_IMG
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = PLAYER_SPEED
        self.shield = False
        self.double_shot = False
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            x = self.rect.centerx
            y = self.rect.top
            bullets.add(Bullet(x, y, -1))
            if self.double_shot:
                bullets.add(Bullet(x - 15, y + 10, -1))
                bullets.add(Bullet(x + 15, y + 10, -1))
            self.last_shot = now

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, special=False, wave=1):
        super().__init__()
        self.image = ENEMY_IMGS[1] if special else ENEMY_IMGS[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.base_x = x
        self.base_y = y
        self.special = special
        self.direction = 1
        self.speed = 1 + wave * 0.2
        self.amplitude = randbelow(16) + 10  # Замена random.randint
        self.frequency = random.uniform(0.002, 0.007)
        self.time_offset = random.uniform(0, math.pi * 2)

    def update(self):
        self.rect.x += self.direction * self.speed
        y_offset = self.amplitude * math.sin(pygame.time.get_ticks() * self.frequency + self.time_offset)
        new_y = self.base_y + y_offset
        if new_y <= MAX_ENEMY_Y:
            self.rect.y = new_y
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.direction *= -1

    def drop_bonus(self):
        bonus_type = choice(['shield', 'double'])
        return Bonus(self.rect.centerx, self.rect.centery, bonus_type)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.image = BULLET_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction

    def update(self):
        self.rect.y += self.direction * BULLET_SPEED
        if self.rect.bottom < 0 or self.rect.top > HEIGHT:
            self.kill()

class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, bonus_type):
        super().__init__()
        self.type = bonus_type
        self.image = SHIELD_IMG if bonus_type == 'shield' else DOUBLE_IMG
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 2

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()

def spawn_wave(all_sprites, enemies, wave_number):
    enemies.empty()
    rows = 3 + wave_number // 2
    cols = 8
    spacing_x = 80
    spacing_y = 60
    start_x = (WIDTH - (cols - 1) * spacing_x) // 2
    start_y = 50

    for row in range(rows):
        for col in range(cols):
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            special = randbelow(10) == 0  # Замена random.random() < 0.1
            enemy = Enemy(x, y, special, wave_number)
            enemies.add(enemy)
            all_sprites.add(enemy)

def main():
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    bonuses = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    score = 0
    wave = 1
    spawn_wave(all_sprites, enemies, wave)

    lose_line = pygame.Rect(0, HEIGHT - 100, WIDTH, 2)

    shield_timer = 0
    double_timer = 0

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(GRAY)
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.shoot(bullets)
            elif event.type == pygame.USEREVENT + 1:
                player.shield = False
                shield_timer = 0
            elif event.type == pygame.USEREVENT + 2:
                player.double_shot = False
                player.shoot_delay = 250
                double_timer = 0

        player.update(keys)
        bullets.update()
        bonuses.update()

        for sprite in all_sprites:
            if sprite is not player:
                sprite.update()

        for bullet in bullets:
            if bullet.direction == -1:
                hits = pygame.sprite.spritecollide(bullet, enemies, True)
                for hit in hits:
                    bullet.kill()
                    score += 10
                    if randbelow(5) == 0:  # Замена random.random() < 0.2
                        bonuses.add(hit.drop_bonus())
                    if len(enemies) == 0:
                        wave += 1
                        spawn_wave(all_sprites, enemies, wave)
            else:
                if pygame.sprite.collide_rect(bullet, player):
                    if not player.shield:
                        running = False
                    bullet.kill()

        for bonus in bonuses:
            if pygame.sprite.collide_rect(bonus, player):
                if bonus.type == 'shield':
                    player.shield = True
                    shield_timer = time.time() + 5
                    pygame.time.set_timer(pygame.USEREVENT + 1, 5000, 1)
                elif bonus.type == 'double':
                    player.double_shot = True
                    player.shoot_delay = 150
                    double_timer = time.time() + 5
                    pygame.time.set_timer(pygame.USEREVENT + 2, 5000, 1)
                bonus.kill()

        for enemy in enemies:
            if enemy.rect.bottom >= lose_line.top:
                running = False
                break

        all_sprites.draw(screen)
        bullets.draw(screen)
        bonuses.draw(screen)

        score_text = font.render(f"Score: {score}", True, BLACK)
        wave_text = font.render(f"Wave: {wave}", True, BLACK)
        screen.blit(score_text, (10, 10))
        screen.blit(wave_text, (10, 40))

        if player.shield:
            remaining = max(0, int(shield_timer - time.time()))
            shield_info = font.render(f"Shield: {remaining}s", True, BLUE)
            screen.blit(shield_info, (WIDTH - 150, 10))

        if player.double_shot:
            remaining = max(0, int(double_timer - time.time()))
            double_info = font.render(f"Double: {remaining}s", True, GREEN)
            screen.blit(double_info, (WIDTH - 150, 40))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()