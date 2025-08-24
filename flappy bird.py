import pygame
import sys
import random
import os 
# ---------- Ayarlar ----------
WIDTH, HEIGHT = 400, 600
FPS = 60

BG_COLOR = (135, 206, 235)  # gökyüzü mavisi
BIRD_COLOR = (255, 215, 0)  # sarı
PIPE_COLOR = (34, 139, 34)  # yeşil
GROUND_COLOR = (222, 184, 135)

GRAVITY = 0.5
JUMP_STRENGTH = -8.5

PIPE_WIDTH = 70
PIPE_GAP = 150
PIPE_SPEED = 3
PIPE_FREQUENCY = 1500  # ms

FONT_NAME = None  # varsayılan font

#ses dosyaları (oyun klasöründe jump.wav ve hit.wav olmalı)
pygame.mixer.init()
jump_sound=pygame.mixer.Sound(os.path.join("jump.wav"))
hit_sound=pygame.mixer.Sound(os.path.join("hit.wav"))

# ---------- Pygame başlat ----------
pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird made by Best")
clock = pygame.time.Clock()
font = pygame.font.SysFont(FONT_NAME, 32)
# ---------- Oyun nesneleri ----------

class Bird:
    def __init__(self):
        self.x = 80
        self.y = HEIGHT // 2
        self.radius = 14
        self.vel = 0
        self.alive = True
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius*2, self.radius*2)

    def update(self):
        self.vel += GRAVITY
        self.y += self.vel
        self.rect.topleft = (self.x - self.radius, self.y - self.radius)
        # sınırlar
        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vel = 0
        if self.y + self.radius >= HEIGHT - 50:
            self.y = HEIGHT - 50 - self.radius
            if self.alive:
                hit_sound.play()
            self.alive = False

    def jump(self):
        if self.alive:
            self.vel = JUMP_STRENGTH
            jump_sound.play()

    def draw(self, surf):
        pygame.draw.circle(surf, BIRD_COLOR, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surf, (0,0,0), (int(self.x)+6, int(self.y)-4), 2)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = PIPE_WIDTH
        self.top_height = random.randint(80, HEIGHT - PIPE_GAP - 80)
        self.gap = PIPE_GAP
        self.passed = False
        self.rect_top = pygame.Rect(self.x, 0, self.width, self.top_height)
        self.rect_bottom = pygame.Rect(self.x, self.top_height + self.gap, self.width, HEIGHT - (self.top_height + self.gap) - 50)

    def update(self):
        self.x -= PIPE_SPEED
        self.rect_top.topleft = (self.x, 0)
        self.rect_bottom.topleft = (self.x, self.top_height + self.gap)

    def draw(self, surf):
        pygame.draw.rect(surf, PIPE_COLOR, (self.x, 0, self.width, self.top_height))
        pygame.draw.rect(surf, PIPE_COLOR, (self.x, self.top_height + self.gap, self.width, HEIGHT - (self.top_height + self.gap) - 50))
        pygame.draw.rect(surf, (0,100,0), (self.x+int(self.width*0.7), 0, int(self.width*0.3), self.top_height))
        pygame.draw.rect(surf, (0,100,0), (self.x+int(self.width*0.7), self.top_height + self.gap, int(self.width*0.3), HEIGHT - (self.top_height + self.gap) - 50))

    def off_screen(self):
        return self.x + self.width < 0

# ---------- Yardımcı fonksiyonlar ----------
def draw_score(surf, score,high_score):
    text = font.render(f"Skor: {score} Yüksek Skor: {high_score}", True,(0,0,0))
    surf.blit(text, (10,10))

def draw_ground(surf,ground_x):
    pygame.draw.rect(surf,GROUND_COLOR,(0,HEIGHT-50,WIDTH,50))
    for i in range(-1, WIDTH//60 +2):
        pygame.draw.rect(surf, (205,133,63), (i*60 + ground_x, HEIGHT-30, 40, 6))

def check_collision(bird, pipes):
    for p in pipes:
        if bird.rect.colliderect(p.rect_top) or bird.rect.colliderect(p.rect_bottom):
            hit_sound.play()
            return True
    if bird.y + bird.radius >= HEIGHT - 50:
        return True
    return False

# ---------- Oyun döngüsü ----------
def main():
    bird = Bird()
    pipes = []
    score = 0
    high_score=0
    ADDPIPE = pygame.USEREVENT + 1
    pygame.time.set_timer(ADDPIPE, PIPE_FREQUENCY)

    running = True
    paused = False
    start_screen = True  # Başlangıç ekranı aktif
    ground_x=0

    while running:
        dt = clock.tick(FPS)

        # ---- Başlangıç ekranı ----
        if start_screen:
            screen.fill(BG_COLOR)
            msg = font.render("Başlamak için bir tuşa basın", True, (0, 0, 0))
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    start_screen = False
            continue

        # ----Event kontrolü ----
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if bird.alive:
                        bird.jump()
                    elif event.key == pygame.K_p:
                        paused = not paused

                    else:
                        # sadece space ile restart
                        bird = Bird()
                        pipes.clear()
                        score = 0
                        PIPE_SPEED=3
                        pygame.time.set_timer(ADDPIPE, PIPE_FREQUENCY)
                elif event.key == pygame.K_UP:
                    if bird.alive:
                        bird.jump()
                elif event.key == pygame.K_p:
                    paused = not paused

            if event.type == ADDPIPE:
                pipes.append(Pipe(WIDTH + 10))

        # ---- Oyun güncelleme ----
        if not paused and bird.alive:
            bird.update()
            for p in pipes:
                p.update()
                if not p.passed and p.x + p.width < bird.x:
                    p.passed = True
                    score += 1
                    #Boru hızı artışı
                    if score %5 == 0:
                        PIPE_SPEED+=0.2
            pipes = [p for p in pipes if not p.off_screen()]
            if check_collision(bird, pipes):
                bird.alive = False
                if score > high_score:
                    high_score= score
                    #----Zemin hareketi----
        ground_x -=3
        if ground_x<= -60:
            ground_x=0

        # ---- Çizimler ----
        screen.fill(BG_COLOR)
        for p in pipes:
            p.draw(screen)
        draw_ground(screen,ground_x)
        bird.draw(screen)
        draw_score(screen, score,high_score)

        if not bird.alive:
            big_font = pygame.font.SysFont(FONT_NAME, 48)
            msg = big_font.render("Oyun Bitti", True, (200,30,30))
            sub = font.render("Space ile yeniden başla", True, (0,0,0))
            screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 40))
            screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 20))

        if paused:
            pa = font.render("PAUSED (P to resume)", True, (0,0,0))
            screen.blit(pa, (WIDTH//2 - pa.get_width()//2, HEIGHT//2 - 100))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
