import pygame
import random
import os
import json

# Инициализация Pygame
pygame.init()

# Параметры окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Арканоид")

# Загрузка фонов
try:
    background = pygame.image.load(os.path.join("fon.jpg"))
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
    level_complete_background = pygame.image.load(os.path.join("complete.jpg"))
    level_complete_background = pygame.transform.scale(level_complete_background, (WIDTH, HEIGHT))
except pygame.error as e:
    print(f"Ошибка загрузки фонового изображения: {e}")
    background = pygame.Surface((WIDTH, HEIGHT))
    background.fill((255, 255, 255))  # Белый фон, если изображение не загружено
    level_complete_background = pygame.Surface((WIDTH, HEIGHT))
    level_complete_background.fill((0, 255, 0))  # Зелёный фон для завершения уровня

# Цвета
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

# Шрифты
font = pygame.font.Font(None, 50)
small_font = pygame.font.Font(None, 30)

# Кнопки
start_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 - 25, 150, 50)
back_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 50, 150, 50)
pause_button = pygame.Rect(WIDTH - 120, HEIGHT - 50, 100, 30)  # Смещена вниз
resume_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 50)
restart_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 100, 150, 50)
exit_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 150, 150, 50)
rename_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 200, 150, 50)  # Кнопка переименования
delete_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 250, 150, 50)  # Кнопка удаления
exit_to_menu_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2 + 50, 150, 50)  # Кнопка выхода в меню

# Параметры платформы
PADDLE_WIDTH, PADDLE_HEIGHT = 100, 10

# Параметры мяча
BALL_SIZE = 10

# Параметры блоков
BLOCK_WIDTH, BLOCK_HEIGHT = 60, 20

# Переменные игры
level = 1
score = 0
playing = False
game_over = False
paused = False
level_complete = False

# Функции для работы с профилями
PROFILES_DIR = "profiles"

def ensure_profiles_dir():
    if not os.path.exists(PROFILES_DIR):
        os.makedirs(PROFILES_DIR)

def save_profile(profile_name, score):
    ensure_profiles_dir()
    profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as file:
            data = json.load(file)
        if score > data.get("max_score", 0):
            data["max_score"] = score
    else:
        data = {"max_score": score}
    with open(profile_path, 'w') as file:
        json.dump(data, file)

def load_profile(profile_name):
    profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
    if os.path.exists(profile_path):
        with open(profile_path, 'r') as file:
            data = json.load(file)
        return data.get("max_score", 0)
    return 0

def list_profiles():
    ensure_profiles_dir()
    return [f.replace(".json", "") for f in os.listdir(PROFILES_DIR) if f.endswith(".json")]

def rename_profile(old_name, new_name):
    ensure_profiles_dir()
    old_path = os.path.join(PROFILES_DIR, f"{old_name}.json")
    new_path = os.path.join(PROFILES_DIR, f"{new_name}.json")
    if os.path.exists(old_path):
        os.rename(old_path, new_path)

def delete_profile(profile_name):
    ensure_profiles_dir()
    profile_path = os.path.join(PROFILES_DIR, f"{profile_name}.json")
    if os.path.exists(profile_path):
        os.remove(profile_path)

# Инициализация профилей
current_profile = None
profiles = list_profiles()
profile_selection = True
renaming = False
new_profile_name = ""

def reset_game():
    global paddle, ball, ball_speed, blocks, playing, game_over, score
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
    ball_speed = [4, -4]
    blocks = []
    for x in range(10, WIDTH - 10, BLOCK_WIDTH + 10):
        for y in range(50, 200, BLOCK_HEIGHT + 10):
            block = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
            color = random.choice(COLORS)
            blocks.append((block, color))
    playing = False
    game_over = False
    score = 0

reset_game()

# Функция отображения текста
def draw_text(text, x, y, color=BLACK, font_type=font):
    img = font_type.render(text, True, color)
    text_rect = img.get_rect(center=(x, y))
    screen.blit(img, text_rect)

def create_blocks():
    blocks = []
    for x in range(10, WIDTH - BLOCK_WIDTH - 10, BLOCK_WIDTH + 10):
        for y in range(50, 200, BLOCK_HEIGHT + 10):
            block = pygame.Rect(x, y, BLOCK_WIDTH, BLOCK_HEIGHT)
            color = random.choice(COLORS)
            blocks.append((block, color))
    return blocks

def create_walls(level):
    walls = []
    if level > 1:
        for _ in range(level - 1):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(250, 400)
            walls.append(pygame.Rect(x, y, 80, 10))
    return walls

def reset_level():
    global paddle, ball, ball_speed, blocks, walls, level_complete
    paddle = pygame.Rect(WIDTH // 2 - PADDLE_WIDTH // 2, HEIGHT - 30, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball = pygame.Rect(WIDTH // 2, HEIGHT // 2, BALL_SIZE, BALL_SIZE)
    ball_speed = [4, -4]
    blocks = create_blocks()
    walls = create_walls(level)
    level_complete = False

def reset_game():
    global level, score, game_over, playing
    level = 1
    score = 0
    game_over = False
    playing = False
    reset_level()

reset_game()

# Главный игровой цикл
running = True
while running:
    screen.blit(background, (0, 0))
    mouse_x, _ = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if profile_selection:
                for i, profile in enumerate(profiles):
                    profile_rect = pygame.Rect(WIDTH // 2 - 75, 150 + i * 60, 150, 50)
                    if profile_rect.collidepoint(event.pos):
                        current_profile = profile
                        profile_selection = False
                new_profile_rect = pygame.Rect(WIDTH // 2 - 75, 150 + len(profiles) * 60, 150, 50)
                if new_profile_rect.collidepoint(event.pos):
                    renaming = True
                    new_profile_name = ""
                rename_rect = pygame.Rect(WIDTH // 2 - 75, 150 + (len(profiles) + 1) * 60, 150, 50)
                if rename_rect.collidepoint(event.pos) and current_profile:
                    renaming = True
                    new_profile_name = current_profile
                delete_rect = pygame.Rect(WIDTH // 2 - 75, 150 + (len(profiles) + 2) * 60, 150, 50)
                if delete_rect.collidepoint(event.pos) and current_profile:
                    delete_profile(current_profile)
                    profiles = list_profiles()
                    current_profile = None
            elif not playing and not game_over and start_button.collidepoint(event.pos):
                playing = True
            elif game_over and back_button.collidepoint(event.pos):
                reset_game()
            elif level_complete and resume_button.collidepoint(event.pos):
                level += 1
                reset_level()
                playing = True
            elif paused and resume_button.collidepoint(event.pos):
                paused = False
            elif paused and exit_to_menu_button.collidepoint(event.pos):
                profile_selection = True
                paused = False
                playing = False
                game_over = False
                level_complete = False
                reset_game()
            elif playing and pause_button.collidepoint(event.pos):
                paused = True
            elif game_over and restart_button.collidepoint(event.pos):
                reset_game()
                playing = True
            elif game_over and exit_button.collidepoint(event.pos):
                running = False
        if event.type == pygame.KEYDOWN:
            if renaming:
                if event.key == pygame.K_RETURN:
                    if new_profile_name:
                        if current_profile:
                            rename_profile(current_profile, new_profile_name)
                            current_profile = new_profile_name
                        else:
                            save_profile(new_profile_name, 0)
                            current_profile = new_profile_name
                        profiles = list_profiles()
                        renaming = False
                elif event.key == pygame.K_BACKSPACE:
                    new_profile_name = new_profile_name[:-1]
                else:
                    new_profile_name += event.unicode

    if profile_selection:
        draw_text("Выберите профиль", WIDTH // 2, 100)
        for i, profile in enumerate(profiles):
            profile_rect = pygame.Rect(WIDTH // 2 - 75, 150 + i * 60, 150, 50)
            pygame.draw.rect(screen, BLUE, profile_rect, border_radius=15)
            draw_text(profile, profile_rect.centerx, profile_rect.centery, WHITE)
        new_profile_rect = pygame.Rect(WIDTH // 2 - 75, 150 + len(profiles) * 60, 150, 50)
        pygame.draw.rect(screen, GREEN, new_profile_rect, border_radius=15)
        draw_text("Новый профиль", new_profile_rect.centerx, new_profile_rect.centery, WHITE)
        if current_profile:
            rename_rect = pygame.Rect(WIDTH // 2 - 75, 150 + (len(profiles) + 1) * 60, 150, 50)
            pygame.draw.rect(screen, BLUE, rename_rect, border_radius=15)
            draw_text("Переименовать", rename_rect.centerx, rename_rect.centery, WHITE)
            delete_rect = pygame.Rect(WIDTH // 2 - 75, 150 + (len(profiles) + 2) * 60, 150, 50)
            pygame.draw.rect(screen, RED, delete_rect, border_radius=15)
            draw_text("Удалить", delete_rect.centerx, delete_rect.centery, WHITE)
        if renaming:
            draw_text(f"Имя: {new_profile_name}", WIDTH // 2, HEIGHT - 100, WHITE)
    elif not playing and not game_over:
        draw_text("ARCANOID", WIDTH // 2, HEIGHT // 3)
        pygame.draw.rect(screen, BLUE, start_button, border_radius=15)
        draw_text("Старт", start_button.centerx, start_button.centery, WHITE)
    elif paused:
        draw_text("Пауза", WIDTH // 2, HEIGHT // 3)
        pygame.draw.rect(screen, BLUE, resume_button, border_radius=15)
        draw_text("Далее", resume_button.centerx, resume_button.centery, WHITE)
        pygame.draw.rect(screen, BLUE, exit_to_menu_button, border_radius=15)
        draw_text("Выход в меню", exit_to_menu_button.centerx, exit_to_menu_button.centery, WHITE)
    elif level_complete:
        screen.blit(level_complete_background, (0, 0))
        draw_text(f"Уровень {level} пройден!", WIDTH // 2, HEIGHT // 3, WHITE)
        pygame.draw.rect(screen, BLUE, resume_button, border_radius=15)
        draw_text("Далее", resume_button.centerx, resume_button.centery, WHITE)
    elif game_over:
        try:
            game_over_background = pygame.image.load(os.path.join("finish.jpg"))
            game_over_background = pygame.transform.scale(game_over_background, (WIDTH, HEIGHT))
            screen.blit(game_over_background, (0, 0))
        except pygame.error as e:
            print(f"Ошибка загрузки фонового изображения: {e}")
            screen.fill(WHITE)
        draw_text("GAME OVER", WIDTH // 2, HEIGHT // 3)
        draw_text(f"Счёт: {score}", WIDTH // 2, HEIGHT // 2, BLACK)
        pygame.draw.rect(screen, BLUE, back_button, border_radius=15)
        draw_text("Назад", back_button.centerx, back_button.centery, WHITE)
        pygame.draw.rect(screen, BLUE, restart_button, border_radius=15)
        draw_text("Рестарт", restart_button.centerx, restart_button.centery, WHITE)
        pygame.draw.rect(screen, BLUE, exit_button, border_radius=15)
        draw_text("Выход", exit_button.centerx, exit_button.centery, WHITE)
        save_profile(current_profile, score)
    elif playing:
        paddle.x = max(0, min(WIDTH - PADDLE_WIDTH, mouse_x - PADDLE_WIDTH // 2))
        ball.move_ip(*ball_speed)

        if ball.left <= 0 or ball.right >= WIDTH:
            ball_speed[0] = -ball_speed[0]
        if ball.top <= 0:
            ball_speed[1] = -ball_speed[1]
        if ball.colliderect(paddle) and ball_speed[1] > 0:
            ball_speed[1] = -ball_speed[1]

        for block, color in blocks[:]:
            if ball.colliderect(block):
                blocks.remove((block, color))
                ball_speed[1] = -ball_speed[1]
                score += 10
                break

        for wall in walls:
            if ball.colliderect(wall):
                ball_speed[1] = -ball_speed[1]
                break

        if ball.bottom >= HEIGHT:
            game_over = True
            playing = False
        if not blocks:
            level_complete = True
            playing = False

        pygame.draw.rect(screen, BLUE, paddle)
        pygame.draw.ellipse(screen, RED, ball)
        for block, color in blocks:
            pygame.draw.rect(screen, color, block)
        for wall in walls:
            pygame.draw.rect(screen, BLACK, wall)

        draw_text(f"Счёт: {score}", WIDTH // 2, 20, WHITE)
        draw_text(f"Уровень: {level}", 100, 20, WHITE)
        draw_text(f"Профиль: {current_profile}", WIDTH - 150, 20, WHITE, small_font)

        pygame.draw.rect(screen, BLUE, pause_button, border_radius=15)
        draw_text("Пауза", pause_button.centerx, pause_button.centery, WHITE, small_font)

    pygame.display.flip()
    pygame.time.delay(16)

pygame.quit()
