import pygame
import random
import sys
import time
import os

pygame.init()
pygame.mixer.init()

# Nhạc nền (loop vô hạn)
pygame.mixer.music.load("background.mp3")
pygame.mixer.music.play(-1)

key_sound = pygame.mixer.Sound("keypress.wav")

# Kích thước màn hình
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Typing Speed")
FONT = pygame.font.SysFont("consolas", 32)
BIG_FONT = pygame.font.SysFont("consolas", 48, bold=True)

# Import danh sách từ vựng
from english3000 import WORDS

clock = pygame.time.Clock()

# ---------------- High score ----------------
HIGHSCORE_FILE = "highscores.txt"

def load_highscores():
    scores = {}
    if os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    name, sc = line.strip().split(":")
                    scores[name] = int(sc)
                except:
                    pass
    return scores

def save_highscores(scores):
    with open(HIGHSCORE_FILE, "w", encoding="utf-8") as f:
        for name, sc in scores.items():
            f.write(f"{name}:{sc}\n")

# Dictionary lưu kỷ lục
high_scores = load_highscores()
# --------------------------------------------

class FallingWord:
    def __init__(self, word, x, y=0, speed=1):
        self.word = word
        self.x = x
        self.y = y
        self.speed = speed

    def update(self):
        self.y += self.speed

    def draw(self, win):
        label = FONT.render(self.word, True, (255, 255, 0))
        win.blit(label, (self.x, self.y))

    def first_char(self):
        return self.word[0] if self.word else None

    def remove_first(self):
        self.word = self.word[1:]

    def is_done(self):
        return len(self.word) == 0

def show_mode_menu():
    choosing = True
    mode = 1
    while choosing:
        WIN.fill((30, 30, 30))
        title = BIG_FONT.render("CHỌN CHẾ ĐỘ", True, (0, 255, 255))
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))
        m1 = FONT.render("1 - Survival: Tốc độ tăng dần", True, (255, 255, 0))
        m2 = FONT.render("2 - 60 Seconds: Tốc độ cao nhất", True, (255, 255, 0))
        WIN.blit(m1, (WIDTH // 2 - m1.get_width() // 2, 220))
        WIN.blit(m2, (WIDTH // 2 - m2.get_width() // 2, 270))
        note = FONT.render("Nhấn 1 hoặc 2 để chọn chế độ", True, (200, 200, 200))
        WIN.blit(note, (WIDTH // 2 - note.get_width() // 2, 400))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    mode = 1
                    choosing = False
                elif event.key == pygame.K_2:
                    mode = 2
                    choosing = False
    return mode

def get_survival_speed(score):
    if score < 15:
        return 10
    elif score < 30:
        return 12
    elif score < 50:
        return 14
    else:
        return 16

def get_nickname():
    nickname = ""
    entering = True
    while entering:
        WIN.fill((30, 30, 30))
        title = BIG_FONT.render("NHẬP NICKNAME", True, (0, 255, 255))
        WIN.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        prompt = FONT.render("Nhập tên rồi nhấn ENTER:", True, (200, 200, 200))
        WIN.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 200))

        name_surface = FONT.render(nickname, True, (255, 255, 0))
        WIN.blit(name_surface, (WIDTH // 2 - name_surface.get_width() // 2, 300))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if nickname.strip() != "":
                        entering = False
                elif event.key == pygame.K_BACKSPACE:
                    nickname = nickname[:-1]
                else:
                    if len(event.unicode) == 1 and event.unicode.isprintable():
                        nickname += event.unicode
    return nickname

def show_gameover(nickname, score):
    global high_scores

    # Lấy kỷ lục cũ
    old_record = high_scores.get(nickname, 0)

    # Nếu điểm mới cao hơn thì cập nhật
    if score > old_record:
        high_scores[nickname] = score
        save_highscores(high_scores)
        old_record = score  # cập nhật để hiển thị luôn

    waiting = True
    while waiting:
        WIN.fill((30, 30, 30))
        gameover = BIG_FONT.render(f"{nickname}, Score: {score}", True, (255, 50, 50))
        WIN.blit(gameover, (WIDTH // 2 - gameover.get_width() // 2, HEIGHT // 2 - 100))

        record_text = FONT.render(f"Kỷ lục: {old_record}", True, (0, 255, 0))
        WIN.blit(record_text, (WIDTH // 2 - record_text.get_width() // 2, HEIGHT // 2 - 30))

        note = FONT.render("Nhấn R để quay lại menu - Nhấn Q để thoát", True, (200, 200, 200))
        WIN.blit(note, (WIDTH // 2 - note.get_width() // 2, HEIGHT // 2 + 50))

        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r:
                    waiting = False

def main():
    nickname = None
    while True:
        run = True
        words = []
        spawn_timer = 0
        score = 0
        lives = 5

        if nickname is None:
            nickname = get_nickname()

        mode = show_mode_menu()

        if mode == 2:
            speed = 6
            start_time = time.time()
        else:
            speed = 2

        while run:
            WIN.fill((30, 30, 30))
            clock.tick(60)
            if mode == 1:
                speed = get_survival_speed(score)

            # Sinh từ mới
            spawn_timer += 1
            if spawn_timer > 60:
                new_word = random.choice(WORDS)
                x = random.randint(50, WIDTH - 100)
                words.append(FallingWord(new_word, x, speed=speed))
                spawn_timer = 0

            # Sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    key_sound.play()
                    if event.key == pygame.K_ESCAPE:
                        run = False
                    else:
                        key = event.unicode
                        for w in words:
                            if w.first_char() == key:
                                w.remove_first()
                                if w.is_done():
                                    score += 1
                                    words.remove(w)
                                break

            # Cập nhật & vẽ
            for w in words[:]:
                w.update()
                if w.y > HEIGHT:
                    lives -= 1
                    words.remove(w)

            for w in words:
                w.draw(WIN)

            # HUD & Game over
            if mode == 2:
                elapsed = int(time.time() - start_time)
                remain = max(0, 60 - elapsed)
                hud = FONT.render(f"Score: {score}   Time: {remain}s", True, (255, 255, 255))
                WIN.blit(hud, (10, 10))
                if remain <= 0:
                    show_gameover(nickname, score)
                    run = False
            else:
                hud = FONT.render(f"Score: {score}   Lives: {lives}   Speed: {speed}", True, (255, 255, 255))
                WIN.blit(hud, (10, 10))
                if lives <= 0:
                    show_gameover(nickname, score)
                    run = False

            pygame.display.update()

if __name__ == "__main__":
    main()

