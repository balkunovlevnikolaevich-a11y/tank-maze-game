import pygame
import sys
import random


# ==========================================
# МОДУЛЬ 1: НАСТРОЙКИ (CONFIG)
# ==========================================
class Config:
    WIDTH = 800
    HEIGHT = 600
    FPS = 60

    # Состояния игры
    STATE_MENU = 0
    STATE_PLAYING = 1
    STATE_GAME_OVER = 2

    # Физика и управление
    GRAVITY = 0.8
    PLAYER_SPEED = 7
    JUMP_POWER = -16
    FRICTION = 0.8

    # Цвета (RGB)
    SKY_COLOR = (135, 206, 235)
    DIRT_COLOR = (139, 69, 19)
    GRASS_COLOR = (50, 200, 50)
    PLAYER_COLOR = (220, 20, 60)
    LAVA_COLOR = (255, 69, 0)
    COIN_COLOR = (255, 215, 0)
    MOUNTAIN_COLOR = (100, 150, 180)
    CLOUD_COLOR = (255, 255, 255)


# ==========================================
# МОДУЛЬ 2: ИГРОК
# ==========================================
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((30, 40), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.is_dead = False
        self.facing_right = True

        self.draw_character()

    def draw_character(self):
        self.image.fill(pygame.SRCALPHA)
        pygame.draw.rect(self.image, Config.PLAYER_COLOR, (0, 0, 30, 40), border_radius=8)

        eye_color = (255, 255, 255)
        pupil_color = (0, 0, 0)
        if self.facing_right:
            pygame.draw.circle(self.image, eye_color, (20, 12), 4)
            pygame.draw.circle(self.image, pupil_color, (22, 12), 2)
        else:
            pygame.draw.circle(self.image, eye_color, (10, 12), 4)
            pygame.draw.circle(self.image, pupil_color, (8, 12), 2)

    def handle_keys(self):
        if self.is_dead:
            return

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a]:
            self.vel_x = -Config.PLAYER_SPEED
            if self.facing_right:
                self.facing_right = False
                self.draw_character()
        elif keys[pygame.K_d]:
            self.vel_x = Config.PLAYER_SPEED
            if not self.facing_right:
                self.facing_right = True
                self.draw_character()
        else:
            self.vel_x *= Config.FRICTION

        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.on_ground:
            self.vel_y = Config.JUMP_POWER
            self.on_ground = False

    def update(self, platforms, lavas):
        self.handle_keys()
        self.vel_y += Config.GRAVITY

        self.rect.x += self.vel_x
        self.check_collisions(platforms, 'x')

        self.rect.y += self.vel_y
        self.check_collisions(platforms, 'y')

        if self.rect.y > Config.HEIGHT + 200 or pygame.sprite.spritecollideany(self, lavas):
            self.is_dead = True

    def check_collisions(self, platforms, axis):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if axis == 'x':
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:
                        self.rect.left = platform.rect.right
                    self.vel_x = 0
                elif axis == 'y':
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.rect.top = platform.rect.bottom
                    self.vel_y = 0


# ==========================================
# МОДУЛЬ 3: ОБЪЕКТЫ
# ==========================================
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(Config.DIRT_COLOR)
        pygame.draw.rect(self.image, Config.GRASS_COLOR, (0, 0, width, 15))
        pygame.draw.rect(self.image, (30, 150, 30), (0, 15, width, 5))
        self.rect = self.image.get_rect(topleft=(x, y))


class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(Config.LAVA_COLOR)
        for _ in range(width // 20):
            px = random.randint(0, width - 10)
            py = random.randint(5, 15)
            pygame.draw.circle(self.image, (255, 165, 0), (px, py), 4)
        self.rect = self.image.get_rect(topleft=(x, y))


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
        pygame.draw.circle(self.image, Config.COIN_COLOR, (12, 12), 12)
        pygame.draw.circle(self.image, (218, 165, 32), (12, 12), 8, 2)
        self.rect = self.image.get_rect(center=(x, y))


# ==========================================
# МОДУЛЬ 4: ИГРА И UI
# ==========================================
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WIDTH, Config.HEIGHT))
        pygame.display.set_caption("Марио: Бесконечный Забег")
        self.clock = pygame.time.Clock()

        # Шрифты разного размера
        self.font_large = pygame.font.SysFont("impact", 64)
        self.font_medium = pygame.font.SysFont("impact", 36)

        self.state = Config.STATE_MENU
        self.camera_x = 0  # Чтобы фон рисовался в меню

        self.generate_background()

    def generate_background(self):
        self.clouds = [(random.randint(0, Config.WIDTH), random.randint(50, 200), random.randint(40, 80)) for _ in
                       range(8)]
        self.mountains = [(x * 150, Config.HEIGHT - random.randint(150, 350)) for x in range(10)]

    def draw_background(self):
        self.screen.fill(Config.SKY_COLOR)
        for cx, cy, csize in self.clouds:
            real_x = (cx - self.camera_x * 0.1) % (Config.WIDTH + 100) - 100
            pygame.draw.ellipse(self.screen, Config.CLOUD_COLOR, (real_x, cy, csize, csize // 2))
        for mx, my in self.mountains:
            real_x = (mx - self.camera_x * 0.3) % (Config.WIDTH + 300) - 300
            pygame.draw.polygon(self.screen, Config.MOUNTAIN_COLOR, [
                (real_x, Config.HEIGHT), (real_x + 150, my), (real_x + 300, Config.HEIGHT)
            ])

    def draw_text(self, text, font, color, x, y):
        # Функция для удобной отрисовки красивого текста с черной тенью
        shadow = font.render(text, True, (0, 0, 0))
        main_text = font.render(text, True, color)
        self.screen.blit(shadow, (x + 3, y + 3))
        self.screen.blit(main_text, (x, y))

    def reset_game(self):
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.lavas = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()

        self.player = Player(100, 300)
        self.all_sprites.add(self.player)

        self.score = 0
        self.camera_x = 0
        self.max_gen_x = 0

        self.generate_platform(0, Config.HEIGHT - 40, 800)

    def generate_platform(self, x, y, width):
        plat = Platform(x, y, width, 200)
        self.platforms.add(plat)
        self.all_sprites.add(plat)
        self.max_gen_x = x + width

    def generate_level_chunk(self):
        while self.max_gen_x < self.camera_x + Config.WIDTH * 2:
            gap = random.randint(80, 220)
            plat_width = random.randint(200, 500)
            plat_y = random.randint(Config.HEIGHT - 180, Config.HEIGHT - 40)

            if random.random() > 0.4:
                lava = Lava(self.max_gen_x, Config.HEIGHT - 30, gap, 200)
                self.lavas.add(lava)
                self.all_sprites.add(lava)

            self.generate_platform(self.max_gen_x + gap, plat_y, plat_width)

            if random.random() > 0.3:
                coin_x = self.max_gen_x - plat_width // 2
                coin_y = plat_y - random.randint(60, 120)
                coin = Coin(coin_x, coin_y)
                self.coins.add(coin)
                self.all_sprites.add(coin)

    def clean_up_offscreen(self):
        for sprite in self.all_sprites:
            if sprite != self.player and sprite.rect.right < self.camera_x - 200:
                sprite.kill()

    def run(self):
        running = True
        while running:
            # 1. СОБЫТИЯ И УПРАВЛЕНИЕ СОСТОЯНИЯМИ
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if self.state == Config.STATE_MENU:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.state = Config.STATE_PLAYING
                    elif self.state == Config.STATE_GAME_OVER:
                        if event.key == pygame.K_SPACE:
                            self.reset_game()
                            self.state = Config.STATE_PLAYING

            # 2. ИГРОВАЯ ЛОГИКА
            if self.state == Config.STATE_PLAYING:
                self.player.update(self.platforms, self.lavas)

                if self.player.is_dead:
                    self.state = Config.STATE_GAME_OVER

                coins_hit = pygame.sprite.spritecollide(self.player, self.coins, True)
                self.score += len(coins_hit)

                target_camera_x = self.player.rect.x - Config.WIDTH // 3
                if target_camera_x > self.camera_x:
                    self.camera_x = target_camera_x

                self.generate_level_chunk()
                self.clean_up_offscreen()

            # 3. ОТРИСОВКА
            self.draw_background()

            if self.state == Config.STATE_MENU:
                self.draw_text("ПИКСЕЛЬНЫЙ БЕГУН", self.font_large, Config.COIN_COLOR, 130, 150)
                self.draw_text("Нажмите ПРОБЕЛ для старта", self.font_medium, (255, 255, 255), 200, 300)
                self.draw_text("Управление: WASD", self.font_medium, (200, 200, 200), 260, 400)

            elif self.state == Config.STATE_PLAYING or self.state == Config.STATE_GAME_OVER:
                for sprite in self.all_sprites:
                    self.screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))

                self.draw_text(f"МОНЕТЫ: {self.score}", self.font_medium, (255, 255, 255), 20, 20)

                if self.state == Config.STATE_GAME_OVER:
                    # Затемняем экран полупрозрачной пленкой
                    death_bg = pygame.Surface((Config.WIDTH, Config.HEIGHT), pygame.SRCALPHA)
                    death_bg.fill((0, 0, 0, 180))
                    self.screen.blit(death_bg, (0, 0))

                    self.draw_text("ИГРА ОКОНЧЕНА", self.font_large, (255, 50, 50), 200, 150)
                    self.draw_text(f"Итоговый счет: {self.score}", self.font_large, Config.COIN_COLOR, 200, 250)
                    self.draw_text("Нажмите ПРОБЕЛ для рестарта", self.font_medium, (255, 255, 255), 180, 400)

            pygame.display.flip()
            self.clock.tick(Config.FPS)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
