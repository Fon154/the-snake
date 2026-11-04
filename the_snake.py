from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

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
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игровых объектов."""

    def __init__(
        self,
        body_color: tuple = BOARD_BACKGROUND_COLOR
    ):
        """Инициализирует игровой объект.

        Args:
            body_color: Цвет тела игрового объекта.
        """
        self.body_color = body_color
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

    def draw(self):
        """Отрисовывает игровой объект."""
        pass


class Apple(GameObject):
    """Класс яблока, которое появляется на игровом поле."""

    def __init__(self):
        """Инициализирует яблоко"""
        super().__init__(APPLE_COLOR)

    def randomize_position(self):
        """Устанавливает яблоку случайную позицию на поле."""
        custom_x = randint(0, GRID_WIDTH - 1) * GRID_SIZE
        custom_y = randint(0, GRID_HEIGHT - 1) * GRID_SIZE
        self.position = (custom_x, custom_y)

    def draw(self):
        """Отрисовывает яблоко на игровом поле."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """Класс змейки, управляющий ее движением и состоянием."""

    def __init__(self):
        """Инициализирует змейку."""
        super().__init__(SNAKE_COLOR)
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None

    def get_head_position(self) -> tuple:
        """Возвращает координаты головы змейки.

        Returns:
            Координаты головы змейки.
        """
        return self.positions[0]

    def move(self):
        """Перемещает змейку на одну ячейку в текущем направлении."""
        current_head_position = self.get_head_position()

        new_head_position = (
            (
                current_head_position[0]
                + self.direction[0] * GRID_SIZE
            ) % SCREEN_WIDTH,
            (
                current_head_position[1]
                + self.direction[1] * GRID_SIZE
            ) % SCREEN_HEIGHT
        )

        self.positions.insert(0, new_head_position)
        self.last = self.positions[-1]

        if len(self.positions) > self.length:
            self.positions.pop()

    def update_direction(self):
        """Обновляет текущее направление змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает змейку на игровом поле."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def reset(self):
        """Сбрасывает змейку в начальное состояние."""
        # Сбросить змейку в начальное состояние, повторно вызывая конструктор
        self.__init__()
        self.direction = choice([RIGHT, LEFT, UP, DOWN])
        # Очистить экран
        screen.fill(BOARD_BACKGROUND_COLOR)


def handle_keys(game_object):
    """Обрабатывает нажатия клавиш управления.

    Args:
        game_object: Игровой объект, направление которого изменяется.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Запускает основной цикл игры."""
    # Инициализация PyGame:
    pygame.init()

    # Создание экземпляров классов.
    snake = Snake()
    apple = Apple()

    while True:
        clock.tick(SPEED)

        # Основная логика игры
        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Проверка съеденного яблока
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()

        # Проверка столкновения змейки с собой
        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()

        # Отрисовка
        snake.draw()
        apple.draw()

        # Обновление экрана
        pygame.display.update()


if __name__ == '__main__':
    main()
