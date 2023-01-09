import pygame
import os
import csv
import random

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('PJF Project Maciej Sołtys WCY20IJ1S1')

clock = pygame.time.Clock()
FPS = 60

ROWS = 16
COLS = 80
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 25

GRAVITY = 0.75 * 800 / SCREEN_WIDTH
SCROLL_THRESH = 300

screen_scroll = 0
bg_scroll = 0

moving_left = False
moving_right = False
shoot = False
level = 1
start_game = False
start_intro = False

pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountains_img = pygame.image.load('img/Background/mountains_bg.png').convert_alpha()
mountains_img = pygame.transform.scale(mountains_img, (600, 400))
sky_img = pygame.image.load('img/Background/sky.png').convert_alpha()
sky_img = pygame.transform.scale(sky_img, (900, 500))
width = sky_img.get_width()
start_unpointed_img = pygame.image.load('img/buttons/start_unpointed.png').convert_alpha()
exit_unpointed_img = pygame.image.load('img/buttons/exit_unpointed.png').convert_alpha()
restart_unpointed_img = pygame.image.load('img/buttons/restart_unpointed.png').convert_alpha()
start_pointed_img = pygame.image.load('img/buttons/start_pointed.png').convert_alpha()
exit_pointed_img = pygame.image.load('img/buttons/exit_pointed.png').convert_alpha()
restart_pointed_img = pygame.image.load('img/buttons/restart_pointed.png').convert_alpha()
author_sign_png = pygame.image.load('img/author_sign.png').convert_alpha()
game_over_png = pygame.image.load('img/game_over_sign.png').convert_alpha()
arrow_img = pygame.image.load('img/icons/arrow.png').convert_alpha()

jump_fx = pygame.mixer.Sound('sounds/jump.wav')
jump_fx.set_volume(0.5)
hit_fx = pygame.mixer.Sound('sounds/hit.wav')
hit_fx.set_volume(0.5)
enemy_hit_fx = pygame.mixer.Sound('sounds/enemy_hit.wav')
enemy_hit_fx.set_volume(0.5)
enemy_kill_fx = pygame.mixer.Sound('sounds/enemy_kill.wav')
enemy_kill_fx.set_volume(0.5)
shoot_fx = pygame.mixer.Sound('sounds/shoot.wav')
shoot_fx.set_volume(0.5)
step_fx = pygame.mixer.Sound('sounds/step.wav')
step_fx.set_volume(0.5)
button_point_fx = pygame.mixer.Sound('sounds/button_point.wav')
button_point_fx.set_volume(0.5)
button_click_fx = pygame.mixer.Sound('sounds/button_click.wav')
button_click_fx.set_volume(0.5)
arrow_wall_hit_fx = pygame.mixer.Sound('sounds/arrow_wallhit.wav')
arrow_wall_hit_fx.set_volume(0.5)
dive_fx = pygame.mixer.Sound('sounds/dive.wav')
dive_fx.set_volume(0.5)
heal_fx = pygame.mixer.Sound('sounds/heal.wav')
heal_fx.set_volume(0.5)
background_start_fx = pygame.mixer.Sound('sounds/background_start.wav')
background_start_fx.set_volume(0.02)
background_reset_fx = pygame.mixer.Sound('sounds/background_reset.wav')
background_reset_fx.set_volume(0.02)
background_run_fx = pygame.mixer.Sound('sounds/background_run.wav')
background_run_fx.set_volume(0.02)

img_list = []

for iterator in range(TILE_TYPES):
    if iterator == 21 or iterator == 23:
        img_temp = pygame.image.load(f'img/tiles/{iterator}.png')
        img_list.append(img_temp)
    else:
        img_temp = pygame.image.load(f'img/tiles/{iterator}.png')
        img_temp = pygame.transform.scale(img_temp, (TILE_SIZE, TILE_SIZE))
        img_list.append(img_temp)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

level_string_font = pygame.font.SysFont('Verdana', 80)
score_font = pygame.font.SysFont('Comic Sans MS', 30)
final_score_font = pygame.font.SysFont('Comic Sans MS', 50)
player_score = 0
player_health = 200
player_max_health = 200


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))


def draw_bg():
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
    for x in range(10):
        screen.blit(mountains_img, ((x * mountains_img.get_width()) - bg_scroll * 0.6,
                                    SCREEN_HEIGHT - mountains_img.get_height() - 250))
    for x in range(5):
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, SCREEN_HEIGHT - pine1_img.get_height() - 160))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()))


def reset_level():
    arrow_group.empty()
    decoration_group.empty()
    water_group.empty()
    exit_group.empty()
    enemy_group.empty()
    mushroom_group.empty()


class Button:
    def __init__(self, x, y, image_pointed, image_unpointed, scale):
        self.width = image_unpointed.get_width() * scale
        self.height = image_unpointed.get_height() * scale
        self.image = pygame.transform.scale(image_unpointed, (self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.clicked = False
        self.pointed_sound = False
        self.image_pointed = pygame.transform.scale(image_pointed, (self.width, self.height))
        self.image_unpointed = pygame.transform.scale(image_unpointed, (self.width, self.height))

    def draw(self, surface):
        action = False
        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            self.image = self.image_pointed
            if not self.pointed_sound:
                button_point_fx.play()
                self.pointed_sound = True
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                action = True
                self.clicked = True
                button_click_fx.play()
        else:
            self.pointed_sound = False
            self.image = self.image_unpointed

        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        surface.blit(self.image, (self.rect.x, self.rect.y))

        return action


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, speed):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.health = player_health
        self.max_health = self.health

        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.shoot_cooldown = 20
        self.in_water = False

        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        animation_types = ['Idle', 'Run', 'Jump', 'Death', 'Shoot']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/player/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/player/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * 1.25), int(img.get_height() * 1.25)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        global player_health
        self.update_animation()
        self.check_alive()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        player_health = self.health

    def move(self, moving_left, moving_right):
        screen_scroll = 0
        dx = 0
        dy = 0

        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        if self.jump and not self.in_air and self.vel_y == 0:
            self.vel_y = -11
            jump_fx.play()
            self.jump = False
            self.in_air = True

        self.vel_y += GRAVITY
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        if self.rect.y > SCREEN_HEIGHT:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
            dx = 0

        if pygame.sprite.spritecollide(self, water_group, False):
            if not self.in_water:
                self.in_water = True
                dive_fx.play()
            self.health -= 3

        for mushroom in mushroom_group:
            if self.rect.colliderect(mushroom.rect):
                if self.alive and self.health < self.max_health:
                    if self.health + mushroom.restore_hp > self.max_health:
                        self.health = self.max_health
                    else:
                        self.health += mushroom.restore_hp
                heal_fx.play()
                mushroom.kill()

        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        if self.rect.bottom > SCREEN_HEIGHT + 50:
            self.health = 0

        self.rect.x += dx
        self.rect.y += dy

        if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH and bg_scroll < (
                world.level_length * TILE_SIZE) - SCREEN_WIDTH) \
                or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
            self.rect.x -= dx
            screen_scroll = -dx

        return screen_scroll, level_complete

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            arrow = Arrow(self.rect.centerx + (0.50 * self.rect.size[0] * self.direction), self.rect.centery,
                          self.direction)
            arrow_group.add(arrow)
            shoot_fx.play()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def update_animation(self):
        animation_cooldown = 100
        if self.action == 0:
            animation_cooldown = 400
        if self.action == 4:
            animation_cooldown = 40
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.action == 1 and self.frame_index % 2 == 0:
                step_fx.play()

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
                if player.action == 4:
                    self.shoot()

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True

        self.health = 30 * level
        self.init_health = self.health
        self.speed = 1
        self.damage = 20

        self.flip = False
        self.direction = 1

        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

        self.vision = pygame.Rect(0, 0, 10, 10)
        self.idling = False
        self.idling_counter = 0
        self.had_hit = False

        animation_types = ['Idle', 'Run', 'Hit', 'Death']
        for animation in animation_types:
            temp_list = []
            num_of_frames = len(os.listdir(f'img/enemy/{animation}'))
            for i in range(num_of_frames):
                img = pygame.image.load(f'img/enemy/{animation}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * 1.5), int(img.get_height() * 1.5)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y + 27)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_animation()
        self.check_alive()

    def ai(self):
        if (self.vision.colliderect(player.rect) or self.had_hit) and self.alive:
            self.update_action(2)

        elif self.alive and player.alive:
            if not self.idling and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50

            else:
                if not self.idling:
                    self.move()
                    self.update_action(1)
                    self.vision.center = (self.rect.centerx + 5 * self.direction, self.rect.centery)
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        elif not self.alive:
            self.update_action(3)

        self.rect.x += screen_scroll

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

    def move(self):
        dx = self.speed * self.direction
        correction = 0
        if self.direction == 1:
            correction = 1

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect.x + dx + correction * 10, self.rect.y, self.width, self.height):
                self.direction *= -1
                self.flip = not self.flip
                return
            if tile[1].colliderect(self.rect.x + dx + self.direction * 30, self.rect.y + 1, self.width, self.height):
                self.rect.x += dx
                return

        self.direction *= -1
        self.flip = not self.flip

    def hit(self):
        player.health -= self.damage
        enemy_hit_fx.play()

    def update_animation(self):
        animation_cooldown = 100
        global player_score

        self.image = self.animation_list[self.action][self.frame_index]
        if self.action == 2 and self.frame_index == 3 and not self.had_hit and self.vision.colliderect(
                player.rect) and player.alive:
            self.had_hit = True
            self.hit()

        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.kill()
                player_score += self.init_health
            elif self.action == 2:
                self.had_hit = False
                self.frame_index = 0
            else:
                self.frame_index = 0

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            enemy_kill_fx.play()


class World:
    def __init__(self):
        self.obstacle_list = []
        self.level_length = 0

    def process_data(self, data):
        self.level_length = len(data[0])
        player = None
        player_info = None
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if 0 <= tile <= 12:
                        self.obstacle_list.append(tile_data)
                    elif tile == 13 or tile == 14:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile == 17:
                        mushroom = Mushroom(img, x * TILE_SIZE, y * TILE_SIZE, 20)
                        mushroom_group.add(mushroom)
                    elif tile == 18:
                        mushroom = Mushroom(img, x * TILE_SIZE, y * TILE_SIZE, 10)
                        mushroom_group.add(mushroom)
                    elif 15 <= tile <= 21:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 22:
                        player = Player(x * TILE_SIZE, y * TILE_SIZE, 5)
                        player_info = PlayerInfo(10, 10, player_health)
                    elif tile == 23:
                        exit_level = Exit(img, x * TILE_SIZE, y * TILE_SIZE)
                        exit_group.add(exit_level)
                    elif tile == 24:
                        enemy = Enemy(x * TILE_SIZE, y * TILE_SIZE)
                        enemy_group.add(enemy)

        return player, player_info

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x + TILE_SIZE // 2, y + TILE_SIZE)

    def update(self):
        self.rect.x += screen_scroll


class Mushroom(pygame.sprite.Sprite):
    def __init__(self, img, x, y, restore_hp):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x + TILE_SIZE // 2, y + TILE_SIZE)
        self.restore_hp = restore_hp

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x + TILE_SIZE // 2, y + TILE_SIZE)

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midbottom = (x + TILE_SIZE // 2, y + TILE_SIZE)

    def update(self):
        self.rect.x += screen_scroll


class PlayerInfo:
    def __init__(self, x, y, max_health):
        self.x = x
        self.y = y
        self.health = max_health
        self.max_health = player_max_health
        imgage = pygame.image.load('img/icons/hp_sign.png')
        self.hp_sign = pygame.transform.scale(imgage, (imgage.get_width() * 6, imgage.get_height() * 6))
        imgage = pygame.image.load('img/icons/heart_black.png')
        self.heart_black = pygame.transform.scale(imgage, (imgage.get_width() * 8, imgage.get_height() * 8))
        imgage = pygame.image.load('img/icons/heart_red.png')
        self.heart_red = pygame.transform.scale(imgage, (imgage.get_width() * 8, imgage.get_height() * 8))

    def draw(self, health):
        self.health = health

        screen.blit(self.hp_sign, (0, 0))
        screen.blit(self.heart_red, (100, 0))
        ratio = (self.max_health - health) / self.max_health
        img = pygame.transform.chop(self.heart_black, (0, self.heart_black.get_height() * ratio,
                                                       0, self.heart_black.get_height()))
        screen.blit(img, (100, 0))

        draw_text('Score: ' + str(player_score), score_font, WHITE, SCREEN_WIDTH - 180, 10)


class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = arrow_img
        if direction == -1:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y - 5)
        self.direction = direction

    def update(self):
        self.rect.x += (self.direction * self.speed)

        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
                arrow_wall_hit_fx.play()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, arrow_group, True):
                if enemy.alive:
                    enemy.health -= 25
                    hit_fx.play()


def generate_world():
    world_data = []
    for row in range(ROWS):
        r = [-1] * COLS
        world_data.append(r)

    with open('map_templates/map_template_start.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][y] = int(tile)

    map_templates = []
    for number in range(15):
        map_templates.append(f'map_templates/map_template_{number}.csv')

    for template_number in range(COLS // 10 - 2):
        rng = random.randint(0, 14)
        with open(map_templates[rng], newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=';')
            for x, row in enumerate(reader):
                for y, tile in enumerate(row):
                    world_data[x][(template_number + 1) * 10 + y] = int(tile)

    with open('map_templates/map_template_end.csv', newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        for x, row in enumerate(reader):
            for y, tile in enumerate(row):
                world_data[x][COLS - 10 + y] = int(tile)

    return world_data


class ScreenFade:
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0
        self.level_display_string_counter = 0

    def fade(self):
        fade_complete = False

        if self.direction == 1:
            if self.level_display_string_counter < 100:
                pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
                draw_text('Level ' + str(level), level_string_font, WHITE, SCREEN_WIDTH // 2 - 150,
                          SCREEN_HEIGHT // 2 - 100)
                self.level_display_string_counter += 1
            else:
                pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH // 2 - self.fade_counter, SCREEN_HEIGHT))
                pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH,
                                                       SCREEN_HEIGHT))
                self.fade_counter += self.speed
        if self.direction == 2:
            pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, self.fade_counter))
            self.fade_counter += self.speed
        if self.fade_counter >= SCREEN_HEIGHT:
            fade_complete = True

        return fade_complete


intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, BLACK, 4)

start_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150, start_pointed_img, start_unpointed_img, 1)
exit_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, exit_pointed_img, exit_unpointed_img, 1)
restart_button = Button(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, restart_pointed_img, restart_unpointed_img, 4)

arrow_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
enemy_group = pygame.sprite.Group()
mushroom_group = pygame.sprite.Group()

world_data = generate_world()
world = World()
player, player_info = world.process_data(world_data)
background_start_fx.play()

run = True
while run:
    clock.tick(FPS)

    if not start_game:
        draw_bg()
        screen.blit(author_sign_png, (SCREEN_WIDTH // 2 - 250, SCREEN_HEIGHT - 200))
        if start_button.draw(screen):
            start_game = True
            start_intro = True
            background_start_fx.stop()
        if exit_button.draw(screen):
            run = False
        if not pygame.mixer.get_busy():
            background_start_fx.play()
    else:
        draw_bg()
        world.draw()
        player_info.draw(player.health)

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        arrow_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        mushroom_group.update()

        arrow_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)
        mushroom_group.draw(screen)

        if start_intro:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0
                intro_fade.level_display_string_counter = 0
                background_reset_fx.stop()
                background_start_fx.stop()

        if not pygame.mixer.get_busy():
            background_run_fx.play()

        if player.alive:
            if shoot:
                player.update_action(4)
            elif player.in_air:
                player.update_action(2)
            elif moving_left or moving_right:
                player.update_action(1)
            else:
                player.update_action(0)
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                reset_level()
                world_data = generate_world()
                world = World()
                player, player_info = world.process_data(world_data)
        else:
            background_run_fx.stop()
            if not pygame.mixer.get_busy():
                background_reset_fx.play()
            screen_scroll = 0
            if death_fade.fade():
                draw_bg()
                level = 1
                screen.blit(game_over_png, (SCREEN_WIDTH // 2 - 250, 50))
                draw_text("Total score: " + str(player_score), final_score_font, WHITE, SCREEN_WIDTH // 2 - 200,
                          SCREEN_HEIGHT - 150)
                if restart_button.draw(screen):
                    player_health = 200
                    player_score = 0
                    background_reset_fx.stop()
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    reset_level()
                    world_data = generate_world()
                    world = World()
                    player, player_info = world.process_data(world_data)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False

    pygame.display.update()

pygame.quit()
