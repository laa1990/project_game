import pygame
import os
import sys

level_name = os.path.join('data', input())
if not os.path.isfile(level_name):
    print(f"Файл с изображением '{level_name}' не найден")
else:
    def load_image(name, colorkey=None):
        fullname = os.path.join('data', name)
        if not os.path.isfile(fullname):
            print(f"Файл с изображением '{fullname}' не найден")
            sys.exit()
        image = pygame.image.load(fullname)
        return image


    def terminate():
        pygame.quit()
        sys.exit()


    def start_screen():
        intro_text = ["ЗАСТАВКА", "",
                      "Правила игры",
                      "Движение осуществляется на стрелочки,"]

        fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 30)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN or \
                        event.type == pygame.MOUSEBUTTONDOWN:
                    screen.fill((0, 255, 255))
                    return  # начинаем игру
            pygame.display.flip()


    def load_level(filename):
        # читаем уровень, убирая символы перевода строки
        with open(filename, 'r') as mapFile:
            level_map = [line.strip() for line in mapFile]

        # и подсчитываем максимальную длину
        max_width = max(map(len, level_map))

        # дополняем каждую строку пустыми клетками ('.')
        return list(map(lambda x: x.ljust(max_width, '.'), level_map))


    tile_images = {
        'wall': load_image('box.png'),
        'empty': load_image('grass.png')
    }
    player_image = load_image('mar.png')

    tile_width = tile_height = 50

    # основной персонаж
    player = None

    # группы спрайтов
    all_sprites = pygame.sprite.Group()
    tiles_group = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    #для отслежования столкнвения
    wall_coords = []


    def generate_level(level):
        new_player, x, y = None, None, None
        for y in range(len(level)):
            for x in range(len(level[y])):
                if level[y][x] == '.':
                    Tile('empty', x, y)
                elif level[y][x] == '#':
                    Tile('wall', x, y)
                elif level[y][x] == '@':
                    Tile('empty', x, y)
                    new_player = Player(x, y)
        # вернем игрока, а также размер поля в клетках
        return new_player, x, y


    class Tile(pygame.sprite.Sprite):
        def __init__(self, tile_type, pos_x, pos_y):
            super().__init__(tiles_group, all_sprites)
            self.image = tile_images[tile_type]
            if tile_type == 'wall':
                self.mask = pygame.mask.from_surface(self.image)
                wall_coords.append(self)
            self.rect = self.image.get_rect().move(
                tile_width * pos_x, tile_height * pos_y)


    class Player(pygame.sprite.Sprite):
        def __init__(self, x, y):
            super().__init__(player_group)
            self.image = player_image
            self.rect = self.image.get_rect().move(
                tile_width * x, tile_height * y)
            self.mask = pygame.mask.from_surface(self.image)
            self.directing = 0
            self.jumpCount = 10

        def walking(self, motion):
            walls = 0
            for i in wall_coords:
                if pygame.sprite.collide_mask(self, i):
                    print(123)
                    walls += 1
                    if motion == -4:
                        self.y = 4
                    elif motion == 4:
                        self.y = -4

            if not walls or motion == -self.directing:
                self.rect.x += motion
                self.directing = 0

        def direction(self, directing):
            self.directing = directing

        def jump(self, motion):
            pass

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
        def update(self, motion):
            if motion:
                if abs(motion) == 1:
                    self.dx = motion
                    self.dy = 0


    if __name__ == '__main__':
        pygame.init()
        size = width, height = 500, 500
        screen = pygame.display.set_mode(size)
        start_screen()
        level1 = load_level(level_name)
        player, level_x, level_y = generate_level(level1)
        camera = Camera()
        running = True
        all_sprites.draw(screen)
        tiles_group.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock = pygame.time.Clock()
        motion = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        motion = 4
                        camera.update(1)
                    if event.key == pygame.K_LEFT:
                        motion = -4
                        camera.update(1)
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_RIGHT and motion == 4:
                        motion = 0
                        camera.update(0)
                    if event.key == pygame.K_LEFT and motion == -4:
                        motion = 0
                        camera.update(0)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        pass
            if motion:
                player.walking(motion)
                player.direction(motion)
                screen.fill((0, 0, 0))
                all_sprites.draw(screen)
                player_group.draw(screen)
                pygame.display.flip()
            clock.tick(60)
        pygame.quit()
