import os
import sys

import pygame

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
tile_width = tile_height = 60


def load_image(name, colorkey=None):
    fullname = os.path.join('', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image

def load_level(filename):
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


player_image = load_image('Walking_KG_1.png')

all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
wall_coords = []

class Player(pygame.sprite.Sprite):
    right = False
    def __init__(self):
        super().__init__(player_group, all_sprites)
        self.frames = []
        self.cut_sheet(player_image, 7, 1)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.timer = 0

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.timer += 1
        if self.change_x != 0:
            if self.timer % 4 == 0:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames)
                self.image = self.frames[self.cur_frame]
                self.flip()
        else:
            self.cur_frame = 1
            self.image = self.frames[self.cur_frame]
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

player = None

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
            self.cur_frame = (self.cur_frame + 1) % 71
            t = "gif/" + str(self.timer // 2 % 71) + ".gif"
            self.image = load_image(t)
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.rect = self.image.get_rect().move(0, 0)

class Land(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = load_image("1.png")
        self.image = pygame.transform.scale(self.image, (tile_width, tile_height))
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


def generate_level(level):
    for x in range(len(level)):
        for y in range(len(level[x])):
            if level[x][y] == "#":
                Land(y, x)
    return y, x

x, y = generate_level(load_level("level2.txt"))

bg = Background()


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
    pygame.init()
    size = SCREEN_WIDTH, SCREEN_HEIGHT
    screen = pygame.display.set_mode(size)
    player = Player()
    player.rect.x = 340
    player.rect.y = 500
    running = True
    clock = pygame.time.Clock()
    camera = Camera()
    while running:
        screen.fill("black")
        all_sprites.draw(screen)
        tiles_group.draw(screen)
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
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > SCREEN_WIDTH:
            player.rect.right = SCREEN_WIDTH
        clock.tick(30)
        pygame.display.flip()
    pygame.quit()