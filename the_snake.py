from random import choice

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
SCREEN_CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Словарь направлений
DIRECTION_MAP = {
    (LEFT, pg.K_UP): UP,
    (RIGHT, pg.K_UP): UP,
    (LEFT, pg.K_w): UP,
    (RIGHT, pg.K_w): UP,

    (LEFT, pg.K_DOWN): DOWN,
    (RIGHT, pg.K_DOWN): DOWN,
    (LEFT, pg.K_s): DOWN,
    (RIGHT, pg.K_s): DOWN,

    (UP, pg.K_LEFT): LEFT,
    (DOWN, pg.K_LEFT): LEFT,
    (UP, pg.K_a): LEFT,
    (DOWN, pg.K_a): LEFT,

    (UP, pg.K_RIGHT): RIGHT,
    (DOWN, pg.K_RIGHT): RIGHT,
    (UP, pg.K_d): RIGHT,
    (DOWN, pg.K_d): RIGHT,
}

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(
        self,
        position: tuple = SCREEN_CENTER,
        body_color: tuple = BOARD_BACKGROUND_COLOR
    ):
        """Инициализирует игровой объект.

        Args:
            position: Положение объекта на экране.
            body_color: Цвет тела игрового объекта.
        """
        self.position = position
        self.body_color = body_color

    def draw(self):
        """Отрисовывает игровой объект."""
        raise NotImplementedError(
            'Метод draw() должен быть обязательно'
            'реализован в дочернем классе!'
        )

    def draw_cell(
        self,
        position: tuple,
        color=None
    ):
        """Отрисовывает одну ячейку игрового поля."""
        if color is None:
            color = self.body_color

        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """Класс яблока, которое появляется на игровом поле."""

    def __init__(
            self,
            occupied_positions: list | None = None,
            position: tuple = SCREEN_CENTER,
            body_color: tuple = APPLE_COLOR
    ):
        """Инициализирует яблоко"""
        super().__init__(
            position=position,
            body_color=body_color
        )

        if occupied_positions is None:
            occupied_positions = []

        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions: list) -> bool:
        """Устанавливает яблоку случайную позицию на поле."""
        free_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied_positions
        ]

        if not free_positions:
            return False

        self.position = choice(free_positions)
        return True

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Класс змейки, управляющий ее движением и состоянием."""

    def __init__(
        self,
        position: tuple = SCREEN_CENTER,
        body_color: tuple = SNAKE_COLOR
    ):
        """Инициализирует змейку."""
        super().__init__(
            position=position,
            body_color=body_color
        )
        self.reset()

    def get_head_position(self) -> tuple:
        """Возвращает координаты головы змейки.

        Returns:
            Координаты головы змейки.
        """
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну ячейку в текущем направлении."""
        current_head_position_x, current_head_position_y \
            = self.get_head_position()

        direction_x, direction_y = self.direction

        new_head_position = (
            (
                current_head_position_x
                + direction_x * GRID_SIZE
            ) % SCREEN_WIDTH,
            (
                current_head_position_y
                + direction_y * GRID_SIZE
            ) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head_position)
        self.last = self.positions.pop()

    def update_direction(self):
        """Обновляет текущее направление змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        # Отрисовка головы
        self.draw_cell(self.get_head_position())

        # Затирание последнего сегмента
        if self.last is not None:
            last_rect = pg.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def grow(self):
        """Увеличивает длину змейки на один сегмент."""
        if self.last is not None:
            self.positions.append(self.last)
            self.last = None

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        # Сбросить змейку в начальное состояние
        self.positions = [self.position]
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш управления.

    Args:
        game_object: Игровой объект, направление которого изменяется.
    """
    for event in pg.event.get():
        # Выход из игры
        if event.type == pg.QUIT:
            pg.quit()
            raise SystemExit
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                pg.quit()
                raise SystemExit

            new_direction = DIRECTION_MAP.get(
                (game_object.direction, event.key)
            )

            if new_direction is not None:
                game_object.next_direction = new_direction


def main():
    """Запускает основной цикл игры."""
    # Инициализация pg:
    pg.init()

    # Создание экземпляров классов.
    snake = Snake()
    apple = Apple(snake.positions)

    while True:
        clock.tick(SPEED)

        # Основная логика игры
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка съеденного яблока
        if snake.get_head_position() == apple.position:
            snake.grow()

            if not apple.randomize_position(snake.positions):
                break

        # Проверка столкновения змейки с собой
        elif snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        # Отрисовка
        snake.draw()
        apple.draw()

        # Обновление экрана
        pg.display.update()


if __name__ == '__main__':
    main()
