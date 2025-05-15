import pygame

# Получаем разрешение экрана
pygame.init()
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
pygame.quit()

# Устанавливаем размеры окна (90% от экрана)
WINDOW_WIDTH = int(SCREEN_WIDTH * 0.9)
WINDOW_HEIGHT = int(SCREEN_HEIGHT * 0.9)
WINDOW_SIZE = min(WINDOW_WIDTH, WINDOW_HEIGHT)

# Размеры сетки (30 клеток по меньшей стороне)
GRID_SIZE = WINDOW_SIZE // 30
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (250,152,155)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BACKGROUND_COLOR = (201,252,225)
GRID_COLOR = (115,248,177)
PINK = (250,152,204)
CORAL =(250,152,155)

# Размеры спрайтов (адаптивные)
SPRITE_WIDTH = GRID_SIZE
SPRITE_HEIGHT = GRID_SIZE