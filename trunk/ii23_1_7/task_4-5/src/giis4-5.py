import pygame
import random
import sys
from pygame import mixer
import warnings

# Инициализация Pygame и генератора случайных чисел
pygame.init()
mixer.init()
random.seed()  # Явная инициализация генератора

# Константы
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -15
PLAYER_SPEED = 4

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
SKY_WHITE = (255, 255, 255)

# Создание окна
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Платформер")
clock = pygame.time.Clock()

# Загрузка звуков
try:
    jump_sound = mixer.Sound('jump.wav')
    coin_sound = mixer.Sound('coin.wav')
    achievement_sound = mixer.Sound('achievement.wav')
except:
    jump_sound = mixer.Sound(buffer=bytearray(100))
    coin_sound = mixer.Sound(buffer=bytearray(100))
    achievement_sound = mixer.Sound(buffer=bytearray(100))

class SpriteSheet:
    def __init__(self, filename):
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except:
            self.sheet = pygame.Surface((32, 32), pygame.SRCALPHA)

    def get_frames(self, frame_width, frame_height, rows=1, cols=1):
        frames = []
        for row in range(rows):
            for col in range(cols):
                frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
                frame.blit(self.sheet, (0, 0), (col * frame_width, row * frame_height, frame_width, frame_height))
                frames.append(frame)
        return frames

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, is_moving=False):
        super().__init__()
        try:
            grass_img = pygame.image.load('trava.png').convert_alpha()
            self.image = pygame.transform.scale(grass_img, (width, height))
        except:
            self.image = pygame.Surface((width, height))
            self.image.fill(GREEN)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_moving = is_moving
        self.direction = 1
        self.speed = 2
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        if self.is_moving:
            prev_x = self.rect.x
            self.rect.x += self.speed * self.direction

            if pygame.sprite.collide_rect(self, player):
                if self.rect.x > prev_x:
                    player.rect.right = self.rect.left
                elif self.rect.x < prev_x:
                    player.rect.left = self.rect.right

            if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
                self.direction *= -1

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.spritesheet = SpriteSheet('player_spritesheet.png')
        self.prev_y = 0

        run_right = self.spritesheet.get_frames(92, 119, rows=1, cols=8)
        run_left = [pygame.transform.flip(frame, True, False) for frame in run_right]

        self.run_right = [self._process_sprite(pygame.transform.scale(frame, (50, 70))) for frame in run_right]
        self.run_left = [self._process_sprite(pygame.transform.scale(frame, (50, 70))) for frame in run_left]

        self.idle_right = [self.run_right[0]]
        self.idle_left = [self.run_left[0]]
        self.jump_right = [self.run_right[3]]
        self.jump_left = [self.run_left[3]]

        self.current_anim = self.idle_right
        self.anim_frame = 0
        self.anim_speed = 1.5
        self.image = self.current_anim[self.anim_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (100, 300)
        self.velocity_y = 0
        self.on_ground = False
        self.score = 0
        self.achievements = []
        self.facing_right = True
        self.last_update = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)
        self.can_pass_through = False

    def _process_sprite(self, image):
        image = image.copy()
        cropped_rect = pygame.Rect(0, 0, image.get_width(), image.get_height() - 10)
        image = image.subsurface(cropped_rect).copy()
        pixels = pygame.PixelArray(image)
        pixels.replace((255, 255, 255, 255), (0, 0, 0, 0))
        del pixels
        return image

    def update(self):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        self.prev_y = self.rect.y

        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        self.on_ground = False
        platform_hits = pygame.sprite.spritecollide(self, platforms, False)

        for platform in platform_hits:
            if self.velocity_y > 0:
                if self.rect.bottom > platform.rect.top and self.prev_y + self.rect.height <= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.velocity_y = 0
                    self.on_ground = True
            elif self.velocity_y < 0:
                if self.rect.top < platform.rect.bottom and self.prev_y >= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.velocity_y = 0

        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED
            self.facing_right = False
            if self.on_ground:
                self.current_anim = self.run_left
        elif keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED
            self.facing_right = True
            if self.on_ground:
                self.current_anim = self.run_right
        elif self.on_ground:
            self.current_anim = self.idle_right if self.facing_right else self.idle_left

        if not self.on_ground:
            self.current_anim = self.jump_right if self.facing_right else self.jump_left

        if now - self.last_update > 100:
            self.last_update = now
            self.anim_frame = (self.anim_frame + self.anim_speed) % len(self.current_anim)
            self.image = self.current_anim[int(self.anim_frame)]
            self.mask = pygame.mask.from_surface(self.image)

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def jump(self):
        if self.on_ground:
            self.velocity_y = JUMP_STRENGTH
            jump_sound.play()

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.spritesheet = SpriteSheet('coin_spritesheet.png')
        self.frames = self.spritesheet.get_frames(64, 64, rows=1, cols=8)
        self.frames = [pygame.transform.scale(frame, (30, 30)) for frame in self.frames]
        self.anim_frame = 0
        self.anim_speed = 0.9
        self.image = self.frames[self.anim_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.last_update = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.anim_frame = (self.anim_frame + self.anim_speed) % len(self.frames)
            self.image = self.frames[int(self.anim_frame)]
            self.mask = pygame.mask.from_surface(self.image)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.spritesheet = SpriteSheet('enemy_spritesheet.png')
        self.frames_right = self.spritesheet.get_frames(64, 64, rows=1, cols=8)
        self.frames_right = [pygame.transform.scale(frame, (40, 40)) for frame in self.frames_right]
        self.frames_left = [pygame.transform.flip(frame, True, False) for frame in self.frames_right]

        self.anim_frame = 0
        self.anim_speed = 1
        self.frames = self.frames_right
        self.image = self.frames[self.anim_frame]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.speed = 4
        self.last_update = pygame.time.get_ticks()
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect.x += self.speed * self.direction

        if self.rect.right > SCREEN_WIDTH:
            self.direction = -1
            self.frames = self.frames_left
        elif self.rect.left < 0:
            self.direction = 1
            self.frames = self.frames_right

        now = pygame.time.get_ticks()
        if now - self.last_update > 100:
            self.last_update = now
            self.anim_frame = (self.anim_frame + self.anim_speed) % len(self.frames)
            self.image = self.frames[int(self.anim_frame)]
            self.mask = pygame.mask.from_surface(self.image)

class Weather:
    def __init__(self):
        self.rain_drops = []
        self.is_raining = False
        self.wind_strength = 0

    def start_rain(self):
        self.is_raining = True
        self.rain_drops = [
            {
                'x': random.uniform(0, SCREEN_WIDTH),
                'y': random.uniform(-50, 0),
                'speed': random.uniform(2.0, 5.0),
                'width': random.uniform(1.0, 3.0)
            }
            for _ in range(100)
        ]

    def update(self):
        if self.is_raining:
            for drop in self.rain_drops:
                drop['y'] += drop['speed']
                drop['x'] += self.wind_strength
                if drop['y'] > SCREEN_HEIGHT:
                    drop.update({
                        'y': random.uniform(-50, 0),
                        'x': random.uniform(0, SCREEN_WIDTH)
                    })

    def draw(self, surface):
        if self.is_raining:
            for drop in self.rain_drops:
                pygame.draw.line(
                    surface,
                    (200, 200, 255, int(drop['width'])),
                    (int(drop['x']), int(drop['y'])),
                    (int(drop['x'] + self.wind_strength * 5), int(drop['y'] + drop['speed'] * 3)),
                    int(drop['width'])
                )

class GameOverScreen:
    def __init__(self):
        self.font_large = pygame.font.SysFont('Arial', 72)
        self.font_small = pygame.font.SysFont('Arial', 36)
        self.restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 50, 200, 50)

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        game_over_text = self.font_large.render("Проиграл!", True, RED)
        surface.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        pygame.draw.rect(surface, GREEN, self.restart_button)
        restart_text = self.font_small.render("Повторить", True, WHITE)
        surface.blit(restart_text, (self.restart_button.centerx - restart_text.get_width() // 2,
                                  self.restart_button.centery - restart_text.get_height() // 2))

    def check_click(self, pos):
        return self.restart_button.collidepoint(pos)

class Door(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((40, 70))
        self.image.fill((139, 69, 19))
        pygame.draw.rect(self.image, (160, 82, 45), (10, 10, 20, 50))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)

def init_game():
    global all_sprites, platforms, coins, enemies, player, weather, game_over, door, win

    all_sprites = pygame.sprite.Group()
    platforms = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    player = Player()
    all_sprites.add(player)

    ground = Platform(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
    platforms.add(ground)
    all_sprites.add(ground)

    platform_positions = [
        (100, 450, 100, 20),
        (300, 400, 100, 20),
        (500, 350, 100, 20, True),
        (200, 300, 100, 20),
        (400, 250, 100, 20),
    ]
    for pos in platform_positions:
        p = Platform(*pos)
        platforms.add(p)
        all_sprites.add(p)

    for _ in range(15):
        coin = Coin(
            x=random.randrange(50, SCREEN_WIDTH - 50),
            y=random.randrange(50, SCREEN_HEIGHT - 100)
        )
        coins.add(coin)
        all_sprites.add(coin)

    enemy = Enemy(200, SCREEN_HEIGHT - 80)
    enemies.add(enemy)
    all_sprites.add(enemy)

    weather = Weather()

    door = Door(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 120)
    door.image.set_alpha(0)
    all_sprites.add(door)

    game_over = False
    win = False

class WinScreen:
    def __init__(self):
        self.font_large = pygame.font.SysFont('Arial', 72)
        self.font_small = pygame.font.SysFont('Arial', 36)

    def draw(self, surface):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        win_text = self.font_large.render("Победа!", True, GREEN)
        surface.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

        score_text = self.font_small.render(f"Собрано монет: {player.score}", True, WHITE)
        surface.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))

# Инициализация игры
init_game()
game_over_screen = GameOverScreen()
win_screen = WinScreen()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_over or win:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if game_over_screen.check_click(event.pos) if game_over else True:
                    init_game()
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()
                if event.key == pygame.K_r:
                    weather.start_rain()
                    weather.wind_strength = random.uniform(-1.0, 1.0)

    if not game_over and not win:
        all_sprites.update()
        weather.update()

        hits = pygame.sprite.spritecollide(player, coins, True, pygame.sprite.collide_mask)
        for hit in hits:
            player.score += 1
            coin_sound.play()

            if player.score >= 20 and door.image.get_alpha() == 0:
                door.image.set_alpha(255)
                achievement_sound.play()

            if player.score >= 5 and "Начинающий сборщик монет" not in player.achievements:
                player.achievements.append("Начинающий сборщик монет")
                achievement_sound.play()

            if player.score >= 30 and "Да ты Жадина!" not in player.achievements:
                player.achievements.append("Да ты Жадина!")
                achievement_sound.play()

            if random.uniform(0.0, 1.0) > 0.3:
                coin = Coin(
                    x=random.randrange(50, SCREEN_WIDTH - 50),
                    y=random.randrange(50, SCREEN_HEIGHT - 100)
                )
                coins.add(coin)
                all_sprites.add(coin)

        if pygame.sprite.spritecollide(player, enemies, False, pygame.sprite.collide_mask):
            game_over = True

        if door.image.get_alpha() == 255 and pygame.sprite.collide_mask(player, door):
            win = True

        screen.fill(SKY_WHITE)
        weather.draw(screen)
        all_sprites.draw(screen)

        font = pygame.font.SysFont('Arial', 24)
        score_text = font.render(f"Монеты: {player.score}/20", True, BLACK)
        screen.blit(score_text, (10, 10))

        if player.achievements:
            ach_text = font.render("Ачивки: " + ", ".join(player.achievements), True, BLACK)
            screen.blit(ach_text, (10, 40))
    elif game_over:
        screen.fill(SKY_WHITE)
        weather.draw(screen)
        all_sprites.draw(screen)
        game_over_screen.draw(screen)
    elif win:
        screen.fill(SKY_WHITE)
        weather.draw(screen)
        all_sprites.draw(screen)
        win_screen.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()