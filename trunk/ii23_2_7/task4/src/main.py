import pygame
import random
import math
from enum import Enum


class Weather(Enum):
    SUNNY = 1
    RAIN = 2
    SNOW = 3
    WINDY = 4


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill((0, 128, 255))  # Синий цвет игрока
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        self.jumping = False
        self.achievements = set()
        self.hidden_bonuses = 0
        self.score = 0

    def update(self, platforms, weather):
        # Гравитация
        self.velocity_y += 0.5

        # Влияние ветра
        if weather == Weather.WINDY:
            self.velocity_x += random.uniform(-0.3, 0.3)

        # Ограничение скорости
        if self.velocity_x > 5:
            self.velocity_x = 5
        elif self.velocity_x < -5:
            self.velocity_x = -5

        # Движение по X
        self.rect.x += self.velocity_x

        # Проверка коллизий по X
        platform_hit = pygame.sprite.spritecollide(self, platforms, False)
        if platform_hit:
            if self.velocity_x > 0:
                self.rect.right = platform_hit[0].rect.left
            elif self.velocity_x < 0:
                self.rect.left = platform_hit[0].rect.right
            self.velocity_x = 0

        # Движение по Y
        self.rect.y += self.velocity_y

        # Проверка коллизий по Y
        platform_hit = pygame.sprite.spritecollide(self, platforms, False)
        if platform_hit:
            if self.velocity_y > 0:
                self.rect.bottom = platform_hit[0].rect.top
                self.jumping = False
            elif self.velocity_y < 0:
                self.rect.top = platform_hit[0].rect.bottom
            self.velocity_y = 0


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, is_moving=False):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))  # Зеленые платформы
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.is_moving = is_moving
        self.move_direction = 1
        self.move_speed = random.randint(1, 3)
        self.original_x = x

    def update(self, weather):
        if self.is_moving:
            # Движение платформы
            if abs(self.rect.x - self.original_x) > 100:
                self.move_direction *= -1
            self.rect.x += self.move_speed * self.move_direction

            # Влияние погоды на скорость
            if weather == Weather.WINDY:
                self.move_speed = random.randint(2, 5)
            else:
                self.move_speed = random.randint(1, 3)


class Bonus(pygame.sprite.Sprite):
    def __init__(self, x, y, bonus_type):
        super().__init__()
        self.bonus_type = bonus_type
        if bonus_type == "coin":
            self.image = pygame.Surface((15, 15))
            self.image.fill((255, 215, 0))  # Золотой цвет
        elif bonus_type == "secret":
            self.image = pygame.Surface((10, 10))
            self.image.fill((255, 0, 255))  # Пурпурный цвет
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Динамический платформер")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)

        # Группы спрайтов
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.bonuses = pygame.sprite.Group()

        # Создание игрока
        self.player = Player()
        self.all_sprites.add(self.player)

        # Создание платформ
        self.create_level()

        # Погода
        self.weather = Weather.SUNNY
        self.weather_change_timer = 0
        self.weather_duration = random.randint(600, 1200)  # 10-20 секунд

        # Дождь/снег
        self.rain_drops = []
        self.snow_flakes = []

    def create_level(self):
        # Основные платформы
        ground = Platform(0, 550, 800, 50)
        self.all_sprites.add(ground)
        self.platforms.add(ground)

        # Добавляем случайные платформы
        for i in range(10):
            self.add_platform_with_bonus()

    def add_platform_with_bonus(self):
        width = random.randint(50, 150)
        x = random.randint(0, 800 - width)
        y = random.randint(100, 500)
        is_moving = random.choice([True, False, False])

        platform = Platform(x, y, width, 20, is_moving)
        self.all_sprites.add(platform)
        self.platforms.add(platform)

        # 50% chance to have a bonus on platform
        if random.random() < 0.5:
            self.add_bonus(platform)

    def add_bonus(self, platform):
        bonus_type = "coin" if random.random() < 0.8 else "secret"
        bonus = Bonus(platform.rect.x + platform.rect.width // 2,
                      platform.rect.y - 20,
                      bonus_type)
        self.all_sprites.add(bonus)
        self.bonuses.add(bonus)

    def add_random_bonuses(self, count=3):
        # Выбираем случайные платформы для новых бонусов
        available_platforms = [p for p in self.platforms
                               if p.rect.y < 500 and  # Не нижняя платформа
                               not any(b.rect.collidepoint(p.rect.x + p.rect.width // 2, p.rect.y - 20)
                                       for b in self.bonuses)]

        for _ in range(min(count, len(available_platforms))):
            platform = random.choice(available_platforms)
            self.add_bonus(platform)
            available_platforms.remove(platform)  # Чтобы не добавлять два бонуса на одну платформу

    def update_weather(self):
        self.weather_change_timer += 1

        if self.weather_change_timer > self.weather_duration:
            previous_weather = self.weather
            self.weather = random.choice(list(Weather))

            # Гарантируем, что новая погода будет отличаться от предыдущей
            while self.weather == previous_weather and len(Weather) > 1:
                self.weather = random.choice(list(Weather))

            self.weather_duration = random.randint(600, 1200)  # 10-20 секунд
            self.weather_change_timer = 0

            # Добавляем новые бонусы при смене погоды
            self.add_random_bonuses(random.randint(1, 3))

            # Особые эффекты для новой погоды
            if self.weather == Weather.RAIN:
                self.rain_drops = [[random.randint(0, 800), random.randint(-50, 0)] for _ in range(100)]
            elif self.weather == Weather.SNOW:
                self.snow_flakes = [[random.randint(0, 800), random.randint(-50, 0)] for _ in range(50)]
            elif self.weather == Weather.WINDY:
                # Усиливаем движение платформ при ветре
                for platform in self.platforms:
                    if platform.is_moving:
                        platform.move_speed = random.randint(2, 5)

    def create_level(self):
        # Основные платформы
        ground = Platform(0, 550, 800, 50)
        self.all_sprites.add(ground)
        self.platforms.add(ground)

        # Добавляем случайные платформы
        for i in range(10):
            width = random.randint(50, 150)
            x = random.randint(0, 800 - width)
            y = random.randint(100, 500)
            is_moving = random.choice([True, False, False])  # 33% chance to move

            platform = Platform(x, y, width, 20, is_moving)
            self.all_sprites.add(platform)
            self.platforms.add(platform)

            # 50% chance to have a bonus on platform
            if random.random() < 0.5:
                bonus_type = "coin" if random.random() < 0.8 else "secret"
                bonus = Bonus(x + width // 2, y - 20, bonus_type)
                self.all_sprites.add(bonus)
                self.bonuses.add(bonus)

    def update_weather(self):
        self.weather_change_timer += 1

        # Смена погоды каждые 10-20 секунд (60 FPS)
        if self.weather_change_timer > self.weather_duration:
            self.weather = random.choice(list(Weather))
            self.weather_duration = random.randint(600, 1200)  # 10-20 секунд
            self.weather_change_timer = 0

            # Особый эффект при смене погоды
            if self.weather == Weather.RAIN:
                self.rain_drops = [[random.randint(0, 800), random.randint(-50, 0)] for _ in range(100)]
            elif self.weather == Weather.SNOW:
                self.snow_flakes = [[random.randint(0, 800), random.randint(-50, 0)] for _ in range(50)]


    def draw_weather_effects(self):
        if self.weather == Weather.RAIN:
            for drop in self.rain_drops:
                pygame.draw.line(self.screen, (100, 100, 255),
                                 (drop[0], drop[1]),
                                 (drop[0], drop[1] + 10), 2)
                drop[1] += 10
                drop[0] += 1  # Наклон дождя
                if drop[1] > 600:
                    drop[1] = random.randint(-50, 0)
                    drop[0] = random.randint(0, 800)

        elif self.weather == Weather.SNOW:
            for flake in self.snow_flakes:
                pygame.draw.circle(self.screen, (255, 255, 255),
                                   (flake[0], flake[1]), 2)
                flake[1] += 3
                flake[0] += random.uniform(-0.5, 0.5)
                if flake[1] > 600:
                    flake[1] = random.randint(-50, 0)
                    flake[0] = random.randint(0, 800)

    def check_achievements(self):
        # Проверка достижений
        if self.player.hidden_bonuses >= 3 and "collector" not in self.player.achievements:
            self.player.achievements.add("collector")
            print("Достижение получено: Коллекционер!")

        if self.player.score >= 1000 and "rich" not in self.player.achievements:
            self.player.achievements.add("rich")
            print("Достижение получено: Богач!")

        # Пасхалка: прыгнуть 10 раз за 5 секунд
        # (это нужно реализовать через подсчет прыжков и таймер)

    def run(self):
        running = True
        while running:
            # Обработка событий
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not self.player.jumping:
                        self.player.velocity_y = -12
                        self.player.jumping = True

            # Управление
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.velocity_x = -5
            elif keys[pygame.K_RIGHT]:
                self.player.velocity_x = 5
            else:
                self.player.velocity_x = 0

            # Обновление
            self.update_weather()
            self.platforms.update(self.weather)
            self.player.update(self.platforms, self.weather)

            # Проверка бонусов
            bonuses_hit = pygame.sprite.spritecollide(self.player, self.bonuses, True)
            for bonus in bonuses_hit:
                if bonus.bonus_type == "coin":
                    self.player.score += 100
                elif bonus.bonus_type == "secret":
                    self.player.score += 500
                    self.player.hidden_bonuses += 1

            self.check_achievements()

            # Отрисовка
            self.screen.fill((135, 206, 235))  # Небо

            # Рисуем эффекты погоды
            self.draw_weather_effects()

            # Рисуем все спрайты
            self.all_sprites.draw(self.screen)

            # UI
            score_text = self.font.render(f"Очки: {self.player.score}", True, (0, 0, 0))
            weather_text = self.font.render(f"Погода: {self.weather.name}", True, (0, 0, 0))
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(weather_text, (10, 50))

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()