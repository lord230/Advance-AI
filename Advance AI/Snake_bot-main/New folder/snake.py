import pygame as pg
from random import randrange

pg.init()
pg.font.init()

WINDOW = 1000
Title = 50
Range = (Title // 2, WINDOW - Title // 2, Title)
get_rand = lambda: [randrange(*Range),randrange(*Range)]


snake = pg.rect.Rect([0,0,Title - 2, Title - 2])
snake.center = get_rand()
length = 1
food = snake.copy()
food.center = get_rand()

time , time_step = 0,110

segments =  [snake.copy()]
screen = pg.display.set_mode([WINDOW]*2)
clock = pg.time.Clock()
dirs = {pg.K_w:1 , pg.K_s: 1, pg.K_a:1, pg.K_d:1}
score = 0
snake_dir = (0,0)



while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            exit()
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_w and dirs[pg.K_w]:
                snake_dir = (0, -Title)
                dirs = {pg.K_w:1 , pg.K_s: 0, pg.K_a:1, pg.K_d:1}
            if event.key == pg.K_s and dirs[pg.K_s]:
                snake_dir = (0, Title)
                dirs = {pg.K_w:0 , pg.K_s: 1, pg.K_a:1, pg.K_d:1}
            if event.key == pg.K_a and dirs[pg.K_a]:
                snake_dir = (-Title, 0)
                dirs = {pg.K_w:1 , pg.K_s: 1, pg.K_a:1, pg.K_d:0}
            if event.key == pg.K_d and dirs[pg.K_d]:
                snake_dir = (Title,0)
                dirs = {pg.K_w:1 , pg.K_s: 1, pg.K_a:0, pg.K_d:1}

    screen.fill('red')

    font = pg.font.SysFont("Arial",32)
    txt = font.render(f"Score : {score}",True,"white")
    screen.blit(txt,(10,10))


    # food
    [pg.draw.rect(screen,'blue',food)]
    # snake
    pg.draw.rect(screen, 'blue', food)
    for segment in segments:
       pg.draw.rect(screen, 'white', segment)

    # conditions for length and food
    if snake.center == food.center:
        food.center = get_rand()
        print(segments,"\n")
        length += 1
        score += 1

      # collision
    self_eat = pg.Rect.collidelist(snake,segments[:-1]) != -1

    # conditions for border and slef eat restart 
    if snake.left < 0 or snake.right > WINDOW or snake.top < 0 or snake.bottom >WINDOW or self_eat:
        snake.center, food.center = get_rand(),get_rand()
        length, snake_dir = 1 , (0,0)
        segments = [snake.copy()]
        score = 0
    
  


    time_now = pg.time.get_ticks()
    if time_now - time > time_step:
        time = time_now
        snake.move_ip(snake_dir)
        segments.append(snake.copy())
        segments = segments[-length:]
   
    pg.display.flip()
    clock.tick(60)
