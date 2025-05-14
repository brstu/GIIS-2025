import pygame
import random
import time
from collections import deque
from pygame import gfxdraw

# Инициализация Pygame
pygame.init()
WIDTH, HEIGHT = 500, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Пятнашки: Розовый стиль!")

# Цвета
PINK = (255, 182, 193)      # Фон плиток
WHITE = (255, 255, 255)     # Цифры
BLACK = (0, 0, 0)           # Рамки
HOT_PINK = (255, 105, 180)  # Подсказки
MINT = (180, 255, 180)      # Победа

# Параметры игры
tile_size = 90
grid_pos = (50, 150)
board = list(range(1, 16)) + [None]
solved_state = list(range(1, 16)) + [None]
hints_left = 3
moves = 0
game_time = 0
start_time = time.time() 
timer_active = True       
bonus_points = 0
animation = None
hint_tile = None

# Перемешиваем доску (с проверкой на решаемость)
def shuffle_board():
    global board
    while True:
        random.shuffle(board)
        if is_solvable(board):
            break

def is_solvable(board):
    inversions = 0
    for i in range(len(board)):
        for j in range(i + 1, len(board)):
            if board[i] and board[j] and board[i] > board[j]:
                inversions += 1
    return inversions % 2 == 0

# Поиск подсказки (упрощённый алгоритм)
def find_hint():
    empty_pos = board.index(None)
    for tile_pos in get_possible_moves(board):
        new_board = board.copy()
        new_board[empty_pos], new_board[tile_pos] = new_board[tile_pos], new_board[empty_pos]
        if distance_to_solved(new_board) < distance_to_solved(board):
            return tile_pos
    return None

def distance_to_solved(state):
    distance = 0
    for i in range(16):
        if state[i]:
            target_row = (state[i] - 1) // 4
            target_col = (state[i] - 1) % 4
            current_row = i // 4
            current_col = i % 4
            distance += abs(target_row - current_row) + abs(target_col - current_col)
    return distance

# Анимация перемещения
def start_animation(from_pos, to_pos):
    global animation
    animation = {
        "from": from_pos,
        "to": to_pos,
        "progress": 0,
        "direction": ( (to_pos % 4 - from_pos % 4), (to_pos // 4 - from_pos // 4) )
    }

def update_animation():
    global animation, board
    if animation:
        animation["progress"] += 0.20  # Скорость анимации
        if animation["progress"] >= 1:
            board[animation["to"]], board[animation["from"]] = board[animation["from"]], board[animation["to"]]
            animation = None

# Отрисовка плитки с рамкой
def draw_tile(x, y, number, color=PINK, border_color=BLACK, border_width=3):
    pygame.draw.rect(screen, border_color, (x, y, tile_size, tile_size))
    pygame.draw.rect(screen, color, (x + border_width, y + border_width, 
                     tile_size - 2*border_width, tile_size - 2*border_width))
    if number:
        font = pygame.font.SysFont("Comic Sans MS", 45)
        text = font.render(str(number), True, WHITE)
        screen.blit(text, (x + tile_size//2 - text.get_width()//2, 
                          y + tile_size//2 - text.get_height()//2))

# Отрисовка доски
def draw_board():
    for i in range(16):
        if board[i] or (animation and i == animation["from"] and animation["progress"] < 1):
            row, col = i // 4, i % 4
            x = grid_pos[0] + col * tile_size
            y = grid_pos[1] + row * tile_size
            
            if animation and i == animation["from"]:
                dx = animation["direction"][0] * tile_size * animation["progress"]
                dy = animation["direction"][1] * tile_size * animation["progress"]
                x += dx
                y += dy
            
            color = HOT_PINK if i == hint_tile else PINK
            draw_tile(x, y, board[i], color)

# Отрисовка интерфейса
def draw_ui():
    font = pygame.font.SysFont("Comic Sans MS", 29)
    moves_text = font.render(f"Ходы: {moves}", True, BLACK)
    hints_text = font.render(f"Подсказки: {hints_left}", True, BLACK)
    
    # Рассчитываем текущее время игры
    current_time = int(time.time() - start_time) if timer_active else int(game_time)
    time_text = font.render(f"Время: {current_time} с", True, BLACK)
    
    screen.blit(moves_text, (10, 50))
    screen.blit(hints_text, (139, 50))
    screen.blit(time_text, (350, 50))
    
    if bonus_points > 0:
        bonus_text = font.render(f"Бонус: {bonus_points}", True, MINT)
        screen.blit(bonus_text, (200, 100))


# Возможные ходы
def get_possible_moves(state):
    empty_pos = state.index(None)
    moves = []
    if empty_pos % 4 > 0: moves.append(empty_pos - 1)     # Влево
    if empty_pos % 4 < 3: moves.append(empty_pos + 1)     # Вправо
    if empty_pos // 4 > 0: moves.append(empty_pos - 4)    # Вверх
    if empty_pos // 4 < 3: moves.append(empty_pos + 4)    # Вниз
    return moves

# Основной цикл
shuffle_board()
clock = pygame.time.Clock()
running = True

while running:
    screen.fill(WHITE)
    
    if animation:
        update_animation()
    elif board == solved_state and timer_active:  # Таймер останавливается при победе
        game_time = time.time() - start_time
        bonus_points = max(0, 300 - int(game_time))
        timer_active = False
    
    draw_ui()
    draw_board()
    
    if board == solved_state:
        font = pygame.font.SysFont("Comic Sans MS", 60)
        win_text = font.render("Ты победила! ♡", True, MINT)
        screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT - 100))
    
    pygame.display.flip()
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and not animation:
            x, y = pygame.mouse.get_pos()
            col = (x - grid_pos[0]) // tile_size
            row = (y - grid_pos[1]) // tile_size
            
            if 0 <= row < 4 and 0 <= col < 4:
                clicked_pos = row * 4 + col
                empty_pos = board.index(None)
                if clicked_pos in get_possible_moves(board):
                    start_animation(clicked_pos, empty_pos)
                    moves += 1
                    hint_tile = None
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h and hints_left > 0 and not animation:
                hint_tile = find_hint()
                if hint_tile is not None:
                    hints_left -= 1
            
            elif event.key == pygame.K_r:  # Рестарт
                shuffle_board()
                moves = 0
                hints_left = 3
                start_time = time.time()  # Сбрасываем таймер
                timer_active = True       # Включаем таймер заново
                game_time = 0
                bonus_points = 0
                hint_tile = None
                animation = None

pygame.quit()