import pygame
import random 

pygame.init()

#Renkler
beyaz = (255 , 255 , 255)
siyah =(0 , 0 , 0)
kirmizi = (255 , 0 , 0)
yesil = (0 , 255 , 0)

#Ekran Boyutu
genislik= 600
yukseklik = 400
pencere = pygame.display.set_mode((genislik , yukseklik))
pygame.display.set_caption("Yılan Oyunu made by nZ")

saat= pygame.time.Clock()
kutu_boyutu=20
hiz=10

font=pygame.font.SysFont("Arial",24)

def skor_yazdir(skor):
    metin = font.render("Skor: " + str(skor),True,siyah)
    pencere.blit(metin ,[10,10])

def oyun():
    oyun_bitti=False
    oyun_durdu=False

    x = genislik // 2
    y = yukseklik // 2

    x_deg=0
    y_deg=0

    yilan = []
    uzunluk = 1

    yem_x = round(random.randrange(0,genislik - kutu_boyutu) / 20.0)*20.0
    yem_y = round(random.randrange(0,yukseklik - kutu_boyutu) / 20.0)*20.0

    while not oyun_bitti:
        for etkinlik in pygame.event.get():
            if etkinlik.type == pygame.QUIT:
                oyun_bitti = True
            if etkinlik.type == pygame.KEYDOWN:
                if etkinlik.key == pygame.K_LEFT and x_deg == 0:
                    x_deg = -kutu_boyutu
                    y_deg = 0
                elif etkinlik.key == pygame.K_RIGHT and x_deg == 0:
                    x_deg= kutu_boyutu
                    y_deg = 0
                elif etkinlik.key == pygame.K_UP and y_deg == 0:
                    x_deg = 0
                    y_deg = -kutu_boyutu
                elif etkinlik.key == pygame.K_DOWN and y_deg == 0:
                    x_deg= 0
                    y_deg= kutu_boyutu
        
        if x>= genislik or x < 0 or y>= yukseklik or y <0:
            oyun_durdu = True

        x += x_deg
        y +=y_deg

        pencere.fill(beyaz)
        pygame.draw.rect(pencere,yesil, [yem_x, yem_y,kutu_boyutu,kutu_boyutu])

        yilan_kafasi=[]
        yilan_kafasi.append(x)
        yilan_kafasi.append(y)
        yilan.append(yilan_kafasi)

        if len(yilan) > uzunluk:
            del yilan [0]

        for parca in yilan [:-1]:
            if parca == yilan_kafasi:
                oyun_durdu=True

        for parca in yilan:
            pygame.draw.rect(pencere,siyah,[parca[0],parca[1],kutu_boyutu,kutu_boyutu])

        skor_yazdir(uzunluk -1)
        pygame.display.update()

        if x == yem_x and y == yem_y:
            yem_x = round (random.randrange(0,genislik - kutu_boyutu) / 20.0)*20.0
            yem_y = round (random.randrange(0,yukseklik - kutu_boyutu) / 20.0)* 20.0
            uzunluk +=1

        if oyun_durdu:
            break

        saat.tick(hiz)

    pygame.quit()

oyun()

