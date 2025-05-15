import pygame
import secrets
import sys
import json
import os
from constants import *
from sprites import load_sprites
from entities import Snake, Food, PowerUp, Portal, Brick, PowerUpType


def weighted_choice(choices, weights):
    # Преобразуем веса в целые числа, умножая на 100 для сохранения точности
    weights = [int(w * 100) for w in weights]
    total = sum(weights)
    r = secrets.randbelow(total)
    upto = 0
    for c, w in zip(choices, weights):
        if upto + w > r:
            return c
        upto += w
    return choices[-1]


class Game:
    def __init__(self):
        pygame.init()

        pygame.mixer.init()
        pygame.mixer.music.load('background_music.mp3')  # путь к твоему музыкальному файлу
        pygame.mixer.music.set_volume(0.5)  # громкость от 0.0 до 1.0
        pygame.mixer.music.play(-1)  # -1 означает бесконечное повторение

        self.portal_sound = pygame.mixer.Sound('portal.mp3')  # Добавьте файл portal.wav
        self.death_sound = pygame.mixer.Sound('death.mp3')  # Добавьте файл death.wav

        # Используем размеры из constants.py
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()

        self.sprites = load_sprites()

        self.snake = Snake()
        self.foods = []
        self.bricks = []
        self.power_up = None
        self.blue_portal_start = None
        self.blue_portal_end = None
        self.red_portal_start = None
        self.red_portal_end = None
        self.game_over = False
        self.difficulty_selected = False
        self.selected_difficulty = None

        # Адаптивные размеры шрифтов
        self.font = pygame.font.Font(None, int(WINDOW_HEIGHT * 0.07))
        self.title_font = pygame.font.Font(None, int(WINDOW_HEIGHT * 0.12))
        self.small_font = pygame.font.Font(None, int(WINDOW_HEIGHT * 0.035))

        # Сетка с учетом динамических размеров
        self.grid_surface = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        for x in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(self.grid_surface, GRID_COLOR, (x, 0), (x, WINDOW_SIZE), 2)
        for y in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(self.grid_surface, GRID_COLOR, (0, y), (WINDOW_SIZE, y), 2)

        self.create_map()
        self.spawn_portals()
        self.spawn_foods()

        self.high_scores = self.load_high_scores()

    def load_high_scores(self):
        if os.path.exists('high_scores.json'):
            with open('high_scores.json', 'r') as f:
                return json.load(f)
        return {"Easy": 0, "Medium": 0, "Hard": 0}

    def save_high_scores(self):
        with open('high_scores.json', 'w') as f:
            json.dump(self.high_scores, f)

    def update_high_score(self):
        difficulty = self.selected_difficulty["name"]
        if self.snake.score > self.high_scores[difficulty]:
            self.high_scores[difficulty] = self.snake.score
            self.save_high_scores()

    def create_map(self):
        self.bricks = []

        # Сначала создаем границы карты (неизменные)
        for x in range(GRID_COUNT):
            self.bricks.append(Brick(x, 0, self.sprites['brick']))
            self.bricks.append(Brick(x, GRID_COUNT - 1, self.sprites['brick']))
        for y in range(GRID_COUNT):
            self.bricks.append(Brick(0, y, self.sprites['brick']))
            self.bricks.append(Brick(GRID_COUNT - 1, y, self.sprites['brick']))

        # Параметры для генерации случайных стен
        num_walls = 8  # Количество стен
        min_wall_length = 2  # Минимальная длина стены
        max_wall_length = 5  # Максимальная длина стены
        margin = 2  # Отступ от границ

        for _ in range(num_walls):
            # Выбираем случайное направление (0 - горизонтально, 1 - вертикально)
            direction = secrets.randbelow(2)

            if direction == 0:  # Горизонтальная стена
                wall_length = secrets.randbelow(max_wall_length - min_wall_length + 1) + min_wall_length
                x = secrets.randbelow(GRID_COUNT - margin * 2 - wall_length) + margin
                y = secrets.randbelow(GRID_COUNT - margin * 2) + margin

                for i in range(wall_length):
                    if (x + i, y) not in [(b.x, b.y) for b in self.bricks]:  # Проверка на пересечение
                        self.bricks.append(Brick(x + i, y, self.sprites['brick']))

            else:  # Вертикальная стена
                wall_length = secrets.randbelow(max_wall_length - min_wall_length + 1) + min_wall_length
                x = secrets.randbelow(GRID_COUNT - margin * 2) + margin
                y = secrets.randbelow(GRID_COUNT - margin * 2 - wall_length) + margin

                for i in range(wall_length):
                    if (x, y + i) not in [(b.x, b.y) for b in self.bricks]:  # Проверка на пересечение
                        self.bricks.append(Brick(x, y + i, self.sprites['brick']))

    def spawn_single_food(self):
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            position = (secrets.randbelow(GRID_COUNT), secrets.randbelow(GRID_COUNT))

            is_snake = position in self.snake.positions
            is_food = position in [(food.x, food.y) for food in self.foods]
            is_brick = position in [(brick.x, brick.y) for brick in self.bricks]
            is_portal = (
                    position == (self.blue_portal_start.x, self.blue_portal_start.y) or
                    position == (self.blue_portal_end.x, self.blue_portal_end.y) or
                    position == (self.red_portal_start.x, self.red_portal_start.y) or
                    position == (self.red_portal_end.x, self.red_portal_end.y)
            )

            if not (is_snake or is_food or is_brick or is_portal):
                if secrets.randbelow(10) < 1:  # 10% шанс
                    food_type = 'gold_apple'
                else:
                    food_type = secrets.choice(['apple', 'cherry', 'cookie'])
                self.foods.append(Food(position[0], position[1], food_type, self.sprites[food_type]))
                return

            attempts += 1

    def spawn_foods(self):
        self.foods = []
        for _ in range(7):
            self.spawn_single_food()

    def spawn_power_up(self):
        max_attempts = 100
        attempts = 0

        while attempts < max_attempts:
            position = (secrets.randbelow(GRID_COUNT), secrets.randbelow(GRID_COUNT))

            is_snake = position in self.snake.positions
            is_food = position in [(food.x, food.y) for food in self.foods]
            is_brick = position in [(brick.x, brick.y) for brick in self.bricks]
            is_portal = (
                    position == (self.blue_portal_start.x, self.blue_portal_start.y) or
                    position == (self.blue_portal_end.x, self.blue_portal_end.y) or
                    position == (self.red_portal_start.x, self.red_portal_start.y) or
                    position == (self.red_portal_end.x, self.red_portal_end.y)
            )

            if not (is_snake or is_food or is_brick or is_portal):
                base_speed = self.selected_difficulty["speed"]
                if base_speed <= 5:
                    power_type = weighted_choice(
                        [PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.INVINCIBLE],
                        [0.5, 0.2, 0.3]
                    )
                elif base_speed <= 10:
                    power_type = weighted_choice(
                        [PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.INVINCIBLE],
                        [0.3, 0.4, 0.3]
                    )
                else:
                    power_type = weighted_choice(
                        [PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.INVINCIBLE],
                        [0.2, 0.5, 0.3]
                    )

                sprite_key = f'powerup_{power_type.name.lower()}'
                self.power_up = PowerUp(position[0], position[1], power_type, self.sprites[sprite_key])
                return

            attempts += 1

    def handle_power_up(self):
        if self.power_up and self.snake.get_head_position() == (self.power_up.x, self.power_up.y):
            existing_power_up = next((p for p in self.snake.power_ups if p.type == self.power_up.type), None)

            if existing_power_up:
                remaining_time = existing_power_up.get_remaining_time()
                existing_power_up.duration = remaining_time + self.power_up.duration
                existing_power_up.start_time = pygame.time.get_ticks()
            else:
                self.power_up.active = True
                self.power_up.start_time = pygame.time.get_ticks()

                base_speed = self.selected_difficulty["speed"]
                if self.power_up.type == PowerUpType.SPEED:
                    self.snake.speed = int(base_speed * 1.5)
                elif self.power_up.type == PowerUpType.SLOW:
                    self.snake.speed = int(base_speed * 0.5)
                elif self.power_up.type == PowerUpType.INVINCIBLE:
                    self.snake.invincible = True

                self.snake.power_ups.append(self.power_up)

            self.power_up = None

    def spawn_portals(self):
        self.blue_portal_start = Portal(2, 2, True, 'blue')
        self.blue_portal_end = Portal(GRID_COUNT - 3, GRID_COUNT - 3, False, 'blue')
        self.red_portal_start = Portal(2, GRID_COUNT - 3, True, 'red')
        self.red_portal_end = Portal(GRID_COUNT - 3, 2, False, 'red')

    def update_power_ups(self):
        current_time = pygame.time.get_ticks()
        for power_up in self.snake.power_ups[:]:
            if current_time - power_up.start_time > power_up.duration:
                if power_up.type == PowerUpType.SPEED:
                    self.snake.speed = self.selected_difficulty["speed"]
                elif power_up.type == PowerUpType.SLOW:
                    self.snake.speed = self.selected_difficulty["speed"]
                elif power_up.type == PowerUpType.INVINCIBLE:
                    self.snake.invincible = False
                self.snake.power_ups.remove(power_up)

    def draw_power_up_timers(self):
        start_x = 40  # Отступ слева
        start_y = 170  # Начинаем ниже заголовка "Power Ups"

        for i, power_up in enumerate(self.snake.power_ups):
            remaining_time = power_up.get_remaining_time() / 1000
            if remaining_time > 0:
                if power_up.type == PowerUpType.SPEED:
                    text = f"Speed: {remaining_time:.1f}s"
                    color = WHITE
                elif power_up.type == PowerUpType.SLOW:
                    text = f"Slow: {remaining_time:.1f}s"
                    color = WHITE
                elif power_up.type == PowerUpType.INVINCIBLE:
                    text = f"Invincible: {remaining_time:.1f}s"
                    color = WHITE

                timer_text = self.small_font.render(text, True, color)
                self.screen.blit(timer_text, (start_x, start_y + i * 30))  # i * 30 - отступ между улучшениями

    def initialize_game(self):

        self.snake = Snake()
        self.foods = []
        self.bricks = []
        self.power_up = None
        self.blue_portal_start = None
        self.blue_portal_end = None
        self.red_portal_start = None
        self.red_portal_end = None
        self.game_over = False

        self.snake.speed = self.selected_difficulty["speed"]

        self.create_map()
        self.spawn_portals()
        self.spawn_foods()

    def show_difficulty_screen(self):
        # Загрузка фонового изображения (один раз при инициализации)
        try:
            background_image = pygame.image.load('images/menu_background.jpg').convert()
            # Масштабируем изображение под размер экрана
            background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        except:
            background_image = None
            print("Не удалось загрузить фоновое изображение, будет использован цветной фон")

        difficulties = [
            {"name": "Easy", "speed": 5},
            {"name": "Medium", "speed": 10},
            {"name": "Hard", "speed": 15}
        ]

        # Параметры кнопок
        button_width = 300
        button_height = 80
        button_margin = 30  # Расстояние между кнопками

        # Рассчитываем общую высоту всех кнопок с отступами
        total_height = (button_height * len(difficulties)) + (button_margin * (len(difficulties) - 1))

        # Начальная позиция Y для первой кнопки (центрирование по вертикали)
        start_y = (WINDOW_HEIGHT - total_height) // 1.4

        buttons = []
        for i, diff in enumerate(difficulties):
            # Центрирование по горизонтали: (ширина экрана - ширина кнопки) / 2
            button_x = (WINDOW_WIDTH - button_width) // 2.47 #2.5
            button_y = start_y + i * (button_height + button_margin)

            button_rect = pygame.Rect(
                button_x,
                button_y,
                button_width,
                button_height
            )
            buttons.append({"rect": button_rect, "difficulty": diff})

        while not self.difficulty_selected:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    for button in buttons:
                        if button["rect"].collidepoint(mouse_pos):
                            self.selected_difficulty = button["difficulty"]
                            self.difficulty_selected = True
                            self.initialize_game()
                            return
            if background_image:
                self.screen.blit(background_image, (0, 0))  # Рисуем изображение на весь экран
            else:
                self.screen.fill(BACKGROUND_COLOR)


            # Отрисовка
            #self.screen.fill(BACKGROUND_COLOR)

            # Загрузка и отображение логотипа вместо текстового заголовка
            try:
                # Загружаем логотип (предполагается, что файл logo.png находится в папке images)
                logo = pygame.image.load('images/logo.png').convert_alpha()

                # Масштабируем логотип (подбирайте размеры под ваш логотип)
                logo_width = 650  # Ширина логотипа
                logo_height = 250  # Высота логотипа
                logo = pygame.transform.scale(logo, (logo_width, logo_height))

                # Позиционируем логотип (центрируем по горизонтали)
                logo_rect = logo.get_rect(center=(WINDOW_WIDTH // 2.4, start_y - 220)) #2.5
                self.screen.blit(logo, logo_rect)

            except Exception as e:
                # Если логотип не загрузился, отображаем текст как запасной вариант
                print(f"Не удалось загрузить логотип: {e}")
                title_text = self.title_font.render("Snake", True, WHITE)
                title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2.4, start_y - 100)) #2.5
                self.screen.blit(title_text, title_rect)

            # Подзаголовок (необязательно)
            subtitle_text = self.font.render("Выберите уровень сложности", True, WHITE)
            subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2.4, start_y - 40)) #2.5
            self.screen.blit(subtitle_text, subtitle_rect)

            # Отрисовка кнопок
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons:
                is_hovered = button["rect"].collidepoint(mouse_pos)

                # Цвет контура (желтый при наведении, белый в обычном состоянии)
                border_color = YELLOW if is_hovered else WHITE

                # Создаем поверхность с прозрачностью
                button_surface = pygame.Surface((button_width, button_height), pygame.SRCALPHA)

                # Рисуем контур (толщина 3 пикселя)
                pygame.draw.rect(button_surface, border_color, (0, 0, button_width, button_height), 3)

                # Отображаем поверхность с кнопкой
                self.screen.blit(button_surface, button["rect"])

                # Текст кнопки (центрированный внутри кнопки)
                text = self.font.render(button["difficulty"]["name"], True, border_color)  # Цвет текста как у контура
                text_rect = text.get_rect(center=button["rect"].center)
                self.screen.blit(text, text_rect)

            pygame.display.flip()
            self.clock.tick(60)

    def reset_game(self):
        self.initialize_game()

    def show_game_over_screen(self):

        if not hasattr(self, 'death_sound_played'):
            self.death_sound.play()
            self.death_sound.set_volume(1)
            self.death_sound_played = True

        button_height = 80
        button_width = 300
        button_margin = 20

        restart_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2.62,
            WINDOW_HEIGHT // 2 + 20,
            button_width,
            button_height
        )

        menu_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2.62,
            WINDOW_HEIGHT // 2 + button_height + button_margin + 20,
            button_width,
            button_height
        )

        exit_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2.62,
            WINDOW_HEIGHT // 2 + (button_height + button_margin) * 2 + 20,
            button_width,
            button_height
        )

        self.update_high_score()

        while self.game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if restart_button.collidepoint(mouse_pos):
                        self.reset_game()
                        return
                    elif menu_button.collidepoint(mouse_pos):
                        self.difficulty_selected = False
                        self.show_difficulty_screen()
                        return
                    elif exit_button.collidepoint(mouse_pos):
                        pygame.quit()
                        sys.exit()

            self.screen.fill(BACKGROUND_COLOR)

            game_surface = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
            game_surface.fill(BACKGROUND_COLOR)
            game_surface.blit(self.grid_surface, (0, 0))

            for brick in self.bricks:
                brick.draw(game_surface)

            for food in self.foods:
                food.draw(game_surface)

            if self.power_up:
                self.power_up.draw(game_surface)

            self.snake.draw(game_surface, self.sprites)

            if self.blue_portal_start:
                self.blue_portal_start.draw(game_surface)
            if self.blue_portal_end:
                self.blue_portal_end.draw(game_surface)
            if self.red_portal_start:
                self.red_portal_start.draw(game_surface)
            if self.red_portal_end:
                self.red_portal_end.draw(game_surface)

            x_offset = (WINDOW_WIDTH - WINDOW_SIZE) // 2.45
            y_offset = (WINDOW_HEIGHT - WINDOW_SIZE) // 2
            self.screen.blit(game_surface, (x_offset, y_offset))

            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))

            title_size = int(WINDOW_HEIGHT * 0.15)
            score_size = int(WINDOW_HEIGHT * 0.08)

            title_font = pygame.font.Font(None, title_size)
            score_font = pygame.font.Font(None, score_size)

            game_over_text = title_font.render('Game Over!', True, PINK)
            self.screen.blit(game_over_text, (WINDOW_WIDTH // 2.45 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 6))

            score_text = score_font.render(f'Score: {self.snake.score}', True, PINK)
            self.screen.blit(score_text,
                             (WINDOW_WIDTH // 2.45 - score_text.get_width() // 2, WINDOW_HEIGHT // 6 + title_size))

            high_score_text = score_font.render(f'High Score: {self.high_scores[self.selected_difficulty["name"]]}',
                                                True, PINK)
            self.screen.blit(high_score_text, (
            WINDOW_WIDTH // 2.45 - high_score_text.get_width() // 2, WINDOW_HEIGHT // 6 + title_size + score_size))

            mouse_pos = pygame.mouse.get_pos()

            is_hovered = restart_button.collidepoint(mouse_pos)
            if is_hovered:
                shadow_rect = restart_button.copy()
                shadow_rect.x += 5
                shadow_rect.y += 5
                pygame.draw.rect(self.screen, PINK, shadow_rect, 2)
                pygame.draw.rect(self.screen, (100, 100, 100), restart_button, 2)
            else:
                pygame.draw.rect(self.screen, WHITE, restart_button, 2)
            restart_text = self.font.render("Play Again", True, WHITE)
            restart_text_rect = restart_text.get_rect(center=restart_button.center)
            self.screen.blit(restart_text, restart_text_rect)

            is_hovered = menu_button.collidepoint(mouse_pos)
            if is_hovered:
                shadow_rect = menu_button.copy()
                shadow_rect.x += 5
                shadow_rect.y += 5
                pygame.draw.rect(self.screen, PINK, shadow_rect, 2)
                pygame.draw.rect(self.screen, (100, 100, 100), menu_button, 2)
            else:
                pygame.draw.rect(self.screen, WHITE, menu_button, 2)
            menu_text = self.font.render("Menu", True, WHITE)
            menu_text_rect = menu_text.get_rect(center=menu_button.center)
            self.screen.blit(menu_text, menu_text_rect)

            is_hovered = exit_button.collidepoint(mouse_pos)
            if is_hovered:
                shadow_rect = exit_button.copy()
                shadow_rect.x += 5
                shadow_rect.y += 5
                pygame.draw.rect(self.screen, PINK, shadow_rect, 2)
                pygame.draw.rect(self.screen, (100, 100, 100), exit_button, 2)
            else:
                pygame.draw.rect(self.screen, WHITE, exit_button, 2)
            exit_text = self.font.render("Exit", True, WHITE)
            exit_text_rect = exit_text.get_rect(center=exit_button.center)
            self.screen.blit(exit_text, exit_text_rect)

            pygame.display.flip()
            self.clock.tick(60)

    def run(self):
        power_up_timer = 0

        self.show_difficulty_screen()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
                    current_direction = self.snake.direction
                    if event.key == pygame.K_w and current_direction != (0, 1):
                        self.snake.direction = (0, -1)
                    elif event.key == pygame.K_s and current_direction != (0, -1):
                        self.snake.direction = (0, 1)
                    elif event.key == pygame.K_a and current_direction != (1, 0):
                        self.snake.direction = (-1, 0)
                    elif event.key == pygame.K_d and current_direction != (-1, 0):
                        self.snake.direction = (1, 0)

            if not self.game_over:
                head_pos = self.snake.get_head_position()
                x, y = self.snake.direction
                new_pos = ((head_pos[0] + x) % GRID_COUNT, (head_pos[1] + y) % GRID_COUNT)

                if any(brick.x == new_pos[0] and brick.y == new_pos[1] for brick in self.bricks):
                    if not self.snake.invincible:
                        self.game_over = True
                        self.show_game_over_screen()
                        continue
                    else:
                        continue

                if not self.snake.update(self.blue_portal_start):
                    self.game_over = True
                    self.show_game_over_screen()
                    continue

                head_pos = self.snake.get_head_position()

                for food in self.foods[:]:
                    if (food.x, food.y) == head_pos:
                        if food.type == 'gold_apple':
                            self.snake.length += 3
                            self.snake.score += 3
                        else:
                            self.snake.length += 1
                            self.snake.score += 1
                        self.foods.remove(food)
                        self.spawn_single_food()
                        break

                power_up_timer += 1
                if power_up_timer >= 30:
                    if not self.power_up:
                        self.spawn_power_up()
                    power_up_timer = 0

                if self.power_up:
                    if self.power_up.should_disappear():
                        self.power_up = None
                    else:
                        if head_pos == (self.power_up.x, self.power_up.y):
                            self.handle_power_up()

                if self.blue_portal_start and head_pos == (self.blue_portal_start.x, self.blue_portal_start.y):
                    self.snake.positions[0] = (self.blue_portal_end.x, self.blue_portal_end.y)
                    self.portal_sound.play()

                if self.red_portal_start and head_pos == (self.red_portal_start.x, self.red_portal_start.y):
                    self.snake.positions[0] = (self.red_portal_end.x, self.red_portal_end.y)
                    self.portal_sound.play()

                self.update_power_ups()

            self.screen.fill(BACKGROUND_COLOR)

            game_surface = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
            game_surface.fill(BACKGROUND_COLOR)
            game_surface.blit(self.grid_surface, (0, 0))

            # Отрисовка игровых объектов
            for brick in self.bricks:
                brick.draw(game_surface)
            for food in self.foods:
                food.draw(game_surface)
            if self.power_up:
                self.power_up.draw(game_surface)
            self.snake.draw(game_surface, self.sprites)

            if self.blue_portal_start:
                self.blue_portal_start.draw(game_surface)
            if self.blue_portal_end:
                self.blue_portal_end.draw(game_surface)
            if self.red_portal_start:
                self.red_portal_start.draw(game_surface)
            if self.red_portal_end:
                self.red_portal_end.draw(game_surface)

            x_offset = (WINDOW_WIDTH - WINDOW_SIZE) // 2
            y_offset = (WINDOW_HEIGHT - WINDOW_SIZE) // 2
            self.screen.blit(game_surface, (x_offset, y_offset))

            # Отрисовка панелей интерфейса
            panel_width = 200
            panel_margin = 20

            # 1. Панель счета
            score_panel = pygame.Rect(
                panel_margin,
                panel_margin,
                panel_width,
                80
            )
            pygame.draw.rect(self.screen, CORAL, score_panel, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, score_panel, 2, border_radius=10)
            score_text = self.font.render(f'Score: {self.snake.score}', True, WHITE)
            self.screen.blit(score_text, (panel_margin + 20, panel_margin + 20))

            # 2. Панель улучшений
            powerups_panel = pygame.Rect(
                panel_margin,
                panel_margin + 100,
                panel_width,
                150
            )
            pygame.draw.rect(self.screen, CORAL, powerups_panel, border_radius=10)
            pygame.draw.rect(self.screen, WHITE, powerups_panel, 2, border_radius=10)
            powerups_title = self.small_font.render("Power Ups:", True, WHITE)
            self.screen.blit(powerups_title, (panel_margin + 20, panel_margin + 120))

            # 3. Отрисовка самих улучшений (ПЕРЕМЕЩЕНО ПОСЛЕ ОТРИСОВКИ ПАНЕЛЕЙ)
            self.draw_power_up_timers()

            pygame.display.flip()
            self.clock.tick(self.snake.speed)


if __name__ == '__main__':
    game = Game()
    game.run() 