import pygame
import random
import sys
from pygame.locals import *

# Инициализация pygame
pygame.init()
pygame.mixer.init()

# Настройки окна
WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Космический шутер")

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Загрузка ресурсов с обработкой ошибок
try:
    background = pygame.transform.scale(pygame.image.load('galaxy.jpg'), (WIDTH, HEIGHT))
except:
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill(BLACK)
    print("Фон galaxy.jpg не найден, используется черный фон")

try:
    spaceship_img = pygame.transform.scale(pygame.image.load('rocket.png'), (50, 50))
except:
    spaceship_img = pygame.Surface((50, 50))
    spaceship_img.fill(GREEN)
    print("Изображение корабля rocket.png не найдено")

try:
    enemy_img = pygame.transform.scale(pygame.image.load('ufo.png'), (50, 50))
except:
    enemy_img = pygame.Surface((50, 50))
    enemy_img.fill(RED)
    print("Изображение врага ufo.png не найдено")

try:
    bullet_img = pygame.transform.scale(pygame.image.load('bullet.png'), (10, 20))
except:
    bullet_img = pygame.Surface((10, 20))
    bullet_img.fill(WHITE)
    print("Изображение пули bullet.png не найдено")

# Звуки
try:
    pygame.mixer.music.load('space.ogg')
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except:
    print("Фоновая музыка space.ogg не найдена")

try:
    fire_sound = pygame.mixer.Sound('fire.ogg')
except:
    fire_sound = None
    print("Звук выстрела fire.ogg не найден")

# Шрифты
try:
    stats_font = pygame.font.Font(None, 36)
except:
    stats_font = pygame.font.SysFont('arial', 36)
    print("Не удалось загрузить шрифт, используется системный Arial")

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed = speed
    
    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Bullet(GameSprite):
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()

class Player(GameSprite):
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < WIDTH - self.rect.width:
            self.rect.x += self.speed
    
    def fire(self):
        bullet = Bullet(bullet_img, self.rect.centerx - 5, self.rect.top, 15)
        bullets.add(bullet)
        if fire_sound:
            fire_sound.play()

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > HEIGHT:
            self.respawn()
            global missed
            missed += 1
    
    def respawn(self):
        self.rect.y = random.randint(-100, -40)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.speed = random.randint(1, 4)

def show_game_over():
    window.fill(BLACK)
    game_over_text = stats_font.render("ИГРА ОКОНЧЕНА", True, RED)
    score_text = stats_font.render(f"Уничтожено врагов: {destroyed}", True, WHITE)
    restart_text = stats_font.render("Нажмите R для перезапуска", True, WHITE)
    
    window.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 50))
    window.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    window.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
    pygame.display.update()

def reset_game():
    global player, enemies, bullets, missed, destroyed, game_over
    
    player = Player(spaceship_img, WIDTH//2, HEIGHT-100, 5)
    enemies = pygame.sprite.Group()
    for _ in range(5):
        enemy = Enemy(enemy_img, random.randint(0, WIDTH-50), 
                      random.randint(-100, 0), random.randint(1, 3))
        enemies.add(enemy)
    
    bullets = pygame.sprite.Group()
    missed = 0
    destroyed = 0
    game_over = False

# Инициализация игры
reset_game()

# Игровой цикл
clock = pygame.time.Clock()
FPS = 60
running = True

while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_SPACE and not game_over:
                player.fire()
            if event.key == K_r and game_over:
                reset_game()
    
    if not game_over:
        # Обновление объектов
        player.update()
        enemies.update()
        bullets.update()

        # Проверка столкновений
        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for _ in hits:
            destroyed += 1
            enemy = Enemy(enemy_img, random.randint(0, WIDTH-50), 
                          random.randint(-100, 0), random.randint(1, 3))
            enemies.add(enemy)
        
        # Проверка столкновения игрока с врагами
        if pygame.sprite.spritecollide(player, enemies, False):
            game_over = True

        # Отрисовка
        window.blit(background, (0, 0))
        
        # Статистика
        missed_text = stats_font.render(f"Пропущено: {missed}", True, WHITE)
        destroyed_text = stats_font.render(f"Уничтожено: {destroyed}", True, WHITE)
        window.blit(missed_text, (10, 10))
        window.blit(destroyed_text, (10, 50))

        # Отрисовка спрайтов
        player.reset()
        enemies.draw(window)
        bullets.draw(window)
    else:
        show_game_over()
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()
sys.exit()