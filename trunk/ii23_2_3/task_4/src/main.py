import pygame
import random

pygame.init()

# --- Настройки экрана ---
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arkanoid with Powerups")

# --- Цвета ---
WHITE = (255, 255, 255)
RED = (200, 50, 50)
BLUE = (50, 50, 200)
GREEN = (50, 200, 50)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)

# --- Шрифты ---
font = pygame.font.SysFont(None, 36)
large_font = pygame.font.SysFont(None, 64)


# --- Классы ---
class Paddle:
    def __init__(self):
        self.width = 100
        self.height = 15
        self.speed = 7
        self.catch_enabled = False
        self.rect = pygame.Rect(WIDTH // 2 - self.width // 2, HEIGHT - 40, self.width, self.height)

    def move(self, direction):
        self.rect.x += direction * self.speed
        self.rect.x = max(0, min(WIDTH - self.rect.width, self.rect.x))

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)

    def resize(self, factor):
        center = self.rect.centerx
        self.width = max(40, min(200, self.width * factor))
        self.rect.width = self.width
        self.rect.centerx = center

    def speed_up(self, factor):
        self.speed = max(3, min(15, self.speed * factor))


class Ball:
    def __init__(self, x, y, dx=4, dy=-4):
        self.radius = 10
        self.rect = pygame.Rect(x - self.radius, y - self.radius, self.radius * 2, self.radius * 2)
        self.dx = dx
        self.dy = dy
        self.caught = False
        self.offset = 0  # смещение от центра ракетки

    def move(self):
        if not self.caught:
            self.rect.x += self.dx
            self.rect.y += self.dy
            if self.rect.left <= 0 or self.rect.right >= WIDTH:
                self.dx *= -1
            if self.rect.top <= 0:
                self.dy *= -1

    def follow_paddle(self, paddle):
        self.rect.centerx = paddle.rect.centerx + self.offset
        self.rect.bottom = paddle.rect.top

    def draw(self):
        pygame.draw.ellipse(screen, RED, self.rect)

    def bounce(self):
        self.dy *= -1


class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 20)
        self.alive = True

    def draw(self):
        if self.alive:
            pygame.draw.rect(screen, GREEN, self.rect)


class PowerUp:
    TYPES = ['bigger', 'smaller', 'faster', 'catch', 'multi']

    def __init__(self, x, y):
        self.type = random.choice(PowerUp.TYPES)
        self.rect = pygame.Rect(x, y, 20, 20)
        self.dy = 2

    def move(self):
        self.rect.y += self.dy

    def draw(self):
        color = YELLOW if self.type == 'multi' else GRAY
        pygame.draw.rect(screen, color, self.rect)
        label = font.render(self.type[0].upper(), True, WHITE)
        screen.blit(label, (self.rect.x + 2, self.rect.y + 1))


# --- Инициализация игры ---
def reset_game():
    paddle = Paddle()
    balls = [Ball(WIDTH // 2, HEIGHT // 2)]
    bricks = [Brick(x * 65 + 10, y * 25 + 40) for x in range(11) for y in range(5)]
    powerups = []
    return paddle, balls, bricks, powerups


paddle, balls, bricks, powerups = reset_game()
lives = 3
clock = pygame.time.Clock()
running = True
game_over = False
victory = False

# --- Игровой цикл ---
while running:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    direction = 0
    if keys[pygame.K_LEFT]:
        direction = -1
    if keys[pygame.K_RIGHT]:
        direction = 1
    paddle.move(direction)

    if keys[pygame.K_SPACE]:
        for ball in balls:
            if ball.caught:
                ball.caught = False
                ball.dy = -abs(ball.dy)

    # Обработка движения и столкновений мячей
    for ball in balls:
        if ball.caught:
            ball.follow_paddle(paddle)
        else:
            ball.move()
            if paddle.catch_enabled and ball.rect.colliderect(paddle.rect):
                ball.caught = True
                ball.offset = ball.rect.centerx - paddle.rect.centerx
                ball.follow_paddle(paddle)
            elif ball.rect.colliderect(paddle.rect):
                ball.bounce()

    # Столкновения с кирпичами
    for brick in bricks:
        if brick.alive:
            for ball in balls:
                if ball.rect.colliderect(brick.rect):
                    brick.alive = False
                    ball.bounce()
                    if random.random() < 0.3:
                        powerups.append(PowerUp(brick.rect.centerx, brick.rect.centery))

    # Обработка бонусов
    for pu in powerups[:]:
        pu.move()
        if pu.rect.colliderect(paddle.rect):
            if pu.type == 'bigger':
                paddle.resize(1.5)
            elif pu.type == 'smaller':
                paddle.resize(0.7)
            elif pu.type == 'faster':
                paddle.speed_up(1.5)
            elif pu.type == 'catch':
                paddle.catch_enabled = True
            elif pu.type == 'multi':
                new_balls = []
                for _ in range(2):
                    new_ball = Ball(paddle.rect.centerx, paddle.rect.top - 15, dx=random.choice([-4, 4]), dy=-4)
                    new_balls.append(new_ball)
                balls.extend(new_balls)
            powerups.remove(pu)
        elif pu.rect.top > HEIGHT:
            powerups.remove(pu)

    # Проверка потери мяча
    balls = [b for b in balls if b.rect.top <= HEIGHT]
    if not balls:
        lives -= 1
        paddle.catch_enabled = False
        if lives > 0:
            new_ball = Ball(paddle.rect.centerx, paddle.rect.top - 15)
            new_ball.caught = True
            new_ball.offset = 0
            balls.append(new_ball)
        else:
            game_over = True

    # Проверка победы
    if all(not brick.alive for brick in bricks):
        victory = True
        game_over = True

    # Отрисовка объектов
    paddle.draw()
    for ball in balls:
        ball.draw()
    for brick in bricks:
        brick.draw()
    for pu in powerups:
        pu.draw()

    # Жизни
    lives_text = font.render(f"Жизни: {lives}", True, WHITE)
    screen.blit(lives_text, (10, 10))

    # Конец игры
    if game_over:
        if victory:
            msg = "Вы победили!"
        else:
            msg = "Вы проиграли!"
        label = large_font.render(msg, True, YELLOW)
        screen.blit(label, (WIDTH // 2 - label.get_width() // 2, HEIGHT // 2 - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
