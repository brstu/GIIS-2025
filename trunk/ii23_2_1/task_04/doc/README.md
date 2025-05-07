# Лабораторная работа 4-5

## Тема: "Разработка игр"

## Цель работы

 Создать игровые проекты с сохранением канонического визуала и механик, дополнив их уникальными особенностями для расширения игрового опыта и стратегической глубины.

## Основные требования

1. Канонический визуал и базовый игровой процесс.
2. Две уникальные игровые особенности, которые:
   - Органично вписываются в оригинальную механику.  
   - Добавляют стратегический или тактический элемент.
   - Повышают реиграбельность или сложность.
    
## Оценка работы:
1. Соответствие каноническому стилю.  
2. Устойчивость новых механик к балансу.  
3. Креативность и влияние особенностей на игровой опыт.

## Вариант 1 - Snake
 Модели объектов для игры нарисован вручную в Paint и находятся в папке src/images
### Реализованы следующие функции:
- Выбор сложности игры
- Телепорты
- Припятствия в виде кирпичей
- Дополнительные механики для змейки (ускорение ![](../src/images/speed.png), замедление ![](../src/images/slow.png), неуязвимость ![](../src/images/invulnerability.png))
- Сохранение рекордов на разных сложностях

## Код программы
### game.py:
```
import pygame
import random
import sys
import json
import os
from constants import *
from sprites import load_sprites
from entities import Snake, Food, PowerUp, Portal, Brick, PowerUpType

class Game:
    def __init__(self):
        pygame.init()
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
        
        self.font = pygame.font.Font(None, 72)
        self.title_font = pygame.font.Font(None, 120)
        self.small_font = pygame.font.Font(None, 36)
        
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
        
        for x in range(GRID_COUNT):
            self.bricks.append(Brick(x, 0, self.sprites['brick']))
            self.bricks.append(Brick(x, GRID_COUNT-1, self.sprites['brick']))
        for y in range(GRID_COUNT):
            self.bricks.append(Brick(0, y, self.sprites['brick']))
            self.bricks.append(Brick(GRID_COUNT-1, y, self.sprites['brick']))

        wall_length = 3
        gap_length = 4
        margin = 3

        for x in range(margin, GRID_COUNT-margin, wall_length + gap_length):
            for i in range(wall_length):
                if x + i < GRID_COUNT - margin:
                    self.bricks.append(Brick(x + i, margin, self.sprites['brick']))

        for x in range(margin, GRID_COUNT-margin, wall_length + gap_length):
            for i in range(wall_length):
                if x + i < GRID_COUNT - margin:
                    self.bricks.append(Brick(x + i, GRID_COUNT-margin-1, self.sprites['brick']))

        for y in range(margin, GRID_COUNT-margin, wall_length + gap_length):
            for i in range(wall_length):
                if y + i < GRID_COUNT - margin:
                    self.bricks.append(Brick(margin, y + i, self.sprites['brick']))

        for y in range(margin, GRID_COUNT-margin, wall_length + gap_length):
            for i in range(wall_length):
                if y + i < GRID_COUNT - margin:
                    self.bricks.append(Brick(GRID_COUNT-margin-1, y + i, self.sprites['brick']))

    def spawn_single_food(self):
        max_attempts = 100
        attempts = 0
        
        while attempts < max_attempts:
            position = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            
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
                if random.random() < 0.1:
                    food_type = 'gold_apple'
                else:
                    food_type = random.choice(['apple', 'cherry', 'cookie'])
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
            position = (random.randint(0, GRID_COUNT-1), random.randint(0, GRID_COUNT-1))
            
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
                    power_type = random.choices(
                        [PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.INVINCIBLE],
                        weights=[0.5, 0.2, 0.3]
                    )[0]
                elif base_speed <= 10:  
                    power_type = random.choices(
                        [PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.INVINCIBLE],
                        weights=[0.3, 0.4, 0.3]
                    )[0]
                else:  
                    power_type = random.choices(
                        [PowerUpType.SPEED, PowerUpType.SLOW, PowerUpType.INVINCIBLE],
                        weights=[0.2, 0.5, 0.3]
                    )[0]
                
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
        self.blue_portal_end = Portal(GRID_COUNT-3, GRID_COUNT-3, False, 'blue')
        self.red_portal_start = Portal(2, GRID_COUNT-3, True, 'red')
        self.red_portal_end = Portal(GRID_COUNT-3, 2, False, 'red')

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
        y_offset = 100
        for power_up in self.snake.power_ups:
            remaining_time = power_up.get_remaining_time() / 1000
            if remaining_time > 0:
                if power_up.type == PowerUpType.SPEED:
                    text = f"Speed: {remaining_time:.1f}s"
                    color = GREEN
                elif power_up.type == PowerUpType.SLOW:
                    text = f"Slow: {remaining_time:.1f}s"
                    color = RED
                elif power_up.type == PowerUpType.INVINCIBLE:
                    text = f"Invincible: {remaining_time:.1f}s"
                    color = BLUE
                
                timer_text = self.small_font.render(text, True, color)
                self.screen.blit(timer_text, (20, y_offset))
                y_offset += 40

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
        difficulties = [
            {"name": "Easy", "speed": 5},
            {"name": "Medium", "speed": 10},
            {"name": "Hard", "speed": 15}
        ]
        
        button_height = 80
        button_width = 300
        button_margin = 20
        total_height = len(difficulties) * (button_height + button_margin)
        start_y = (WINDOW_HEIGHT - total_height) // 2
        
        buttons = []
        for i, diff in enumerate(difficulties):
            button_rect = pygame.Rect(
                (WINDOW_WIDTH - button_width) // 2,
                start_y + i * (button_height + button_margin),
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
            
            self.screen.fill(BACKGROUND_COLOR)
            
            title_text = self.title_font.render("Snake", True, WHITE)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, start_y - 100))
            self.screen.blit(title_text, title_rect)
            
            mouse_pos = pygame.mouse.get_pos()
            for button in buttons:
                is_hovered = button["rect"].collidepoint(mouse_pos)
                
                if is_hovered:
                    shadow_rect = button["rect"].copy()
                    shadow_rect.x += 5
                    shadow_rect.y += 5
                    pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, 2)
                    pygame.draw.rect(self.screen, (100, 100, 100), button["rect"], 2)
                else:
                    pygame.draw.rect(self.screen, WHITE, button["rect"], 2)
                
                text = self.font.render(button["difficulty"]["name"], True, WHITE)
                text_rect = text.get_rect(center=button["rect"].center)
                self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(60)

    def reset_game(self):
        self.initialize_game()

    def show_game_over_screen(self):
        button_height = 80
        button_width = 300
        button_margin = 20
        
        restart_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            WINDOW_HEIGHT // 2 + 20,
            button_width,
            button_height
        )
        
        menu_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
            WINDOW_HEIGHT // 2 + button_height + button_margin + 20,
            button_width,
            button_height
        )
        
        exit_button = pygame.Rect(
            (WINDOW_WIDTH - button_width) // 2,
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
            
            x_offset = (WINDOW_WIDTH - WINDOW_SIZE) // 2
            y_offset = (WINDOW_HEIGHT - WINDOW_SIZE) // 2
            self.screen.blit(game_surface, (x_offset, y_offset))
            
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            title_size = int(WINDOW_HEIGHT * 0.15)  
            score_size = int(WINDOW_HEIGHT * 0.08)  
            
            title_font = pygame.font.Font(None, title_size)
            score_font = pygame.font.Font(None, score_size)
            
            game_over_text = title_font.render('Game Over!', True, WHITE)
            self.screen.blit(game_over_text, (WINDOW_WIDTH//2 - game_over_text.get_width()//2, WINDOW_HEIGHT//6))
            
            score_text = score_font.render(f'Score: {self.snake.score}', True, WHITE)
            self.screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, WINDOW_HEIGHT//6 + title_size))
            
            high_score_text = score_font.render(f'High Score: {self.high_scores[self.selected_difficulty["name"]]}', True, WHITE)
            self.screen.blit(high_score_text, (WINDOW_WIDTH//2 - high_score_text.get_width()//2, WINDOW_HEIGHT//6 + title_size + score_size))
            
            mouse_pos = pygame.mouse.get_pos()
            
            is_hovered = restart_button.collidepoint(mouse_pos)
            if is_hovered:
                shadow_rect = restart_button.copy()
                shadow_rect.x += 5
                shadow_rect.y += 5
                pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, 2)
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
                pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, 2)
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
                pygame.draw.rect(self.screen, (0, 0, 0), shadow_rect, 2)
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

                if self.red_portal_start and head_pos == (self.red_portal_start.x, self.red_portal_start.y):
                    self.snake.positions[0] = (self.red_portal_end.x, self.red_portal_end.y)

                self.update_power_ups()

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
            
            x_offset = (WINDOW_WIDTH - WINDOW_SIZE) // 2
            y_offset = (WINDOW_HEIGHT - WINDOW_SIZE) // 2
            self.screen.blit(game_surface, (x_offset, y_offset))
            
            score_text = self.font.render(f'Score: {self.snake.score}', True, WHITE)
            self.screen.blit(score_text, (10, 10))

            self.draw_power_up_timers()

            pygame.display.flip()
            self.clock.tick(self.snake.speed)

if __name__ == '__main__':
    game = Game()
    game.run() 
```
### sprites.py
```
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
```
### entities.py
```
import pygame
from enum import Enum
from constants import GRID_SIZE, GRID_COUNT

class PowerUpType(Enum):
    SPEED = 1
    SLOW = 2
    INVINCIBLE = 3

class Food:
    def __init__(self, x, y, type, sprite):
        self.x = x
        self.y = y
        self.type = type
        self.sprite = sprite

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

class PowerUp:
    def __init__(self, x, y, type, sprite):
        self.x = x
        self.y = y
        self.type = type
        self.sprite = sprite
        self.duration = 5000
        self.active = False
        self.start_time = 0
        self.spawn_time = pygame.time.get_ticks()

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

    def get_remaining_time(self):
        if not self.active:
            return 0
        current_time = pygame.time.get_ticks()
        remaining = self.duration - (current_time - self.start_time)
        return max(0, remaining)

    def should_disappear(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.spawn_time >= 5000

class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        self.length = 2
        start_x = 3
        start_y = GRID_COUNT // 2
        self.positions = [(start_x, start_y), (start_x - 1, start_y)]
        self.direction = (1, 0)
        self.score = 0
        self.speed = 10
        self.power_ups = []
        self.invincible = False
        self.is_teleporting = False

    def get_head_position(self):
        return self.positions[0]

    def update(self, portals):
        cur = self.get_head_position()
        x, y = self.direction
        new = ((cur[0] + x) % GRID_COUNT, (cur[1] + y) % GRID_COUNT)

        if new in self.positions[:-1]:
            if not self.invincible:
                return False
        else:
            self.positions.insert(0, new)
            if len(self.positions) > self.length:
                self.positions.pop()
        return True

    def get_body_sprite(self, i, sprites):
        if i == 0:
            if self.direction == (0, -1):
                return sprites['snake_head_up']
            elif self.direction == (0, 1):
                return sprites['snake_head_down']
            elif self.direction == (-1, 0):
                return sprites['snake_head_left']
            else:
                return sprites['snake_head_right']
        else:
            return sprites['snake_body']

    def draw(self, screen, sprites):
        for i, p in enumerate(self.positions):
            sprite = self.get_body_sprite(i, sprites)
            screen.blit(sprite, (p[0] * GRID_SIZE, p[1] * GRID_SIZE))

class Portal:
    def __init__(self, x, y, is_start=True, color='blue'):
        self.x = x
        self.y = y
        self.is_start = is_start
        self.color = color
        if is_start:
            self.sprite = pygame.image.load(f'images/{color}portal_start.png').convert_alpha()
        else:
            self.sprite = pygame.image.load(f'images/{color}portal_end.png').convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (GRID_SIZE, GRID_SIZE))

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE))

class Brick:
    def __init__(self, x, y, sprite):
        self.x = x
        self.y = y
        self.sprite = sprite

    def draw(self, screen):
        screen.blit(self.sprite, (self.x * GRID_SIZE, self.y * GRID_SIZE)) 
```
### constants.py
```
import pygame

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
WINDOW_SIZE = min(WINDOW_WIDTH, WINDOW_HEIGHT)
GRID_SIZE = WINDOW_SIZE // 30
GRID_COUNT = WINDOW_SIZE // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
BACKGROUND_COLOR = (20, 20, 40)
GRID_COLOR = (40, 40, 60)

SPRITE_WIDTH = 32
SPRITE_HEIGHT = 32 
```
## Результаты работы

### Интерфейс
1. Выбор сложности:
![](1.jpg)
2. Дизайн игры:
![](2.jpg)
3. Конец игры:
![](3.jpg)

