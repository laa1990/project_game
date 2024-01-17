import math
import os
import sys
from random import choice

import pygame
from pygame import Rect

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
tile_width = tile_height = 50
pygame.init()
size = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(size)


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image

def load_level(filename):
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    level_map = ["#" * max_width] * 10 + list(map(lambda x: x.ljust(max_width, '.'), level_map)) + ["#" * max_width] * 10
    level_map = list(map(lambda x: "#####" * 5 + x + "#####" * 5, level_map))
    return level_map



skins = {
    "orange": ['forward_idle.png', "walk_right.png", "roll.png"]
}

player_image = load_image('forward_idle.png')
player_image = pygame.transform.scale(player_image, (8 * 50, 50))

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
ball_group = pygame.sprite.Group()
notchanged_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
wall_coords = []

enemy_im = [pygame.transform.scale(load_image("img_" + str(i) + ".png"), (tile_width, tile_height)) for i in range(7)]
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemy_group, all_sprites)

        self.image = pygame.transform.scale(enemy_im[0], (50, 50))
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.timer = 0
        self.rect.x = tile_width * x
        self.rect.y = tile_height * y
        self.cur_frame = 0


    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:
            self.cur_frame = (self.cur_frame + 1) % 7
            self.image = pygame.transform.scale(enemy_im[self.cur_frame], (50, 50))
        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            self.change_y = 0
        if self.timer % 50 == 0:
            if ((player.rect.x + 25 - self.rect.x - 20) ** 2 + (player.rect.y + 25 - self.rect.y) ** 2) ** 0.5 < 500:
                Bullet(self.rect.x - 20, self.rect.y)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullet_group, all_sprites)
        if player.rect.x + 25 == x:
            if player.rect.y + 25 > y:
                angle = 90
            else:
                angle = 270
        else:
            angle = abs(math.degrees(math.atan((player.rect.y + 25 - y) / (player.rect.x - x))))
            if player.rect.y + 25 > y:
                if player.rect.x + 25 > x:
                    angle = -angle
                else:
                    angle = angle - 180
            else:
                if player.rect.x + 25 > x:
                    angle = angle
                else:
                    angle = 180 - angle
        self.image = pygame.transform.rotate(pygame.transform.scale(load_image("bull.png", -1), (30, 20)), angle)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.x = player.rect.x + 25 - x
        self.y = player.rect.y + 25 - y
        self.timer = 0
        self.distance = (self.x ** 2 + self.y ** 2) ** 0.5

    def update(self):
        self.timer += 1
        if self.timer % 2 == 0:
            self.rect.y += self.y // (self.distance / 7)
            self.rect.x += self.x // (self.distance / 7)



class Player(pygame.sprite.Sprite):
    right = False
    def __init__(self, x, y):
        super().__init__(player_group, all_sprites)
        self.color = "orange"
        self.stop_frames = []
        self.cut_sheet(player_image, 8, 1, self.stop_frames)
        self.cur_frame = 0
        self.image = self.stop_frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.timer = 0
        self.walk_frames = []
        self.cut_sheet(pygame.transform.scale(load_image(skins[self.color][1]), (6 * 50, 50)), 6, 1, self.walk_frames)
        self.jump_frames = []
        self.cut_sheet(pygame.transform.scale(load_image(skins[self.color][2]), (5 * 50, 50)), 5, 1,
                       self.jump_frames)
        self.rect.x = tile_width * x
        self.rect.y = tile_height * y


    def cut_sheet(self, sheet, columns, rows, mass):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                mass.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.timer += 1
        if self.change_y != 0:
            if self.timer % 5 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.jump_frames)
                self.image = self.jump_frames[self.cur_frame]
                self.flip()
        elif self.change_x == 0:
            if self.timer % 5 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.stop_frames)
                self.image = self.stop_frames[self.cur_frame]
                self.flip()
        else:
            if self.timer % 5 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.walk_frames)
                self.image = self.walk_frames[self.cur_frame]
                self.flip()
        self.gravitation()
        self.rect.x += self.change_x
        block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        for block in block_hit_list:
            if self.change_x > 0:
                self.rect.right = block.rect.left
            elif self.change_x < 0:
                self.rect.left = block.rect.right
        self.rect.y += self.change_y
        block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        for block in block_hit_list:
            if self.change_y > 0:
                self.rect.bottom = block.rect.top
            elif self.change_y < 0:
                self.rect.top = block.rect.bottom
            self.change_y = 0
        ball_hit_list = pygame.sprite.spritecollide(player, ball_group, True)
        if ball_hit_list:
            global COLLECTED_BALLS
            COLLECTED_BALLS += 1
            running = False


    def gravitation(self):
        if self.change_y == 0:
            self.change_y = 1
        else:
            self.change_y += .95
        if self.rect.y >= SCREEN_HEIGHT - self.rect.height and self.change_y >= 0:
            self.change_y = 0
            self.rect.y = SCREEN_HEIGHT - self.rect.height

    def jump(self):

        self.rect.y += 10
        platform_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
        self.rect.y -= 10
        if len(platform_hit_list) > 0 or self.rect.bottom >= SCREEN_HEIGHT:
            self.change_y = -16

    def go_left(self):
        self.change_x = -9
        if (self.right):
            self.right = False

    def go_right(self):
        self.change_x = 9
        if (not self.right):
            self.right = True

    def stop(self):
        self.change_x = 0

    def flip(self):
        if not self.right:
            self.image = pygame.transform.flip(self.image, True, False)

    def change_skin(self, color):
        pass


class Ball_OF_Thread(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(ball_group, all_sprites)
        self.image = pygame.transform.scale(load_image("ball.png", -1), (30, 25))
        self.rect = self.image.get_rect()
        self.change_y = 1
        self.start_pos = 0
        self.timer = 0
        self.rect.x = tile_width * x + 10
        self.rect.y = tile_height * y + 12

    def update(self):
        self.timer += 1
        if self.timer % 5 == 0:
            if -5 < self.start_pos < 5:
                self.rect.y += self.change_y
                self.start_pos += self.change_y
            else:
                self.change_y *= -1
                self.rect.y += self.change_y
                self.start_pos += self.change_y

class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.image = load_image("gif/0.gif")
        self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.rect = self.image.get_rect().move(-500, -500)
        self.change_x = self.change_y = 0
        self.timer = 0
        self.cur_frame = 0
    def update(self):
        self.timer += 1
        if self.timer % 1 == 0:
            self.cur_frame = (self.cur_frame + 1) % 5
            t = "gif/" + str(self.timer // 2 % 5) + ".gif"
            self.image = load_image(t)
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.image.get_rect().move(0, 0)





grass_im = [load_image(str(i) + "_grass.png", (255, 255, 255)) for i in range(15)]
class Land(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pos):
        super().__init__(tiles_group, all_sprites)
        self.image = grass_im[pos]
        self.image = pygame.transform.scale(self.image, (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)

    def update(self):
        ball_hit_list = pygame.sprite.spritecollide(self, bullet_group, True)
        if ball_hit_list:
            running = False

class Stat_balls(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(notchanged_group)
        self.image = pygame.transform.scale(load_image("stat_ball.png"), (120, 20))
        self.rect = self.image.get_rect().move(50, 30)

    def update(self):
        screen.fill(pygame.Color(100, 125, 52), pygame.Rect(65, 35, 95 // COL_BALLS * COLLECTED_BALLS, 10))
def generate_level(level):
    global START_COORDS
    global COL_BALLS
    for x in range(len(level)):
        for y in range(len(level[x])):
            if level[x][y] == "#":
                if x == 0 or x == len(level) - 1 or y == 0 or y == len(level[x]) - 1:
                    pos = 6
                else:
                    t1 = (level[x - 1][y - 1] != "#")
                    t2 = (level[x][y - 1] != "#")
                    t3 = (level[x + 1][y - 1] != "#")
                    t4 = (level[x + 1][y] != "#")
                    t5 = (level[x + 1][y + 1] != "#")
                    t6 = (level[x][y + 1] != "#")
                    t7 = (level[x - 1][y + 1] != "#")
                    t8 = (level[x - 1][y] != "#")
                    if t2 and t4 and t6 and t8:
                        pos = 9
                    elif t2 and t8 and t6:
                        pos = 10
                    elif t8 and t4 and t6:
                        pos = 11
                    elif t4 and t2 and t8:
                        pos = 12
                    elif t4 and t2 and t6:
                        pos = 13
                    elif t6 and t4:
                        pos = 4
                    elif t2 and t4:
                        pos = 5
                    elif t8 and t6:
                        pos = 2
                    elif t8 and t2:
                        pos = 0
                    elif t8 and t4:
                        pos = 1
                    elif t6 and t2:
                        pos = 14
                    elif t6:
                        pos = 3
                    elif t2:
                        pos = 6
                    elif t8:
                        pos = 1
                    elif t4:
                        pos = 8
                    else:
                        pos = 7

                Land(y, x, pos)
            elif level[x][y] == "@":
                START_COORDS = (y, x)
            elif level[x][y] == "E":
                Enemy(y, x)
            elif level[x][y] == "b":
                COL_BALLS += 1
                Ball_OF_Thread(y, x)
    return y, x
COL_BALLS = 0
COLLECTED_BALLS = 0
WIDTH_GAME, HEIGHT_GAME = generate_level(load_level("level2.txt"))
statsBall = Stat_balls()
bg = Background()

player = Player(*START_COORDS)



class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - SCREEN_WIDTH // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - SCREEN_HEIGHT // 2)





if __name__ == '__main__':
    running = True
    clock = pygame.time.Clock()
    camera = Camera()
    while running:
        screen.fill("black")
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        ball_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        statsBall.update()
        notchanged_group.draw(screen)
        bullet_group.draw(screen)
        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.go_left()
                if event.key == pygame.K_RIGHT:
                    player.go_right()
                if event.key == pygame.K_UP:
                    player.jump()

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT and player.change_x < 0:
                    player.stop()
                if event.key == pygame.K_RIGHT and player.change_x > 0:
                    player.stop()
        player.update()
        bg.update()
        for bullet in bullet_group:
            bullet.update()
        for land in tiles_group:
            land.update()
        for enemy in enemy_group:
            enemy.update()
        for ball in ball_group:
            ball.update()
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        clock.tick(30)
        pygame.display.flip()
    pygame.quit()