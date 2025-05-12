import pygame
import secrets

pygame.init()

SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
GRID_WIDTH = SCREEN_WIDTH // BLOCK_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // BLOCK_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
GOLD = (255, 215, 0)

COLORS = [RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW, ORANGE]

SHAPES = [
    [[1], [1], [1], [1]],
    [[1, 1], [1, 1]],
    [[0, 1, 0], [1, 1, 1]],
    [[0, 1, 1], [1, 1, 0]],
    [[1, 1, 0], [0, 1, 1]],
    [[1, 1, 1], [1, 0, 0]],
    [[1, 1, 1], [0, 0, 1]]
]

screen = pygame.display.set_mode((SCREEN_WIDTH + 150, SCREEN_HEIGHT))
pygame.display.set_caption("Tetris")

font = pygame.font.Font(None, 36)

clock = pygame.time.Clock()

def new_piece():
    shape = secrets.choice(SHAPES)
    color = secrets.choice(COLORS)
    return {'shape': shape, 'color': color, 'x': GRID_WIDTH // 2 - len(shape[0]) // 2, 'y': 0}

def check_collision(grid, piece, offset_x=0, offset_y=0):
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                new_x = piece['x'] + x + offset_x
                new_y = piece['y'] + y + offset_y
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT or (new_y >= 0 and grid[new_y][new_x]):
                    return True
    return False

def update_grid(grid, piece):
    bonus_activated = False
    for y, row in enumerate(piece['shape']):
        for x, cell in enumerate(row):
            if cell:
                grid[piece['y'] + y][piece['x'] + x] = piece['color']
                if grid[piece['y'] + y][piece['x'] + x] == GOLD:
                    bonus_activated = True
    return grid, bonus_activated

def clear_lines(grid):
    full_rows = [i for i, row in enumerate(grid) if all(row)]
    for row in full_rows:
        del grid[row]
        grid.insert(0, [None] * GRID_WIDTH)
    return len(full_rows)

def activate_bonus(grid, x, y):
    for i in range(-1, 2):
        if 0 <= y + i < GRID_HEIGHT:
            grid[y + i] = [None] * GRID_WIDTH
    for i in range(-1, 2):
        if 0 <= x + i < GRID_WIDTH:
            for row in grid:
                row[x + i] = None

def draw_grid(grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell:
                pygame.draw.rect(screen, cell, (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    for x in range(GRID_WIDTH):
        pygame.draw.line(screen, WHITE, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(GRID_HEIGHT):
        pygame.draw.line(screen, WHITE, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

def draw_text(text, x, y, color=WHITE):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (x, y))

def main():
    grid = [[None] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
    current_piece = new_piece()
    next_piece = new_piece()
    fall_time = 0
    fall_speed = 500
    score = 0
    combo_multiplier = 1
    last_clear_time = pygame.time.get_ticks()
    combo_bonus = 0

    running = True
    while running:
        screen.fill(BLACK)
        fall_time += clock.get_rawtime()
        clock.tick()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not check_collision(grid, current_piece, -1, 0):
                    current_piece['x'] -= 1
                if event.key == pygame.K_RIGHT and not check_collision(grid, current_piece, 1, 0):
                    current_piece['x'] += 1
                if event.key == pygame.K_DOWN:
                    if not check_collision(grid, current_piece, 0, 1):
                        current_piece['y'] += 1
                if event.key == pygame.K_UP:  # Поворот
                    rotated = list(zip(*current_piece['shape'][::-1]))
                    if not check_collision(grid, {'shape': rotated, 'x': current_piece['x'], 'y': current_piece['y']}, 0, 0):
                        current_piece['shape'] = rotated

        if fall_time > fall_speed:
            fall_time = 0
            if not check_collision(grid, current_piece, 0, 1):
                current_piece['y'] += 1
            else:
                grid, bonus_activated = update_grid(grid, current_piece)
                cleared_lines = clear_lines(grid)
                current_time = pygame.time.get_ticks()

                if cleared_lines > 0:
                    if current_time - last_clear_time < 5000:
                        combo_multiplier += 1
                        combo_bonus += 10 * combo_multiplier
                    else:
                        combo_multiplier = 1
                        combo_bonus = 0
                    last_clear_time = current_time
                    score += cleared_lines * 10 * combo_multiplier + combo_bonus

                    if secrets.randbits() < 0.2:
                        bonus_placed = False
                        attempts = 0
                        while not bonus_placed and attempts < 100:
                            bonus_x = secrets.randbelow(GRID_WIDTH)
                            bonus_y = secrets.randbelow(GRID_HEIGHT)
                            if grid[bonus_y][bonus_x] is None:
                                grid[bonus_y][bonus_x] = GOLD
                                bonus_placed = True
                            attempts += 1

                else:
                    combo_multiplier = 1
                    combo_bonus = 0

                if bonus_activated:
                    for y, row in enumerate(grid):
                        for x, cell in enumerate(row):
                            if cell == GOLD:
                                activate_bonus(grid, x, y)

                if not check_collision(grid, next_piece):
                    current_piece = next_piece
                    next_piece = new_piece()
                else:
                    running = False

        draw_grid(grid)
        for y, row in enumerate(current_piece['shape']):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(screen, current_piece['color'],
                                     ((current_piece['x'] + x) * BLOCK_SIZE,
                                      (current_piece['y'] + y) * BLOCK_SIZE,
                                      BLOCK_SIZE, BLOCK_SIZE), 0)

        draw_text(f"Score: {score}", SCREEN_WIDTH + 10, 20)
        draw_text(f"Combo: x{combo_multiplier}", SCREEN_WIDTH + 10, 60)
        draw_text(f"Bonus: {combo_bonus}", SCREEN_WIDTH + 10, 100)

        pygame.display.flip()

    print(f"Game Over! Your score: {score}")
    pygame.quit()

if __name__ == "__main__":
    main()