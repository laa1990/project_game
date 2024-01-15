import os
import sys
from random import choice

import pygame

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
player_image = pygame.transform.scale(player_image, (800 // 2, 100 // 2))

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
wall_coords = []

enemy_im = [pygame.transform.scale(load_image("img_" + str(i) + ".png"), (tile_width, tile_height)) for i in range(7)]
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemy_group, all_sprites)

        self.image = enemy_im[0]
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
            self.image = enemy_im[self.cur_frame]
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
        self.cut_sheet(pygame.transform.scale(load_image(skins[self.color][1]), (600 // 2, 100 // 2)), 6, 1, self.walk_frames)
        self.jump_frames = []
        self.cut_sheet(pygame.transform.scale(load_image(skins[self.color][2]), (500 // 2, 100 // 2)), 5, 1,
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


grass_im = [load_image(str(i) + "_grass.png", (255, 255, 255)) for i in range(9)]
class Land(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y, pos):
        super().__init__(tiles_group, all_sprites)
        self.image = grass_im[pos]
        self.image = pygame.transform.scale(self.image, (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)



def generate_level(level):
    global START_COORDS
    for x in range(len(level)):
        for y in range(len(level[x])):
            if level[x][y] == "#":
                if x == 0 or x == len(level) - 1 or y == 0 or y == len(level[x]) - 1:
                    pos = 6
                elif level[x - 1][y] != "#":
                    if level[x][y - 1] != "#":
                        pos = 0
                    elif level[x][y + 1] != "#":
                        pos = 2
                    else:
                        pos = 1
                elif level[x + 1][y] != "#":
                    if level[x][y - 1] != "#":
                        pos = 5
                    elif level[x][y + 1] != "#":
                        pos = 4
                    else:
                        pos = 8
                else:
                    if level[x][y - 1] != "#":
                        pos = 6
                    elif level[x][y + 1] != "#":
                        pos = 3
                    else:
                        pos = 7
                Land(y, x, pos)
            elif level[x][y] == "@":
                START_COORDS = (y, x)
            elif level[x][y] == "E":
                Enemy(y, x)
    return y, x

WIDTH_GAME, HEIGHT_GAME = generate_level(load_level("level2.txt"))

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

        enemy_group.draw(screen)
        player_group.draw(screen)
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
        for enemy in enemy_group:
            enemy.update()
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        clock.tick(30)
        pygame.display.flip()
    pygame.quit()