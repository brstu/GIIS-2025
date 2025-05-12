import pygame
import sys
import random
import math


pygame.init()


WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")


BLACK = (0, 0, 0)


player_img = pygame.image.load("graphics/spaceship.png")
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 10
player_speed = 3  # уменьшил скорость для плавности


pygame.mixer.music.load("sounds/music.ogg")
pygame.mixer.music.play(-1)


lives = 3
life_img = pygame.transform.scale(player_img, (32, 24))

bullet_img = pygame.Surface((4, 16))
bullet_img.fill((255, 255, 0))
bullet_speed = -7
bullets = []


shoot_sound = pygame.mixer.Sound("sounds/laser.ogg")
explosion_sound = pygame.mixer.Sound("sounds/explosion.ogg")


enemy_bullet_img = pygame.Surface((4, 16))
enemy_bullet_img.fill((255, 0, 0))
enemy_bullets = []
enemy_bullet_speed = 5
ENEMY_SHOOT_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SHOOT_EVENT, 700)


EXPLOSION_TIME = 10  # кадров
explosions = []  # [{'rect': ..., 'timer': ...}]

# Враги
enemy_imgs = [pygame.image.load(f"graphics/alien_{i}.png") for i in range(1, 4)]
enemies = []
ENEMY_ROWS = 3
ENEMY_COLS = 7
for row in range(ENEMY_ROWS):
    for col in range(ENEMY_COLS):
        img = enemy_imgs[row % len(enemy_imgs)]
        rect = img.get_rect()
        rect.x = 80 + col * 80
        rect.y = 60 + row * 60
        enemies.append({'img': img, 'rect': rect, 'alive': True})

enemy_direction = 1
enemy_speed = 1


score = 0
font = pygame.font.Font("font/monogram.ttf", 32)

clock = pygame.time.Clock()

level = 1

paused = False

game_over = False


BONUS_TYPES = ["double_shot", "shield"]
BONUS_COLORS = {"double_shot": (0, 255, 255), "shield": (255, 0, 255)}
bonuses = []  # [{'rect': ..., 'type': ..., 'timer': ...}]
BONUS_TIME = 600  # 10 секунд (60 FPS)
active_bonuses = {"double_shot": 0, "shield": 0}

win = False


boss_img = pygame.image.load("graphics/mystery.png")
boss_rect = boss_img.get_rect()
boss_alive = False
boss_hp = 20
boss_direction = 1
boss_speed = 3
boss_bullets = []
boss_bullet_img = pygame.Surface((8, 24))
boss_bullet_img.fill((255, 128, 0))
BOSS_SHOOT_EVENT = pygame.USEREVENT + 2
pygame.time.set_timer(BOSS_SHOOT_EVENT, 500)

boss_invulnerable = False
boss_invuln_timer = 0
boss_shoot_timer = 0
boss_bonus_timer = 0


special_wave = False
special_enemies = []


difficulty = None
DIFFICULTY_SETTINGS = {
    1: {  
        'enemy_speed': 1,
        'enemy_shoot_interval': 900,
        'lives': 5,
        'boss_speed': 2
    },
    2: {  
        'enemy_speed': 1.5,
        'enemy_shoot_interval': 700,
        'lives': 3,
        'boss_speed': 3
    },
    3: {  
        'enemy_speed': 2.2,
        'enemy_shoot_interval': 400,
        'lives': 2,
        'boss_speed': 4
    }
}


miniboss_img = pygame.transform.scale(boss_img, (80, 48))
minibosses = []  # [{'rect': ..., 'hp': ...}]
MINIBOSS_HP = 10
miniboss_wave = False

def spawn_boss():
    global boss_alive, boss_hp, boss_rect
    boss_alive = True
    boss_hp = 20 + 5 * (level - 1)
    boss_rect.x = WIDTH // 2 - boss_rect.width // 2
    boss_rect.y = 30

def spawn_special_wave():
    global special_wave, special_enemies
    special_wave = True
    special_enemies.clear()
    for i in range(5):
        img = enemy_imgs[i % len(enemy_imgs)]
        rect = img.get_rect()
        rect.x = 100 + i * 120
        rect.y = 100
        special_enemies.append({'img': img, 'rect': rect, 'alive': True, 'speed': 6})

def spawn_minibosses():
    global minibosses, miniboss_wave
    minibosses = []
    miniboss_wave = True
    for i in range(3):
        rect = miniboss_img.get_rect()
        rect.x = 200 + i * 150
        rect.y = 80
        minibosses.append({'rect': rect, 'hp': MINIBOSS_HP})

def reset_game(next_level=False):
    global enemies, bullets, player_rect, lives, score, enemy_direction, enemy_speed, enemy_bullets, explosions, level, boss_alive, boss_bullets, bonuses, active_bonuses, special_wave, special_enemies, win
    player_rect.centerx = WIDTH // 2
    player_rect.bottom = HEIGHT - 10
    bullets.clear()
    enemy_bullets.clear()
    boss_bullets.clear()
    explosions.clear()
    bonuses.clear()
    active_bonuses = {"double_shot": 0, "shield": 0}
    enemies.clear()
    special_enemies.clear()
    special_wave = False
    for row in range(ENEMY_ROWS):
        for col in range(ENEMY_COLS):
            img = enemy_imgs[row % len(enemy_imgs)]
            rect = img.get_rect()
            rect.x = 80 + col * 80
            rect.y = 60 + row * 60
            enemies.append({'img': img, 'rect': rect, 'alive': True})
    enemy_direction = 1
    if next_level:
        enemy_speed += 0.5
        level += 1
    else:
        enemy_speed = 1
        level = 1
    if not next_level:
        score = 0
        lives = 3
    boss_alive = False
    win = False

def show_difficulty_menu():
    menu = True
    while menu:
        screen.fill((10, 10, 30))
        title = font.render("SPACE INVADERS", True, (0, 255, 0))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 120))
        prompt = font.render("Choose difficulty:", True, (255, 255, 255))
        screen.blit(prompt, (WIDTH//2 - prompt.get_width()//2, 220))
        easy = font.render("1 - Easy", True, (0, 200, 255))
        medium = font.render("2 - Medium", True, (255, 255, 0))
        hard = font.render("3 - Hard", True, (255, 80, 80))
        screen.blit(easy, (WIDTH//2 - easy.get_width()//2, 300))
        screen.blit(medium, (WIDTH//2 - medium.get_width()//2, 350))
        screen.blit(hard, (WIDTH//2 - hard.get_width()//2, 400))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                if event.key == pygame.K_2:
                    return 2
                if event.key == pygame.K_3:
                    return 3


if __name__ == "__main__":
    difficulty = show_difficulty_menu()
    settings = DIFFICULTY_SETTINGS[difficulty]
    enemy_speed = settings['enemy_speed']
    lives = settings['lives']
    boss_speed = settings['boss_speed']
    pygame.time.set_timer(ENEMY_SHOOT_EVENT, settings['enemy_shoot_interval'])

    running = True
    while running:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if not game_over and not win and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if event.key == pygame.K_F4:
                    level = 4
                    enemies.clear()
                    minibosses.clear()
                    miniboss_wave = False
                    boss_alive = True
                    boss_hp = 20
                    boss_rect.x = WIDTH // 2 - boss_rect.width // 2
                    boss_rect.y = 30
                    win = False
            if not game_over and not paused and not win and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if active_bonuses["double_shot"] > 0:
                        if len(bullets) < 6:
                            for dx in [-12, 12]:
                                bullet_rect = bullet_img.get_rect()
                                bullet_rect.centerx = player_rect.centerx + dx
                                bullet_rect.bottom = player_rect.top
                                bullets.append(bullet_rect)
                            shoot_sound.play()
                    else:
                        if len(bullets) < 3:
                            bullet_rect = bullet_img.get_rect()
                            bullet_rect.centerx = player_rect.centerx
                            bullet_rect.bottom = player_rect.top
                            bullets.append(bullet_rect)
                            shoot_sound.play()
            if (game_over or win) and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game()
                    game_over = False
                    win = False
            if not game_over and not paused and not win and event.type == ENEMY_SHOOT_EVENT:
                shooters = [e for e in enemies if e['alive']]
                if shooters:
                    shooter = random.choice(shooters)
                    bullet = enemy_bullet_img.get_rect()
                    bullet.centerx = shooter['rect'].centerx
                    bullet.top = shooter['rect'].bottom
                    enemy_bullets.append(bullet)
            if not game_over and not paused and boss_alive and event.type == BOSS_SHOOT_EVENT:
                bullet = boss_bullet_img.get_rect()
                bullet.centerx = boss_rect.centerx
                bullet.top = boss_rect.bottom
                boss_bullets.append(bullet)

        if not game_over and not paused and not win:
            
            for bonus in bonuses[:]:
                bonus['rect'].y += 3
                if bonus['rect'].top > HEIGHT:
                    bonuses.remove(bonus)
                elif bonus['rect'].colliderect(player_rect):
                    active_bonuses[bonus['type']] = BONUS_TIME
                    bonuses.remove(bonus)
            for btype in active_bonuses:
                if active_bonuses[btype] > 0:
                    active_bonuses[btype] -= 1

            
            if boss_alive:
               
                boss_rect.x = int(WIDTH // 2 + 200 * math.sin(pygame.time.get_ticks() / 900))
               
                boss_shoot_timer += 1
                if boss_shoot_timer > 120:
                    for dx in [-40, 0, 40]:
                        bullet = boss_bullet_img.get_rect()
                        bullet.centerx = boss_rect.centerx + dx
                        bullet.top = boss_rect.bottom
                        boss_bullets.append(bullet)
                    boss_shoot_timer = 0
                
                boss_invuln_timer += 1
                if boss_invuln_timer > 240:
                    boss_invulnerable = True
                if boss_invuln_timer > 300:
                    boss_invulnerable = False
                    boss_invuln_timer = 0
               
                boss_bonus_timer += 1
                if boss_bonus_timer > 180:
                    if random.random() < 0.2:
                        btype = random.choice(BONUS_TYPES)
                        brect = pygame.Rect(boss_rect.centerx-12, boss_rect.bottom, 24, 24)
                        bonuses.append({'rect': brect, 'type': btype, 'timer': BONUS_TIME})
                    boss_bonus_timer = 0
               
                for bullet in bullets[:]:
                    if bullet.colliderect(boss_rect) and not boss_invulnerable:
                        boss_hp -= 1
                        bullets.remove(bullet)
                        if boss_hp <= 0:
                            boss_alive = False
                            score += 200
                            explosions.append({'rect': boss_rect.copy(), 'timer': EXPLOSION_TIME * 2})
                            if level == 4:
                                win = True
           
            if special_wave:
                for enemy in special_enemies:
                    if enemy['alive']:
                        enemy['rect'].x += enemy['speed']
                        if enemy['rect'].left < 0 or enemy['rect'].right > WIDTH:
                            enemy['speed'] *= -1
                for bullet in bullets[:]:
                    for enemy in special_enemies:
                        if enemy['alive'] and bullet.colliderect(enemy['rect']):
                            enemy['alive'] = False
                            bullets.remove(bullet)
                            score += 50
                            explosions.append({'rect': enemy['rect'].copy(), 'timer': EXPLOSION_TIME})
                            
                            if random.random() < 0.5:
                                btype = random.choice(BONUS_TYPES)
                                brect = pygame.Rect(enemy['rect'].centerx-12, enemy['rect'].centery-12, 24, 24)
                                bonuses.append({'rect': brect, 'type': btype, 'timer': BONUS_TIME})
                            break
                if all(not e['alive'] for e in special_enemies):
                    special_wave = False
                    reset_game(next_level=True)
            
            if level == 4:
                fixed_speed = 1.5
                move_down = False
                for enemy in enemies:
                    if not enemy['alive']:
                        continue
                    enemy['rect'].x += enemy_direction * fixed_speed
                    if enemy['rect'].right >= WIDTH - 10 or enemy['rect'].left <= 10:
                        move_down = True
                if move_down:
                    enemy_direction *= -1
                    for enemy in enemies:
                        enemy['rect'].y += 20
                
                if all(not enemy['alive'] for enemy in enemies) and not boss_alive:
                    spawn_boss()
                
                if not boss_alive and all(not enemy['alive'] for enemy in enemies):
                    win = True
            else:
                
                move_down = False
                for enemy in enemies:
                    if not enemy['alive']:
                        continue
                    enemy['rect'].x += enemy_direction * enemy_speed
                    if enemy['rect'].right >= WIDTH - 10 or enemy['rect'].left <= 10:
                        move_down = True
                if move_down:
                    enemy_direction *= -1
                    for enemy in enemies:
                        enemy['rect'].y += 20
                if level < 4 and all(not enemy['alive'] for enemy in enemies) and not boss_alive and not special_wave:
                    reset_game(next_level=True)

            for bullet in bullets[:]:
                for enemy in enemies:
                    if enemy['alive'] and bullet.colliderect(enemy['rect']):
                        enemy['alive'] = False
                        bullets.remove(bullet)
                        explosion_sound.play()
                        score += 10
                        explosions.append({'rect': enemy['rect'].copy(), 'timer': EXPLOSION_TIME})
                        # шанс бонуса
                        if random.random() < 0.2:
                            btype = random.choice(BONUS_TYPES)
                            brect = pygame.Rect(enemy['rect'].centerx-12, enemy['rect'].centery-12, 24, 24)
                            bonuses.append({'rect': brect, 'type': btype, 'timer': BONUS_TIME})
                        break

            for enemy in enemies:
                if enemy['alive'] and enemy['rect'].bottom >= HEIGHT - 50:
                    lives -= 1
                    if lives > 0:
                        player_rect.centerx = WIDTH // 2
                        player_rect.bottom = HEIGHT - 10
                        bullets.clear()
                        enemy_bullets.clear()
                        for e in enemies:
                            e['rect'].y = 60 + (e['rect'].y - 60) // 60 * 60
                    else:
                        game_over = True
                    break

            for exp in explosions[:]:
                exp['timer'] -= 1
                if exp['timer'] <= 0:
                    explosions.remove(exp)

        if not game_over and not paused and not win:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_rect.x -= player_speed
            if keys[pygame.K_RIGHT]:
                player_rect.x += player_speed
            if player_rect.left < 0:
                player_rect.left = 0
            if player_rect.right > WIDTH:
                player_rect.right = WIDTH

    
        for bullet in bullets[:]:
            bullet.y += bullet_speed
            if bullet.bottom < 0 or bullet.top > HEIGHT:
                bullets.remove(bullet)

   
        for bullet in enemy_bullets[:]:
            bullet.y += enemy_bullet_speed
            if bullet.top > HEIGHT:
                enemy_bullets.remove(bullet)
            elif bullet.colliderect(player_rect):
                enemy_bullets.remove(bullet)
                if active_bonuses["shield"] == 0:
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        
        for bullet in boss_bullets[:]:
            bullet.y += 7
            if bullet.top > HEIGHT:
                boss_bullets.remove(bullet)
            elif bullet.colliderect(player_rect):
                boss_bullets.remove(bullet)
                if active_bonuses["shield"] == 0:
                    lives -= 1
                    if lives <= 0:
                        game_over = True

        # Рендер
        screen.fill(BLACK)
        for enemy in enemies:
            if enemy['alive']:
                screen.blit(enemy['img'], enemy['rect'])
        for enemy in special_enemies:
            if enemy['alive']:
                screen.blit(enemy['img'], enemy['rect'])
        for bullet in bullets:
            screen.blit(bullet_img, bullet)
        for bullet in enemy_bullets:
            screen.blit(enemy_bullet_img, bullet)
        for bullet in boss_bullets:
            screen.blit(boss_bullet_img, bullet)
        if boss_alive:
            
            if boss_invulnerable and (pygame.time.get_ticks() // 100) % 2 == 0:
                pass  
            else:
                screen.blit(boss_img, boss_rect)
            bar_w = boss_rect.width
            bar_h = 12
            hp_ratio = boss_hp / (20 + 5 * (level - 1))
            pygame.draw.rect(screen, (255,0,0), (boss_rect.x, boss_rect.y-18, bar_w, bar_h))
            pygame.draw.rect(screen, (0,255,0), (boss_rect.x, boss_rect.y-18, int(bar_w*hp_ratio), bar_h))
        if not game_over and not win or lives > 0:
            screen.blit(player_img, player_rect)
        
        for exp in explosions:
            pygame.draw.ellipse(screen, (255, 255, 0), exp['rect'], 0)
        
        for bonus in bonuses:
            pygame.draw.rect(screen, BONUS_COLORS[bonus['type']], bonus['rect'])
        
        bx = 10
        for btype in active_bonuses:
            if active_bonuses[btype] > 0:
                btxt = font.render(btype.upper(), True, BONUS_COLORS[btype])
                screen.blit(btxt, (bx, HEIGHT-40))
                bx += btxt.get_width() + 10
        score_text = font.render(f"SCORE: {score}", True, (0, 255, 0))
        screen.blit(score_text, (10, 10))
        for i in range(lives):
            screen.blit(life_img, (WIDTH - 40 - i * 40, 10))
        level_text = font.render(f"LEVEL: {level}", True, (0, 200, 255))
        screen.blit(level_text, (10, 50))
        if paused:
            pause_text = font.render("PAUSED", True, (255, 255, 0))
            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
        if win:
            win_text = font.render("YOU WIN!", True, (0, 255, 0))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
        if game_over:
            over_text = font.render("GAME OVER", True, (255, 0, 0))
            restart_text = font.render("Press R to Restart", True, (255, 255, 255))
            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))
        pygame.display.flip()

pygame.quit()
sys.exit() 