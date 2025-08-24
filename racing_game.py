import pygame
import random
import sys

#start to pygame
pygame.init()

#screen size
WIDTH = 400
HEIGHT =600
screen=pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Araba Yarışı made by J3w21")

#colors
WHITE = (255,255,255)
BLACK=(0,0,0)
RED=(200,0,0)

#clock
clock =pygame.time.Clock()

#car
car_width= 50
car_height=90
car_x = WIDTH // 2 -car_width // 2
car_y = HEIGHT -car_height - 20
car_speed=5

#enemy car
enemy_height=90
enemy_widht=50
enemy_x=random.randint(0, WIDTH -enemy_widht)
enemy_y=-enemy_height
enemy_speed=5

#score
score=0
font =pygame.font.SysFont(None,35)

def draw_text(text,size,color,x,y):
    font=pygame.font.SysFont(None,size)
    label=font.render(text,True,color)
    screen.blit(label, (x,y))

#oyun döngüsü
running = True
while running:
    screen.fill(WHITE)

    #events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    #tuş kombinasyonları
    keys=pygame.key.get_pressed()
    if keys[pygame.K_LEFT]and car_x>0:
        car_x -= car_speed
    if keys[pygame.K_RIGHT] and car_x < WIDTH - car_width:
        car_x += car_speed

    
    #düşman hareketi
    enemy_y += enemy_speed
    if enemy_y > HEIGHT:
        enemy_y = -enemy_height
        enemy_x = random.randint(0 , WIDTH- enemy_widht)
        score += 1
        enemy_speed += 0.2 #zamanla hızlanır

    #araba çiz
    pygame.draw.rect(screen,BLACK, (car_x, car_y, car_height , car_width))
    #düşman arabasını çiz
    pygame.draw.rect(screen,RED,(enemy_x,enemy_y,enemy_widht,enemy_height))

    #çarpışma kontrolü
    if (car_x < enemy_x + enemy_widht and
        car_x + car_width > enemy_x and 
        car_y < enemy_y + enemy_height and
        car_y + car_height > enemy_y):
        draw_text("Oyun Bitti!", 50,RED,WIDTH // 4, HEIGHT // 3)
        pygame.display.flip()
        pygame.time.wait(2000)
        pygame.quit()
        sys.exit()

    #skore yaz
    draw_text(f"Skor: {score}", 35,BLACK ,10,10)
    
    #ekranı güncelle
    pygame.display.flip()
    clock.tick(60)

