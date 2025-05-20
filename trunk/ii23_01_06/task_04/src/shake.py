import sys
from random import randrange

import pygame

pygame.init()
# =========================Constants===========================
# WIDTH and HEIGHT must be multiple of CELL_SIZE
WIDTH = 1500
HEIGHT = 900
CELL_SIZE = 25
# block_size for better look
BLOCK_SIZE = CELL_SIZE - 1
# -1 for better look
EYE_SIZE = 9 - 1
SOUND_DEATH = pygame.mixer.Sound('resources/death.wav')
SOUND_EAT = pygame.mixer.Sound('resources/mmm.wav')
ICON = pygame.image.load('resources/icon.png')
NOT_BIG_FONT = pygame.font.SysFont('Arial', 22, bold=True)
BIG_FONT = pygame.font.SysFont('Arial', 66, bold=True)
# ==========================Colors=============================
bg1_color = (30, 150, 120)
bg2_color = (30, 159, 120)
bg_fill_color = pygame.Color('gray20')
snake_color = (236, 160, 40)
snake_eyes_color = pygame.Color('white')
food_color = (255, 54, 60)
speed_up_color = (239, 218, 7)
speed_down_color = (134, 173, 247)
wall_color = pygame.Color('gray55')
portals_color = (244, 242, 246)
# =============================================================
pygame.display.set_caption('SHAKE IT')
pygame.display.set_icon(ICON)


class Game:
    def __init__(self):
        self.fps_control = pygame.time.Clock()
        self.fps = 7
        self.score = 0
        self.lives = 3
        self.is_paused = False

    @staticmethod
    def draw_bg(surface):
        for row in range(int(HEIGHT / CELL_SIZE)):
            for column in range(int(WIDTH / CELL_SIZE)):
                if (row + column) % 2 == 0:
                    pygame.draw.rect(surface, bg1_color,
                                     (column * CELL_SIZE, row * CELL_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))
                else:
                    pygame.draw.rect(surface, bg2_color,
                                     (column * CELL_SIZE, row * CELL_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE))

    def refresh_screen(self):
        pygame.display.flip()
        self.fps_control.tick(self.fps)

    def controls_handler(self, snake, buffer):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE]:
                    if not self.is_paused:
                        snake._dx, snake._dy = snake.dx, snake.dy
                        snake.dx, snake.dy = 0, 0
                        self.is_paused = True
                        self.fps_control.tick(10)
                    else:
                        snake.dx, snake.dy = snake._dx, snake._dy
                        self.is_paused = False
                        self.fps_control.tick(10)
                if event.key in [pygame.K_UP, pygame.K_w]:
                    buffer.append('up')
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    buffer.append('down')
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    buffer.append('right')
                if event.key in [pygame.K_LEFT, pygame.K_a]:
                    buffer.append('left')
                # cheats
                if event.key in [pygame.K_x]:
                    snake.length += 1
                    self.score += 1
                if event.key in [pygame.K_c]:
                    self.fps += 1
                if event.key in [pygame.K_v]:
                    self.fps -= 1
                if event.key in [pygame.K_z]:
                    self.lives += 99
                # restart
                if event.key in [pygame.K_SPACE]:
                    main()
            elif event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        if not buffer:
            buffer.append(None)
        return buffer

    def draw_hud(self, surface, game):
        if self.is_paused:
            render_pause = BIG_FONT.render('PAUSE', 1, pygame.Color('black'))
            surface.blit(render_pause, (WIDTH // 2 - 90, HEIGHT // 2 - 10))
        render_score = NOT_BIG_FONT.render(f'Score: {self.score}', 1, pygame.Color('black'))
        render_lives = NOT_BIG_FONT.render(f'Lives: {game.lives}', 1, pygame.Color('black'))
        surface.blit(render_score, (int(CELL_SIZE // 1.5), 2))
        surface.blit(render_lives, (int(WIDTH - CELL_SIZE * 3.5), 2))

    def game_over(self, surface, snake, walls, game, level):
        if snake.check_death(walls):
            game.lives -= 1
            SOUND_DEATH.play()
            if game.lives > 0:
                snake.x, snake.y = level.snake_cords[0], level.snake_cords[1]
                snake.body = [(snake.x, snake.y)]
                snake.dx = 0
                snake.dy = 0
                snake.dirs = 'all'
                snake.length = 1
                game.fps_control.tick(6)
                return
            while True:
                render_end = BIG_FONT.render('PRESS SPACE TO RESTART', 1, pygame.Color('black'))
                surface.fill(bg_fill_color)
                game.draw_bg(surface)
                surface.blit(render_end, (int(WIDTH // 2 - 350), int(HEIGHT // 2.5)))
                self.draw_hud(surface, self)
                pygame.display.flip()
                self.controls_handler(snake, buffer=[])


class Snake:
    def __init__(self, x, y, color, eye_color):
        self.color = color
        self.eye_color = eye_color
        self.x = x
        self.y = y
        self.body = [(self.x, self.y)]
        self.length = 1
        self.dx = 0
        self.dy = 0
        self._dx = 0
        self._dy = 0
        self.dirs = 'all'

    def draw_snake(self, surface):
        # '+- 1 or 2' for perfect snake's eyes looking
        [pygame.draw.rect(surface, self.color,
                          (i, j, BLOCK_SIZE, BLOCK_SIZE)) for i, j in self.body]
        if self.dirs == 'up':
            pygame.draw.rect(surface, self.eye_color,
                             (self.x,
                              self.y + BLOCK_SIZE - EYE_SIZE,
                              EYE_SIZE, EYE_SIZE))
            pygame.draw.rect(surface, self.eye_color,
                             (self.x + BLOCK_SIZE - EYE_SIZE,
                              self.y + BLOCK_SIZE - EYE_SIZE,
                              EYE_SIZE, EYE_SIZE))
        elif self.dirs == 'down':
            pygame.draw.rect(surface, self.eye_color,
                             (self.x,
                              self.y,
                              EYE_SIZE, EYE_SIZE))
            pygame.draw.rect(surface, self.eye_color,
                             (self.x + BLOCK_SIZE - EYE_SIZE,
                              self.y,
                              EYE_SIZE, EYE_SIZE))
        elif self.dirs == 'left':
            pygame.draw.rect(surface, self.eye_color,
                             (self.x + BLOCK_SIZE - EYE_SIZE,
                              self.y, EYE_SIZE, EYE_SIZE))
        elif self.dirs == 'right':
            pygame.draw.rect(surface, self.eye_color,
                             (self.x,
                              self.y,
                              EYE_SIZE, EYE_SIZE))

    def eat_food(self, game, portals, walls, *food):
        for piece in food:
            if self.body[-1] == (piece.x, piece.y):
                SOUND_EAT.play()
                piece.spawn_food(self, walls, portals, *food)
                piece.give_bonus(self, game)

    def move_snake(self, game):
        if not game.is_paused:
            self.x += self.dx * CELL_SIZE
            self.y += self.dy * CELL_SIZE
            self.body.append((self.x, self.y))
            self.body = self.body[-self.length:]

    def change_direction(self, buffer):
        if buffer is not None:
            if buffer[0] == 'up' and self.dirs != 'down':
                self.dx, self.dy = 0, -1
                self.dirs = buffer[0]
            if buffer[0] == 'down' and self.dirs != 'up':
                self.dx, self.dy = 0, 1
                self.dirs = buffer[0]
            if buffer[0] == 'right' and self.dirs != 'left':
                self.dx, self.dy = 1, 0
                self.dirs = buffer[0]
            if buffer[0] == 'left' and self.dirs != 'right':
                self.dx, self.dy = -1, 0
                self.dirs = buffer[0]

    def check_death(self, walls):
        if self.x < 0 \
                or self.x > WIDTH - CELL_SIZE \
                or self.y < 0 \
                or self.y > HEIGHT - CELL_SIZE \
                or len(self.body) != len(set(self.body)) \
                or True in [wall.check_collision_with_wall(self) for wall in walls]:
            return True


class Food:
    def __init__(self, x, y, color):
        self.color = color
        self.x = x
        self.y = y

    def draw_food(self, surface):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))

    def spawn_food(self, snake, portals, walls, *other_food):
        collision = False
        food_cords = []
        portal_cords = []
        for piece in other_food:
            food_cords.append((piece.x, piece.y))
        while not collision:
            x, y = randrange(CELL_SIZE, WIDTH - CELL_SIZE, CELL_SIZE), \
                   randrange(CELL_SIZE, HEIGHT - CELL_SIZE, CELL_SIZE)
            if (x, y) not in snake.body \
                    and (x, y) not in portal_cords \
                    and (x, y) not in food_cords \
                    and (x, y) not in [(wall.x, wall.y) for wall in walls] \
                    and (x, y) not in [(portal.f_x, portal.f_y) for portal in portals] \
                    and (x, y) not in [(portal.s_x, portal.s_y) for portal in portals]:
                self.x = x
                self.y = y
                collision = True

    def give_bonus(self, snake, game):
        game.score += 1
        snake.length += 1


class SpeedUp(Food):
    def give_bonus(self, snake, game):
        game.fps += 1
        game.score += 3


class SpeedDown(Food):
    def give_bonus(self, snake, game):
        # lower fps is bad for game experience
        if game.fps > 3:
            game.fps -= 1
        game.score -= 2


class Portal:
    def __init__(self, first_x, first_y,
                 second_x, second_y,
                 first_color, second_color):
        self.f_color = first_color
        self.s_color = second_color
        self.f_x = first_x
        self.f_y = first_y
        self.s_x = second_x
        self.s_y = second_y

    def draw_portals(self, surface):
        pygame.draw.rect(surface, self.f_color,
                         (self.f_x, self.f_y, BLOCK_SIZE, BLOCK_SIZE))
        pygame.draw.rect(surface, self.s_color,
                         (self.s_x, self.s_y, BLOCK_SIZE, BLOCK_SIZE))

    def collision_with_portal(self, snake):
        if (snake.x, snake.y) == (self.f_x, self.f_y):
            snake.x, snake.y = self.s_x, self.s_y
        elif (snake.x, snake.y) == (self.s_x, self.s_y):
            snake.x, snake.y = self.f_x, self.f_y


class Wall:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color

    def draw_wall(self, surface):
        pygame.draw.rect(surface, self.color,
                         (self.x, self.y, BLOCK_SIZE, BLOCK_SIZE))

    def check_collision_with_wall(self, snake):
        if (self.x, self.y) == (snake.x, snake.y):
            return True


class Level:
    def __init__(self):
        self.type = 1
        self.walls = []
        self.portals = []
        self.snake_cords = (0, 0)

    @staticmethod
    def clear_line(line, start_letter):
        return line.replace(start_letter, '') \
            .replace('(', '') \
            .replace(')', '') \
            .replace(',', '')

    def check_new_level(self, snake, game):
        if snake.length > 5 and game.score > 10 and self.type == 1:
            self.type = 2
            self.walls.clear()
            self.portals.clear()
            return True
        if snake.length > 10 and game.score > 20 and self.type == 2:
            self.type = 3
            self.walls.clear()
            self.portals.clear()
            return True

    def parse_level_txt(self, level, wall, portals):
        # basic snake position if not snake in level
        self.snake_cords = 0, 0
        with open(level, 'r') as file:
            for line in file:
                if line[0] == 'w':
                    line = self.clear_line(line, 'w')
                    x, y = line.split(' ')
                    self.walls.append(Wall(int(x), int(y), wall.color))
                if line[0] == 'p':
                    line = self.clear_line(line, 'p')
                    fx, fy, sx, sy = line.split(' ')
                    self.portals.append(Portal(int(fx), int(fy),
                                               int(sx), int(sy),
                                               portals.f_color,
                                               portals.s_color))
                if line[0] == 's':
                    line = self.clear_line(line, 's')
                    x, y = line.split(' ')
                    self.snake_cords = int(x), int(y)

    def load_level(self, wall, portals):
        if self.type == 1:
            self.parse_level_txt('levels/level1.txt', wall, portals)
        elif self.type == 2:
            self.parse_level_txt('levels/level2.txt', wall, portals)
        elif self.type == 3:
            self.parse_level_txt('levels/level3.txt', wall, portals)


def main():
    game = Game()
    surface = pygame.display.set_mode((WIDTH, HEIGHT))
    p = Portal(0, 0, 0, 0, portals_color, portals_color)
    w = Wall(0, 0, wall_color)
    level = Level()
    buffer = ['all']

    while True:
        level.load_level(w, p)
        snake = Snake(level.snake_cords[0], level.snake_cords[1],
                      snake_color, snake_eyes_color)
        apple = Food(0, 0, food_color)
        speed_up_bonus = SpeedUp(0, 0, speed_up_color)
        speed_down_bonus = SpeedDown(0, 0, speed_down_color)

        # initialize food
        apple.spawn_food(snake, level.portals, level.walls,
                         speed_up_bonus, speed_down_bonus, apple)
        speed_up_bonus.spawn_food(snake, level.portals, level.walls,
                                  speed_up_bonus, speed_down_bonus, apple)
        speed_down_bonus.spawn_food(snake, level.portals, level.walls,
                                    speed_up_bonus, speed_down_bonus, apple)

        while True:
            buffer = game.controls_handler(snake, buffer)
            if len(buffer) > 3:
                buffer.pop(0)
            snake.change_direction(buffer)
            surface.fill(bg_fill_color)
            # drawing bg grid
            game.draw_bg(surface)
            # drawing walls, portals, snake, food,
            [wall.draw_wall(surface) for wall in level.walls]
            [portal.draw_portals(surface) for portal in level.portals]
            snake.draw_snake(surface)
            apple.draw_food(surface)
            speed_up_bonus.draw_food(surface)
            speed_down_bonus.draw_food(surface)
            # show score, lives and pause text
            game.draw_hud(surface, game)
            # entering in portals
            [portal.collision_with_portal(snake) for portal in level.portals]
            # snake movement
            snake.move_snake(game)
            # eating food
            snake.eat_food(game, level.walls, level.portals,
                           apple, speed_up_bonus, speed_down_bonus)
            # screen refresh
            game.refresh_screen()
            # clear buffer
            buffer.pop(0)
            # game over
            game.game_over(surface, snake, level.walls, game, level)
            # transition to new level
            if level.check_new_level(snake, game):
                break


if __name__ == '__main__':
    main()
