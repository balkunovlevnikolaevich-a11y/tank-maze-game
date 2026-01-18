"""
TANK MAZE PHYSICS - Простая игра танки в лабиринте
Минимальный, но рабочий код
"""

import arcade
import math
import random

# Настройки экрана
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Tank Maze Physics"

class Tank:
    """Класс танка"""
    def __init__(self, x, y, is_player=True):
        self.center_x = x
        self.center_y = y
        self.width = 30
        self.height = 30
        self.angle = 0

        # Цвета
        if is_player:
            self.color = arcade.color.GREEN
        else:
            self.color = arcade.color.RED

        # Физика
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration = 500
        self.friction = 0.9
        self.max_speed = 200

        # Управление
        self.move_forward = False
        self.move_backward = False
        self.rotate_left = False
        self.rotate_right = False

        # Стрельба
        self.is_player = is_player
        self.is_alive = True
        self.health = 100
        self.last_shot = 0
        self.shoot_cooldown = 0.5 if is_player else 1.5
        self.shoot_range = 300

    def draw(self):
        """Отрисовка танка"""
        if not self.is_alive:
            return

        # Создаем точки для корпуса танка
        half_width = self.width / 2
        half_height = self.height / 2

        # Углы прямоугольника
        corners = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]

        # Применяем поворот
        angle_rad = math.radians(self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        rotated_corners = []
        for x, y in corners:
            # Поворот
            x_rot = x * cos_a - y * sin_a
            y_rot = x * sin_a + y * cos_a
            # Сдвиг
            rotated_corners.append((
                self.center_x + x_rot,
                self.center_y + y_rot
            ))

        # Рисуем корпус
        arcade.draw_polygon_filled(rotated_corners, self.color)

        # Рисуем контур
        outline_points = rotated_corners + [rotated_corners[0]]
        arcade.draw_line_strip(outline_points, arcade.color.BLACK, 2)

        # Дуло
        barrel_length = self.width * 0.8
        barrel_end_x = self.center_x + math.cos(math.radians(self.angle)) * barrel_length
        barrel_end_y = self.center_y + math.sin(math.radians(self.angle)) * barrel_length

        arcade.draw_line(
            self.center_x, self.center_y,
            barrel_end_x, barrel_end_y,
            arcade.color.BLACK, 3
        )

        # Полоска здоровья для врагов
        if not self.is_player and self.is_alive:
            health_width = 30
            health_height = 5
            health_x = self.center_x
            health_y = self.center_y + 25

            # Фон полоски здоровья (красный)
            health_bg_points = [
                (health_x - health_width/2, health_y - health_height/2),
                (health_x + health_width/2, health_y - health_height/2),
                (health_x + health_width/2, health_y + health_height/2),
                (health_x - health_width/2, health_y + health_height/2)
            ]
            arcade.draw_polygon_filled(health_bg_points, arcade.color.RED)

            # Текущее здоровье (зеленый)
            health_percent = max(0, self.health / 100)
            current_width = health_width * health_percent
            if current_width > 0:
                health_fg_points = [
                    (health_x - health_width/2, health_y - health_height/2),
                    (health_x - health_width/2 + current_width, health_y - health_height/2),
                    (health_x - health_width/2 + current_width, health_y + health_height/2),
                    (health_x - health_width/2, health_y + health_height/2)
                ]
                arcade.draw_polygon_filled(health_fg_points, arcade.color.GREEN)

    def update(self, delta_time):
        """Обновление движения"""
        if not self.is_alive:
            return

        # Ускорение
        acceleration_x = 0
        acceleration_y = 0

        if self.move_forward:
            acceleration_x += math.cos(math.radians(self.angle))
            acceleration_y += math.sin(math.radians(self.angle))
        if self.move_backward:
            acceleration_x -= math.cos(math.radians(self.angle)) * 0.7
            acceleration_y -= math.sin(math.radians(self.angle)) * 0.7

        # Поворот
        if self.rotate_left:
            self.angle += 180 * delta_time
        if self.rotate_right:
            self.angle -= 180 * delta_time

        # Нормализация
        length = math.hypot(acceleration_x, acceleration_y)
        if length > 0:
            acceleration_x = (acceleration_x / length) * self.acceleration * delta_time
            acceleration_y = (acceleration_y / length) * self.acceleration * delta_time

        # Обновление скорости
        self.velocity_x += acceleration_x
        self.velocity_y += acceleration_y

        # Ограничение скорости
        speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.velocity_x *= scale
            self.velocity_y *= scale

        # Трение
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction

        # Движение
        self.center_x += self.velocity_x * delta_time
        self.center_y += self.velocity_y * delta_time

    def get_corners(self):
        """Получить координаты углов танка"""
        half_width = self.width / 2
        half_height = self.height / 2

        corners = [
            (-half_width, -half_height),
            (half_width, -half_height),
            (half_width, half_height),
            (-half_width, half_height)
        ]

        angle_rad = math.radians(self.angle)
        cos_a = math.cos(angle_rad)
        sin_a = math.sin(angle_rad)

        rotated_corners = []
        for x, y in corners:
            x_rot = x * cos_a - y * sin_a + self.center_x
            y_rot = x * sin_a + y * cos_a + self.center_y
            rotated_corners.append((x_rot, y_rot))

        return rotated_corners

    def check_wall_collision(self, walls):
        """Проверка столкновений со стенами"""
        if not self.is_alive:
            return False

        corners = self.get_corners()

        for wall in walls:
            wall_left = wall.center_x - wall.width/2
            wall_right = wall.center_x + wall.width/2
            wall_bottom = wall.center_y - wall.height/2
            wall_top = wall.center_y + wall.height/2

            for corner_x, corner_y in corners:
                if (wall_left <= corner_x <= wall_right and
                    wall_bottom <= corner_y <= wall_top):
                    # Столкновение - отталкиваем танк
                    if corner_x < wall_left:
                        self.center_x = wall_left - self.width/2
                    elif corner_x > wall_right:
                        self.center_x = wall_right + self.width/2

                    if corner_y < wall_bottom:
                        self.center_y = wall_bottom - self.height/2
                    elif corner_y > wall_top:
                        self.center_y = wall_top + self.height/2

                    # Отскок
                    self.velocity_x *= -0.5
                    self.velocity_y *= -0.5
                    return True
        return False

class Bullet:
    """Класс пули"""
    def __init__(self, x, y, angle, is_player_bullet=True):
        self.center_x = x
        self.center_y = y
        self.radius = 5
        self.color = arcade.color.YELLOW if is_player_bullet else arcade.color.ORANGE
        self.velocity_x = math.cos(math.radians(angle)) * 400
        self.velocity_y = math.sin(math.radians(angle)) * 400
        self.lifetime = 2.0
        self.time_alive = 0
        self.is_player_bullet = is_player_bullet

    def draw(self):
        arcade.draw_circle_filled(
            self.center_x, self.center_y,
            self.radius, self.color
        )

    def update(self, delta_time):
        self.time_alive += delta_time
        self.center_x += self.velocity_x * delta_time
        self.center_y += self.velocity_y * delta_time

        # Проверка выхода за границы
        if (self.center_x < 0 or self.center_x > SCREEN_WIDTH or
            self.center_y < 0 or self.center_y > SCREEN_HEIGHT or
            self.time_alive > self.lifetime):
            return False
        return True

class Wall:
    """Класс стены"""
    def __init__(self, x, y, width=50, height=50):
        self.center_x = x
        self.center_y = y
        self.width = width
        self.height = height
        self.color = arcade.color.GRAY

    def draw(self):
        # Рисуем прямоугольник
        left = self.center_x - self.width/2
        right = self.center_x + self.width/2
        bottom = self.center_y - self.height/2
        top = self.center_y + self.height/2

        points = [
            (left, bottom),
            (right, bottom),
            (right, top),
            (left, top)
        ]

        arcade.draw_polygon_filled(points, self.color)

        # Контур
        outline_points = points + [points[0]]
        arcade.draw_line_strip(outline_points, arcade.color.BLACK, 2)

class Game(arcade.Window):
    """Главное окно игры"""
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Игровые объекты
        self.player = None
        self.enemies = []
        self.bullets = []
        self.walls = []

        # Время
        self.total_time = 0

        # Инициализация
        self.setup()

    def setup(self):
        """Настройка игры"""
        # Игрок
        self.player = Tank(100, 100, is_player=True)

        # Враги
        self.enemies = [
            Tank(600, 500, is_player=False),
            Tank(400, 300, is_player=False),
            Tank(700, 200, is_player=False)
        ]

        # Стены
        self.walls = []

        # Внешние стены
        wall_thickness = 20
        # Верхняя стена
        self.walls.append(Wall(SCREEN_WIDTH//2, SCREEN_HEIGHT - wall_thickness//2, SCREEN_WIDTH, wall_thickness))
        # Нижняя стена
        self.walls.append(Wall(SCREEN_WIDTH//2, wall_thickness//2, SCREEN_WIDTH, wall_thickness))
        # Левая стена
        self.walls.append(Wall(wall_thickness//2, SCREEN_HEIGHT//2, wall_thickness, SCREEN_HEIGHT))
        # Правая стена
        self.walls.append(Wall(SCREEN_WIDTH - wall_thickness//2, SCREEN_HEIGHT//2, wall_thickness, SCREEN_HEIGHT))

        # Внутренние стены
        self.walls.append(Wall(300, 400, 100, 20))
        self.walls.append(Wall(500, 300, 20, 100))
        self.walls.append(Wall(200, 200, 150, 20))
        self.walls.append(Wall(600, 100, 100, 20))
        self.walls.append(Wall(400, 500, 20, 100))

        # Пули
        self.bullets = []

        # Счёт
        self.score = 0
        self.game_over = False

        # Установка фона
        arcade.set_background_color(arcade.color.LIGHT_BLUE)

    def on_draw(self):
        """Отрисовка"""
        self.clear()

        # Стены
        for wall in self.walls:
            wall.draw()

        # Враги
        for enemy in self.enemies:
            enemy.draw()

        # Пули
        for bullet in self.bullets:
            bullet.draw()

        # Игрок
        self.player.draw()

        # Интерфейс
        arcade.draw_text(
            f"Счёт: {self.score}",
            10, SCREEN_HEIGHT - 30,
            arcade.color.BLACK, 20
        )

        arcade.draw_text(
            f"Здоровье: {self.player.health}",
            10, SCREEN_HEIGHT - 60,
            arcade.color.BLACK, 20
        )

        arcade.draw_text(
            "WASD - движение, ПРОБЕЛ - стрельба, R - рестарт",
            10, 10,
            arcade.color.BLACK, 16
        )

        # Сообщение о конце игры
        if self.game_over:
            # Фон сообщения
            bg_points = [
                (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 - 100),
                (SCREEN_WIDTH//2 + 200, SCREEN_HEIGHT//2 - 100),
                (SCREEN_WIDTH//2 + 200, SCREEN_HEIGHT//2 + 100),
                (SCREEN_WIDTH//2 - 200, SCREEN_HEIGHT//2 + 100)
            ]
            arcade.draw_polygon_filled(bg_points, arcade.color.WHITE)

            # Контур
            bg_outline = bg_points + [bg_points[0]]
            arcade.draw_line_strip(bg_outline, arcade.color.BLACK, 2)

            # Текст
            arcade.draw_text(
                "ИГРА ОКОНЧЕНА!",
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 40,
                arcade.color.RED, 36,
                anchor_x="center"
            )
            arcade.draw_text(
                f"Ваш счёт: {self.score}",
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 10,
                arcade.color.BLACK, 24,
                anchor_x="center"
            )
            arcade.draw_text(
                "Нажмите R для перезапуска",
                SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 50,
                arcade.color.BLUE, 20,
                anchor_x="center"
            )

    def on_key_press(self, key, modifiers):
        """Нажатие клавиш"""
        if self.game_over and key == arcade.key.R:
            self.setup()
            return

        # Управление игроком
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.move_forward = True
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.move_backward = True
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.rotate_left = True
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.rotate_right = True
        elif key == arcade.key.SPACE:
            # Стрельба
            if (self.player.is_alive and
                self.total_time - self.player.last_shot > self.player.shoot_cooldown):
                bullet = Bullet(
                    self.player.center_x + math.cos(math.radians(self.player.angle)) * 20,
                    self.player.center_y + math.sin(math.radians(self.player.angle)) * 20,
                    self.player.angle,
                    is_player_bullet=True
                )
                self.bullets.append(bullet)
                self.player.last_shot = self.total_time
        elif key == arcade.key.R:
            # Рестарт
            self.setup()
        elif key == arcade.key.ESCAPE:
            # Выход
            arcade.close_window()

    def on_key_release(self, key, modifiers):
        """Отпускание клавиш"""
        if key == arcade.key.W or key == arcade.key.UP:
            self.player.move_forward = False
        elif key == arcade.key.S or key == arcade.key.DOWN:
            self.player.move_backward = False
        elif key == arcade.key.A or key == arcade.key.LEFT:
            self.player.rotate_left = False
        elif key == arcade.key.D or key == arcade.key.RIGHT:
            self.player.rotate_right = False

    def enemy_ai(self, enemy, delta_time):
        """Искусственный интеллект врага"""
        if not enemy.is_alive:
            enemy.move_forward = False
            enemy.rotate_left = False
            enemy.rotate_right = False
            return

        # Расстояние до игрока
        dx = self.player.center_x - enemy.center_x
        dy = self.player.center_y - enemy.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        # Поворот к игроку
        if distance > 0 and self.player.is_alive:
            target_angle = math.degrees(math.atan2(dy, dx))

            # Плавный поворот к цели
            angle_diff = (target_angle - enemy.angle) % 360
            if angle_diff > 180:
                angle_diff -= 360

            enemy.rotate_left = angle_diff > 5
            enemy.rotate_right = angle_diff < -5

            # Движение
            enemy.move_forward = 50 < distance < 400

            # Стрельба
            if (distance < enemy.shoot_range and
                self.total_time - enemy.last_shot > enemy.shoot_cooldown and
                abs(angle_diff) < 15):
                # Выстрел
                bullet = Bullet(
                    enemy.center_x + math.cos(math.radians(enemy.angle)) * 20,
                    enemy.center_y + math.sin(math.radians(enemy.angle)) * 20,
                    enemy.angle,
                    is_player_bullet=False
                )
                self.bullets.append(bullet)
                enemy.last_shot = self.total_time

    def check_collision_bullet_wall(self, bullet):
        """Проверка столкновения пули со стеной"""
        for wall in self.walls:
            wall_left = wall.center_x - wall.width/2
            wall_right = wall.center_x + wall.width/2
            wall_bottom = wall.center_y - wall.height/2
            wall_top = wall.center_y + wall.height/2

            if (wall_left <= bullet.center_x <= wall_right and
                wall_bottom <= bullet.center_y <= wall_top):
                return True
        return False

    def check_collision_bullet_tank(self, bullet, tank):
        """Проверка столкновения пули с танком"""
        if not tank.is_alive:
            return False

        # Проверяем расстояние от центра пули до центра танка
        dx = bullet.center_x - tank.center_x
        dy = bullet.center_y - tank.center_y
        distance = math.sqrt(dx*dx + dy*dy)

        # Используем упрощенную проверку - круг вокруг танка
        tank_radius = max(tank.width, tank.height) / 2
        return distance < (tank_radius + bullet.radius)

    def on_update(self, delta_time):
        """Обновление игры"""
        if self.game_over:
            return

        self.total_time += delta_time

        # Обновление игрока
        if self.player.is_alive:
            self.player.update(delta_time)
            # Проверка столкновений игрока со стенами
            self.player.check_wall_collision(self.walls)

        # Обновление врагов
        for enemy in self.enemies:
            self.enemy_ai(enemy, delta_time)
            if enemy.is_alive:
                enemy.update(delta_time)
                # Проверка столкновений врагов со стенами
                enemy.check_wall_collision(self.walls)

        # Обновление пуль
        bullets_to_remove = []
        for bullet in self.bullets:
            if not bullet.update(delta_time):
                bullets_to_remove.append(bullet)
                continue

            # Столкновения пуль со стенами
            if self.check_collision_bullet_wall(bullet):
                bullets_to_remove.append(bullet)
                continue

            # Столкновения пуль игрока с врагами
            if bullet.is_player_bullet:
                for enemy in self.enemies:
                    if self.check_collision_bullet_tank(bullet, enemy):
                        bullets_to_remove.append(bullet)
                        enemy.health -= 25
                        if enemy.health <= 0:
                            enemy.is_alive = False
                            self.score += 100
                        break

            # Столкновения пуль врагов с игроком
            elif not bullet.is_player_bullet:
                if self.player.is_alive and self.check_collision_bullet_tank(bullet, self.player):
                    bullets_to_remove.append(bullet)
                    self.player.health -= 20
                    if self.player.health <= 0:
                        self.player.is_alive = False
                        self.player.health = 0
                        self.game_over = True

        # Удаление пуль
        for bullet in bullets_to_remove:
            if bullet in self.bullets:
                self.bullets.remove(bullet)

        # Проверка победы
        if not self.game_over and self.player.is_alive:
            all_enemies_dead = all(not enemy.is_alive for enemy in self.enemies)
            if all_enemies_dead:
                self.game_over = True
                self.score += 500

def main():
    """Запуск игры"""
    window = Game()
    arcade.run()

if __name__ == "__main__":
    main()