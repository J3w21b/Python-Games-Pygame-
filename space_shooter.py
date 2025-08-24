import pygame
import random
import sys
import os

#----------------
#Ayarlar/Sabitler
#----------------
WIDTH,HEIGHT = 480,720
FPS=60

WHITE=(255,255,255)
BLACK=(0,0,0)
PLAYER_COLOR=(80,200,255)
ENEMY_COLOR=(255,80,80)
BULLET_COLOR=(255,255,100)
STAR_COLOR=(200,200,220)
EXPOLOSION_COLOR=(255,200,50)
UI_COLOR=(230,230,230)

PLAYER_SPEED=6
BULLET_SPEED=-10
ENEMY_MIN_SPEED=2
ENEMY_MAX_SPEED=5
ENEMY_SPAWN_MS=800
DIFFICULTY_EVERY=10

FONT_NAME=None
HIGHSCORE_FILE="highscore.txt"

#---------------------
#Yardımcı Fonksiyonlar
#---------------------
def load_highscore():
    try:
        if os.path.exists(HIGHSCORE_FILE):
            with open(HIGHSCORE_FILE,"r",encoding="utf-8") as f:
                return int(f.read().strip() or "0")
            
    except Exception:
        pass
    return 0

def save_highscore(score):
    try:
        with open(HIGHSCORE_FILE , "w",encoding="utf-8") as f:
            f.write(str(score))
    except Exception:
        pass

#---------
#Sınıflar
#----------
class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x= random.randint(0,WIDTH -1)
        self.y=random.randint(-HEIGHT,0)
        self.speed=random.randint(1,4)
        self.size=random.randint(1,2)

    def update(self):
        self.y+=self.speed
        if self.y> HEIGHT:
            self.x=random.randint(0,WIDTH-1)
            self.y=random.randint(-80,-10)
            self.speed=random.randint(1,4)
            self.size=random.randint(1,2)

    def draw(self,surf):
        pygame.draw.rect(surf,STAR_COLOR,(self.x,self.y,self.size,self.size))

class Player:
    def __init__(self):
        self.w=40
        self.h=30
        self.x=WIDTH//2 - self.w//2
        self.y=HEIGHT - self.h -30
        self.speed= PLAYER_SPEED
        self.lives=3
        self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
        self.cooldown=0

    def update(self,keys):
        dx = dy = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed

        self.x = max(0,min(WIDTH - self.w , self.x + dx))
        self.y = max(0, min(HEIGHT - self.h , self.y + dy))
        self.rect.topleft=(self.x,self.y)

        if self.cooldown > 0:
            self.cooldown -=1

    def can_shoot(self):
        return self.cooldown == 0
    
    def shoot(self,bullets):
        if self.can_shoot():
            bx = self.x + self.w // 2 -3 
            by = self.y - 10
            bullets.append(Bullet(bx,by))
            self.cooldown = 10

    def draw(self,surf):
        p1=(self.x + self.w //2,self.y)
        p2=(self.x, self.y + self.h)
        p3=(self.x + self.w,self.y + self.h)
        pygame.draw.polygon(surf,PLAYER_COLOR,(p1,p2,p3))
        pygame.draw.rect(surf,(60,170,240),(self.x + self.w//2-6,self.y + 6,12,self.h-10))

class Bullet:
    def __init__(self,x,y):
        self.w=6
        self.h=14
        self.x=x
        self.y=y
        self.rect=pygame.Rect(self.x,self.y,self.w,self.h)
        self.alive=True

    def update(self):
        self.y+=BULLET_SPEED
        self.rect.topleft=(self.x,self.y)
        if self.y<-self.h:
            self.alive=False

    def draw(self,surf):
        pygame.draw.rect(surf,BULLET_COLOR,self.rect)


class Enemy:
    def __init__(self,level=0):
        self.size=random.randint(28,40)
        self.x=random.randint(0,WIDTH - self.size)
        self.y=-self.size-random.randint(0,200)
        base_speed=random.uniform(ENEMY_MIN_SPEED,ENEMY_MAX_SPEED)
        self.speed=base_speed + level * 0.15
        self.rect=pygame.Rect(self.x,self.y,self.size,self.size)
        self.hp=1+(level//25)
        self.alive=True

    def update(self):
        self.y += self.speed
        self.rect.topleft =(self.x,self.y)
        if self.y > HEIGHT + 10:
            self.alive= False

    def draw(self,surf):
        pygame.draw.rect(surf,ENEMY_COLOR,self.rect,border_radius=6)
        eye = pygame.Rect(self.x + self.size//3,self.y+self.size//3,6,6)
        pygame.draw.rect(surf,BLACK,eye)


class Particle:
    """Basit patlama partikülü."""
    def __init__(self,x,y):
        self.x=x
        self.y=y
        self.vx=random.uniform(-3,3)
        self.vy=random.uniform(-3,3)
        self.life=random.randint(15,30)

    def update(self):
        self.x +=self.vx
        self.y += self.vy
        self.vy +=0.1
        self.life -=1 

    def draw(self,surf):
        if self.life >0:
            pygame.draw.circle(surf,EXPOLOSION_COLOR,(int(self.x),int(self.y)),max(1,self.life//6))

    @property
    def alive(self):
        return self.life > 0
    

#------------
#Ana Oyun
#------------
def main():
    pygame.init()
    screen=pygame.display.set_mode((WIDTH,HEIGHT))
    pygame.display.set_caption("Space Shooter made by Best")
    clock = pygame.time.Clock()
    font=pygame.font.SysFont(FONT_NAME,24)
    bigfont=pygame.font.SysFont(FONT_NAME,48)

    #Arka plan yıldızları
    stars=[Star() for _ in range(80)]

    #Oyuncu ve listeler
    player = Player()
    bullets = []
    enemies= []
    particles = []

    score = 0
    highscore = load_highscore()
    level = 0
    paused = False
    running = True
    game_over = False

    #Düşman doğurma olayı
    SPAWN = pygame.USEREVENT + 1
    spawn_ms = ENEMY_SPAWN_MS
    pygame.time.set_timer(SPAWN,spawn_ms)

    def reset_game():
        nonlocal player,bullets,enemies,particles,score,level,paused,game_over,spawn_ms
        player = Player()
        bullets = []
        enemies = []
        particles = []
        score = 0
        level = 0
        paused = False
        game_over = False
        spawn_ms=ENEMY_SPAWN_MS
        pygame.time.set_timer(SPAWN,spawn_ms)

    while running:
        dt = clock.tick(FPS)

        #-------------------OLAYLAR-----------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running=False
                break

            if event.type==pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running=False
                elif event.key ==pygame.K_p:
                    paused = not paused
                elif event.key == pygame.K_r and game_over:
                    reset_game()

            if event.type == SPAWN and not paused and not game_over:
                enemies.append(Enemy(level))

        keys = pygame.key.get_pressed()
        if not paused and not game_over:
            #Ateş et (Boşluk)
            if keys[pygame.K_SPACE]:
                player.shoot(bullets)

        #--------Güncelle-------
        if not paused and not game_over:
            player.update(keys)

            #Mermiler
            for b in bullets:
                b.update()
            bullets = [b for b in bullets if b.alive]

            #Düşmanlar
            for e in enemies:
                e.update()
            enemies=[e for e in enemies if e.alive]

            #Çarpışmalar:mermi -> düşman
            for e in enemies:
                for b in bullets:
                    if e.rect.colliderect(b.rect):
                        b.alive = False
                        e.hp -= 1
                        #Patlama partikülleri
                        for __ in range(8):
                            particles.append(Particle(e.rect.centerx,e.rect.centery))
                        if e.hp <=0:
                            e.alive = False
                            score +=1
                            level = score // DIFFICULTY_EVERY
                            #Zorluk: spawn aralığı kıs
                            new_ms=max(300,ENEMY_SPAWN_MS-level*60)
                            if new_ms !=spawn_ms:
                                spawn_ms=new_ms
                                pygame.time.set_timer(SPAWN,spawn_ms)

            #Çarpışmalar: düşman -> oyuncu
            for e in enemies:
                if e.rect.colliderect(player.rect):
                    e.alive = False
                    player.lives -=1
                    for __ in range(14):
                        particles.append(Particle(player.rect.centerx,player.rect.centery))
                    if player.lives <= 0:
                        game_over=True
                        highscore = max(highscore,score)
                        save_highscore(highscore)

            #Partiküller
            for p in particles:
                p.update()
            particles = [p for p in particles if p.alive]

            #Yıldızlar
            for s in stars:
                s.update()

        #----------Çiz-----------
        screen.fill(BLACK)
        for s in stars:
            s.draw(screen)

        for b in bullets:
            b.draw(screen)
        for e in enemies:
            e.draw(screen)
        for p in particles:
            p.draw(screen)

        player.draw(screen)

        #UI
        ui_text= f"Skor : {score} Can:{player.lives} En İyi:{highscore} Seviye:{level}"
        txt=font.render(ui_text,True,UI_COLOR)
        screen.blit(txt,(10,10))

        if paused and not game_over:
            t = bigfont.render("Duraklatıldı (P)",True,UI_COLOR)
            screen.blit(t,(WIDTH//2 - t.get_width()//2,HEIGHT//2-30))
        
        if game_over:
            t1=bigfont.render("Oyun Bitti",True,UI_COLOR)
            t2=font.render("R ile yeniden başla | ESC çıkış",True,UI_COLOR)
            screen.blit(t1,(WIDTH//2 - t1.get_width()//2,HEIGHT//2-60))
            screen.blit(t2,(WIDTH//2 -t2.get_width()//2,HEIGHT//2))

        pygame.display.flip()

    pygame.quit()

#Çalıştır
if __name__ == "__main__":
    main()
