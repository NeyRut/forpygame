import pygame
import random

pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

CELL_SIZE = 40
MARGIN = 5

ROWS = 9
COLS = 9
MINES = 10


def create_window(width, height):
    return pygame.display.set_mode((width, height))


def draw_text(surface, text, size, x, y, color=BLACK):
    font = pygame.font.SysFont("Arial", size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)


def generate_mines(rows, cols, mines, start_cell):
    mine_positions = set()
    while len(mine_positions) < mines:
        row = random.randint(0, rows - 1)
        col = random.randint(0, cols - 1)
        if (row, col) != start_cell and (row, col) not in mine_positions:
            mine_positions.add((row, col))
    return mine_positions


def count_adjacent_mines(row, col, mine_positions, rows, cols):
    count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            nr, nc = row + dr, col + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) in mine_positions:
                count += 1
    return count


def reveal_empty_cells(row, col, revealed, mine_positions, rows, cols):
    if (row, col) in revealed:
        return
    revealed.add((row, col))
    if count_adjacent_mines(row, col, mine_positions, rows, cols) == 0:
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in revealed:
                    reveal_empty_cells(nr, nc, revealed, mine_positions, rows, cols)


def draw_board(screen, board, revealed, flagged, mine_positions, explosion_position, rows, cols, cell_size, margin):
    for r in range(rows):
        for c in range(cols):
            rect = pygame.Rect(c * (cell_size + margin), r * (cell_size + margin), cell_size, cell_size)
            if (r, c) in revealed:
                pygame.draw.rect(screen, WHITE, rect)
                if (r, c) == explosion_position:
                    pygame.draw.rect(screen, RED, rect)
                    draw_text(screen, "X", int(cell_size // 2), rect.x + cell_size // 3, rect.y + cell_size // 4, BLACK)
                elif (r, c) in mine_positions:
                    draw_text(screen, "*", int(cell_size // 2), rect.x + cell_size // 3, rect.y + cell_size // 4, RED)
                else:
                    adjacent_mines = count_adjacent_mines(r, c, mine_positions, rows, cols)
                    if adjacent_mines > 0:
                        draw_text(screen, str(adjacent_mines), int(cell_size // 2), rect.x + cell_size // 3, rect.y + cell_size // 4, BLUE)
            elif (r, c) in flagged:
                pygame.draw.rect(screen, GREEN, rect)
                draw_text(screen, "F", int(cell_size // 2), rect.x + cell_size // 3, rect.y + cell_size // 4, BLACK)
            else:
                pygame.draw.rect(screen, GRAY, rect)
            pygame.draw.rect(screen, BLACK, rect, 1)


def main_menu():
    screen = create_window(300, 200)
    pygame.display.set_caption("Меню Сапёра")
    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)
        draw_text(screen, "=== Меню Сапёра ===", 20, 20, 20)
        draw_text(screen, "1. Новая игра", 20, 20, 60)
        draw_text(screen, "2. Настройки", 20, 20, 100)
        draw_text(screen, "3. Выход", 20, 20, 140)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "new_game"
                elif event.key == pygame.K_2:
                    return "settings"
                elif event.key == pygame.K_3:
                    pygame.quit()
                    exit()


def settings_menu():
    screen = create_window(400, 200)
    pygame.display.set_caption("Настройки Сапёра")
    clock = pygame.time.Clock()

    rows = ROWS
    cols = COLS
    mines = MINES

    input_boxes = [
        {"text": "Количество строк:", "var": "rows", "value": str(rows)},
        {"text": "Количество столбцов:", "var": "cols", "value": str(cols)},
        {"text": "Количество мин:", "var": "mines", "value": str(mines)}
    ]
    active_box = None

    while True:
        screen.fill(WHITE)
        y = 20
        for i, box in enumerate(input_boxes):
            draw_text(screen, box["text"], 20, 20, y)
            draw_text(screen, box["value"], 20, 250, y)
            y += 40

        draw_text(screen, "Нажмите Enter для сохранения", 20, 20, y)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    try:
                        rows = int(input_boxes[0]["value"])
                        cols = int(input_boxes[1]["value"])
                        mines = int(input_boxes[2]["value"])
                        if mines >= rows * cols or mines <= 0:
                            raise ValueError
                        return rows, cols, mines
                    except ValueError:
                        print("Некорректные значения!")
                elif event.key == pygame.K_BACKSPACE:
                    if active_box is not None:
                        input_boxes[active_box]["value"] = input_boxes[active_box]["value"][:-1]
                else:
                    if active_box is not None:
                        input_boxes[active_box]["value"] += event.unicode
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for i, box in enumerate(input_boxes):
                    if 250 <= mouse_x <= 350 and 20 + i * 40 <= mouse_y <= 60 + i * 40:
                        active_box = i
                        break
                else:
                    active_box = None


def play_game(rows, cols, mines):
    screen_width = cols * (CELL_SIZE + MARGIN) + MARGIN
    screen_height = rows * (CELL_SIZE + MARGIN) + MARGIN + 40
    screen = create_window(screen_width, screen_height)
    pygame.display.set_caption("Сапёр")

    board = [[0 for _ in range(cols)] for _ in range(rows)]
    revealed = set()
    flagged = set()
    mine_positions = set()
    explosion_position = None
    game_over = False
    win = False

    clock = pygame.time.Clock()

    while True:
        screen.fill(WHITE)
        draw_board(screen, board, revealed, flagged, mine_positions, explosion_position, rows, cols, CELL_SIZE, MARGIN)

        if game_over:
            draw_text(screen, "Вы проиграли! Нажмите ESC для выхода в меню.", 20, 10, screen_height - 35, RED)
        elif win:
            draw_text(screen, "Вы выиграли! Нажмите ESC для выхода в меню.", 20, 10, screen_height - 35, GREEN)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and not win:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                col = mouse_x // (CELL_SIZE + MARGIN)
                row = mouse_y // (CELL_SIZE + MARGIN)
                if 0 <= row < rows and 0 <= col < cols:
                    if event.button == 1:
                        if (row, col) not in flagged:
                            if not mine_positions:
                                mine_positions = generate_mines(rows, cols, mines, (row, col))
                            if (row, col) in mine_positions:
                                game_over = True
                                explosion_position = (row, col)
                            else:
                                reveal_empty_cells(row, col, revealed, mine_positions, rows, cols)
                                if len(revealed) + len(mine_positions) == rows * cols:
                                    win = True
                    elif event.button == 3:
                        if (row, col) not in revealed:
                            if (row, col) in flagged:
                                flagged.remove((row, col))
                            else:
                                flagged.add((row, col))

if __name__ == "__main__":
    while True:
        choice = main_menu()
        if choice == "new_game":
            play_game(ROWS, COLS, MINES)
        elif choice == "settings":
            settings = settings_menu()
            if settings:
                ROWS, COLS, MINES = settings