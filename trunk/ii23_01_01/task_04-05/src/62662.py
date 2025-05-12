import pygame
import secrets
import time

# --- Константы ---
WIDTH, HEIGHT = 600, 600
CELL_SIZE = 20
COLS, ROWS = WIDTH // CELL_SIZE, HEIGHT // CELL_SIZE
FPS = 10

# --- Цвета ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake with Bonuses & Portals")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

# Загрузка спрайтов бонусов и порталов
bonus_images = {
    "speed": pygame.image.load("bonus_speed.jpg").convert_alpha(),
    "slow": pygame.image.load("bonus_slow.jpg").convert_alpha(),
    "invincible": pygame.image.load("bonus_invincible.jpg").convert_alpha()
}
portal_image = pygame.image.load("portal.png").convert_alpha()
food_image = pygame.transform.scale(pygame.image.load("food.jpg").convert_alpha(), (CELL_SIZE, CELL_SIZE))

# --- Классы ---

class Snake:
    def __init__(self):
        self.body = [(COLS // 2, ROWS // 2)]
        self.direction = (0, -1)
        self.grow = False
        self.invincible = False
        self.invincible_timer = 0

    def update(self):
        head_x, head_y = self.body[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % COLS, (head_y + dy) % ROWS)

        if not self.invincible and new_head in self.body:
            return False  # Game over

        self.body.insert(0, new_head)

        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

        if self.invincible and time.time() > self.invincible_timer:
            self.invincible = False

        return True

    def set_direction(self, dir):
        if (dir[0] * -1, dir[1] * -1) != self.direction:
            self.direction = dir

    def eat(self):
        self.grow = True

    def draw(self, surface):
        for i, (x, y) in enumerate(self.body):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GREEN if i == 0 else CYAN
            pygame.draw.rect(surface, color, rect)


class Bonus:
    def __init__(self):
        self.types = ['speed', 'slow', 'invincible']
        self.spawn()

    def spawn(self):
        self.type = secrets.choice(self.types)
        self.pos = (secrets.randbelow(COLS), secrets.randbelow(ROWS))
        self.timer = time.time() + 10

    def draw(self, surface):
        image = pygame.transform.scale(bonus_images[self.type], (CELL_SIZE, CELL_SIZE))
        surface.blit(image, (self.pos[0] * CELL_SIZE, self.pos[1] * CELL_SIZE))


class Portal:
    def __init__(self):
        self.a = (secrets.randbelow(COLS), secrets.randbelow(ROWS))
        self.b = (secrets.randbelow(COLS), secrets.randbelow(ROWS))

    def draw(self, surface):
        scaled = pygame.transform.scale(portal_image, (CELL_SIZE, CELL_SIZE))
        surface.blit(scaled, (self.a[0] * CELL_SIZE, self.a[1] * CELL_SIZE))
        surface.blit(scaled, (self.b[0] * CELL_SIZE, self.b[1] * CELL_SIZE))

    def teleport(self, pos):
        return self.b if pos == self.a else self.a if pos == self.b else pos


# --- Основной игровой цикл ---

def main():
    snake = Snake()
    food = (secrets.randbelow(COLS), secrets.randbelow(ROWS))
    bonus = Bonus()
    portal = Portal()

    score = 0
    running = True
    speed = FPS
    slow_timer = 0
    speed_timer = 0

    while running:
        clock.tick(speed)
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    snake.set_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    snake.set_direction((0, 1))
                elif event.key == pygame.K_LEFT:
                    snake.set_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    snake.set_direction((1, 0))

        # Проверка портала
        snake.body[0] = portal.teleport(snake.body[0])

        # Обновление змейки
        if not snake.update():
            break  # проигрыш

        # Еда
        if snake.body[0] == food:
            snake.eat()
            score += 1
            food = (secrets.randbelow(COLS), secrets.randbelow(ROWS))

        # Бонус
        if snake.body[0] == bonus.pos:
            if bonus.type == 'speed':
                speed = FPS * 2
                speed_timer = time.time() + 5
            elif bonus.type == 'slow':
                speed = FPS // 2
                slow_timer = time.time() + 5
            elif bonus.type == 'invincible':
                snake.invincible = True
                snake.invincible_timer = time.time() + 5
            bonus.spawn()

        # Сброс бонусов по таймеру
        if time.time() > speed_timer and time.time() > slow_timer:
            speed = FPS

        if time.time() > bonus.timer:
            bonus.spawn()

        # Рендер
        snake.draw(screen)
        screen.blit(food_image, (food[0] * CELL_SIZE, food[1] * CELL_SIZE))
        bonus.draw(screen)
        portal.draw(screen)

        text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(text, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
