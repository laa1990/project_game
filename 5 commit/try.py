import math
import os
import sys
from random import choice, randint

import pygame
from pygame import Rect

SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
tile_width = tile_height = 50
pygame.init()
size = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode(size)
pygame.mixer.music.load('music.mp3')

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



def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    fon = pygame.transform.scale(load_image('fon.png'), (SCREEN_WIDTH, SCREEN_HEIGHT))
    play = pygame.transform.scale(load_image('play.jpg', -1), (30, 41))
    screen.blit(fon, (0, 0))
    screen.blit(play, (340, 280))
    button = 0
    start = True
    spisok = [(340, 280), (330, 325), (380, 369)]
    enter = False
    coming_soon = False
    sound1 = pygame.mixer.Sound('enter.mp3')
    sound2 = pygame.mixer.Sound('click.mp3')
    sound1.set_volume(0.5)
    sound2.set_volume(0.5)
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN and not coming_soon:
                if event.key == pygame.K_DOWN:
                    sound1.play()
                    screen.blit(fon, (0, 0))
                    button = (button + 1) % 3
                    screen.blit(play, spisok[button])
                if event.key == pygame.K_UP:
                    sound1.play()
                    screen.blit(fon, (0, 0))
                    button = (button - 1) % 3
                    screen.blit(play, spisok[button])
                if event.key == pygame.K_RETURN:
                    sound2.play()
                    enter = True
            if event.type == pygame.KEYDOWN and coming_soon:
                screen.blit(fon, (0, 0))
                screen.blit(play, spisok[button])
                coming_soon = False
            pygame.display.flip()
        if enter:
            if button == 0:
                pygame.mixer.music.set_volume(0.07)
                pygame.mixer.music.play(-1)
                screen.fill((0, 255, 255))
                return
            if button == 2:
                terminate()
            if button == 1:
                button = 0
                enter = False
                coming_soon = True
                screen.blit(pygame.transform.scale(load_image('soon.png'), (SCREEN_WIDTH, SCREEN_HEIGHT)), (0, 0))



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
    "orange": ['forward_idle.png', "walk_right.png", "roll.png", "damage.png"]
}

player_image = load_image('forward_idle.png')
player_image = pygame.transform.scale(player_image, (8 * 50, 50))


enemy_im = [pygame.transform.scale(load_image("img_" + str(i) + ".png"), (tile_width, tile_height)) for i in range(8)]
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(enemy_group, all_sprites)
        self.image = pygame.transform.scale(enemy_im[0], (50, 50))
        self.rect = self.image.get_rect()
        self.change_x = 0
        self.change_y = 0
        self.timer = 0
        self.countdown = 0
        self.rect.x = tile_width * x
        self.rect.y = tile_height * y + 1
        self.cur_frame = 0
        self.direction = ''
        self.right = True

    def update(self, direction):
        self.timer += 1
        if direction:
            if self.timer % 5 == 0:
                self.cur_frame = (self.cur_frame + 1) % 7
                self.image = enemy_im[self.cur_frame]
                self.flip()
            if direction == 1:
                self.rect.x -= 50
            elif direction == 2:
                self.rect.x += 50
            block_hit_list = pygame.sprite.spritecollide(self, tiles_group, False)
            if not block_hit_list:
                self.stop()
            else:
                self.rect.x += self.change_x
                self.rect.y += self.change_y
            if direction == 1:
                self.rect.x += 50
            elif direction == 2:
                self.rect.x -= 50

        if self.timer % 50 == 0:
            if ((player.rect.x - self.rect.x) ** 2 + (player.rect.y - self.rect.y) ** 2) ** 0.5 < 500:
                Bullet(self.rect.x, self.rect.y)

    def go_left(self):
        self.change_x = -3
        self.right = False

    def go_right(self):
        self.change_x = 3
        self.right = True

    def stop(self):
        self.change_x = 0
        self.image = enemy_im[7]

    def flip(self):
        if not self.right:
            self.image = pygame.transform.flip(self.image, True, False)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(bullet_group, all_sprites)
        if player.rect.x + 25 == x:
            if player.rect.y + 25 > y:
                angle = 90
            else:
                angle = 270
        else:
            angle = abs(math.degrees(math.atan((player.rect.y + 25 - y) / (player.rect.x + 25 - x))))
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
        self.damage_frames = []
        self.cut_sheet(pygame.transform.scale(load_image(skins[self.color][3]), (6 * 50, 50)), 6, 1,
                       self.damage_frames)
        self.rect.x = tile_width * x
        self.rect.y = tile_height * y
        self.injure = False


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
        if self.injure:
            if self.timer % 4 == 0:
                if self.cur_frame == 5:
                    self.injure = False
                else:
                    self.cur_frame += 1
                    self.image = self.damage_frames[self.cur_frame]
                    self.flip()

        elif self.change_y != 0:
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
        bullet_hit_list = pygame.sprite.spritecollide(player, bullet_group, True)
        if bullet_hit_list:
            global HP_STATS
            HP_STATS -= 1
            self.injured()
            running = False
        if pygame.sprite.spritecollideany(self, portal_group):
            pass


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

    def injured(self):
        self.injure = True
        self.cur_frame = 0
        self.change_y -= 15
        if self.right:
            self.change_x -= 7
        else:
            self.change_x += 7



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
        self.rect = self.image.get_rect().move(20, 30)

    def update(self):
        screen.fill(pygame.Color(100, 125, 52), pygame.Rect(30, 35, 95 // COL_BALLS * COLLECTED_BALLS, 10))
        screen.blit(pygame.transform.scale(load_image("ball.png", -1), (40, 30)), (145, 25))
        font = pygame.font.Font("font.ttf", 25)
        text = font.render(str(COLLECTED_BALLS) + " / " + str(COL_BALLS), True, (255, 255, 255))
        screen.blit(text, (200, 25))

class Stat_hp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(notchanged_group)
        self.image = pygame.transform.scale(load_image("stat_ball.png"), (120, 20))
        self.rect = self.image.get_rect().move(20, 80)

    def update(self):
        screen.fill(pygame.Color(255, 177, 76), pygame.Rect(30, 85, 95 // 5 * HP_STATS, 10))
        font = pygame.font.Font("font.ttf", 25)
        text = font.render(str(HP_STATS) + " / " + str(5), True, (255, 255, 255))
        screen.blit(text, (200, 75))


class Portal(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__(all_sprites, portal_group)
        self.frames = []
        self.cut_sheet(pygame.transform.scale(load_image("portal.png"), (4 * 100, 5 * 100)), 4, 5,
                       self.frames)
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = tile_width * x
        self.rect.y = tile_height * y

        self.cur_frame = 0
        self.timer = 0


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
        if self.timer % 2 == 0:
            self.cur_frame = (self.cur_frame + 1) % 20
            self.image = self.frames[self.cur_frame]


def generate_level(level):
    global COL_BALLS
    global player
    global W_G, H_G
    W_G = len(level)
    H_G = len(level[0])
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
                player = Player(y, x)
            elif level[x][y] == "E":
                Enemy(y, x)
            elif level[x][y] == "b":
                COL_BALLS += 1
                Ball_OF_Thread(y, x)
            elif level[x][y] == "p":
                    Portal(y, x)


def del_level():
    global COL_BALLS, HP_STATS, COLLECTED_BALLS, player
    all_sprites.empty()
    tiles_group.empty()
    player_group.empty()
    enemy_group.empty()
    ball_group.empty()
    notchanged_group.empty()
    bullet_group.empty()
    portal_group.empty()
    COL_BALLS = 1
    COLLECTED_BALLS = 0
    HP_STATS = 5
    player = None


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
    start_screen()
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    ball_group = pygame.sprite.Group()
    notchanged_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    portal_group = pygame.sprite.Group()
    COL_BALLS = 1
    COLLECTED_BALLS = 0
    HP_STATS = 5
    player = None
    generate_level(load_level("level2.txt"))
    CURRENT_LEVEL = 1
    END_OF_THE_GAME = False
    statsBall = Stat_balls()
    statHp = Stat_hp()
    bg = Background()
    paused = True
    gotomenu = False
    enemy_direction = 0
    while running:
        screen.fill("black")
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        ball_group.draw(screen)
        enemy_group.draw(screen)
        player_group.draw(screen)
        portal_group.draw(screen)
        statsBall.update()
        statHp.update()
        notchanged_group.draw(screen)
        bullet_group.draw(screen)
        camera.update(player)
        if paused:
            if gotomenu:
                start_screen()
                del_level()
                generate_level(load_level("level1.txt"))
                gotomenu = not gotomenu
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == 32:
                    paused = not paused
                if event.key == 113:
                    gotomenu = True
                if not paused:
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
        bg.update()
        if not paused:
            player.update()
            for enemy in enemy_group:
                if enemy.countdown == 0:
                    enemy.chosee = choice([True, False])
                    enemy.countdown = randint(20, 60)
                    enemy.stop()
                    enemy_direction = 0
                    if enemy.chosee:
                        enemy.direction = choice(['left', 'right'])
                        if enemy.direction == 'left':
                            enemy.go_left()
                            enemy_direction = 1
                        else:
                            enemy.go_right()
                            enemy_direction = 2
                else:
                    enemy.countdown -= 1
                enemy.update(enemy_direction)
            for bullet in bullet_group:
                bullet.update()
            for land in tiles_group:
                land.update()
            for p in portal_group:
                portal_group.update()
            for ball in ball_group:
                ball.update()
            if player.rect.left < 0:
                player.rect.left = 0
            if player.rect.right > SCREEN_WIDTH:
                player.rect.right = SCREEN_WIDTH
        clock.tick(30)
        pygame.display.flip()
    pygame.quit()