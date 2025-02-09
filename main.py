import pygame
import csv
import constants
from character import Character
from weapon import Weapon
from items import Item
from world import World

pygame.init()

screen = pygame.display.set_mode((constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT))
pygame.display.set_caption("Dungeon Crawler")

# create clock for maintaining constant fps
clock = pygame.time.Clock()

# define game variables
level = 1

# define player movement variables
moving_left = False
moving_right = False
moving_up = False
moving_down = False

# define font
font = pygame.font.Font("assets/fonts/AtariClassic.ttf", 20)

# helper function to load images
def scale_img(image, scale):
    w = image.get_width()
    h = image.get_height()
    return pygame.transform.scale(image, (int(w * scale), int(h * scale)))

# load heart images
heart_empty = scale_img(pygame.image.load("assets/images/items/heart_empty.png").convert_alpha(), constants.ITEM_SCALE)
heart_half = scale_img(pygame.image.load("assets/images/items/heart_half.png").convert_alpha(), constants.ITEM_SCALE)
heart_full = scale_img(pygame.image.load("assets/images/items/heart_full.png").convert_alpha(), constants.ITEM_SCALE)

# load coin images
coin_images = []
for x in range(4):
    img = scale_img(pygame.image.load(f"assets/images/items/coin_f{x}.png").convert_alpha(),constants.ITEM_SCALE)
    coin_images.append(img)

# load potion image
red_potion = scale_img(pygame.image.load("assets/images/items/potion_red.png").convert_alpha(), constants.POTION_SCALE)

# load tile images
tile_list = []
for x in range(constants.TILE_TYPES):
    tile_image = pygame.image.load(f"assets/images/tiles/{x}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (constants.TILE_SIZE, constants.TILE_SIZE))
    tile_list.append(tile_image)

# load weapon image
bow_image = scale_img(pygame.image.load("assets/images/weapons/bow.png").convert_alpha(), constants.WEAPON_SCALE)
arrow_image = scale_img(pygame.image.load("assets/images/weapons/arrow.png").convert_alpha(), constants.WEAPON_SCALE)

# load character images
mob_animations = []
mob_types = ['elf', 'imp', 'skeleton', 'goblin', 'muddy', 'tiny_zombie', 'big_demon']

# load player image
animation_types = ['idle', 'run']
for mob in mob_types:
    animation_list = []
    for animation in animation_types:
        # reset temporary list of images
        temp_list = []
        for i in range(4):
            img = pygame.image.load(f"assets/images/characters/{mob}/{animation}/{i}.png").convert_alpha()
            img = scale_img(img, constants.SCALE)
            temp_list.append(img)
        animation_list.append(temp_list)
    mob_animations.append(animation_list)

# function for outputting text onto the screen
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# function for displaying game info
def draw_info():
    # draw panel
    pygame.draw.rect(screen, constants.PANEL, (0, 0, constants.SCREEN_WIDTH, 50))
    pygame.draw.line(screen, constants.WHITE, (0, 50), (constants.SCREEN_WIDTH, 50), 2)

    # draw lives
    half_heart_drawn = False
    for i in range(5):
        if player.health >=  ((i + 1) * 20):
            screen.blit(heart_full, (10 + (i * 50), 0))
        elif (player.health % 20 > 0) and half_heart_drawn == False:
            screen.blit(heart_half, (10 + (i * 50), 0))
            half_heart_drawn = True
        else:    
            screen.blit(heart_empty, (10 + (i * 50), 0))

    # draw score
    draw_text(f"X{player.score}", font, constants.WHITE, constants.SCREEN_WIDTH - 100, 15)

# create empty tile list
world_data = []
for row in range(constants.ROWS):
    r = [-1] * constants.COLS
    world_data.append(r)
# load in level data and create world
with open(f"levels/level{level}_data.csv", newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
world.process_data(world_data, tile_list)

# def draw_grid():
#     for x in range(30):
#         pygame.draw.line(screen, constants.WHITE, (x * constants.TILE_SIZE, 0), (x * constants.TILE_SIZE, constants.SCREEN_HEIGHT))
#         pygame.draw.line(screen, constants.WHITE, (0, x * constants.TILE_SIZE), (constants.SCREEN_WIDTH, x * constants.TILE_SIZE))
                        

# damage text class
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(str(damage), True, color)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        # move damage text up
        self.rect.y -= 1
        # delete after a few frames
        self.counter += 1
        if self.counter > 30:
            self.kill()


# create player
player = Character(100, 100, 100, mob_animations, 0)

# create enemy
enemy = Character(200, 300, 100, mob_animations, 1)

# create player's weapon
bow = Weapon(bow_image, arrow_image)

# create empty enemy list
enemy_list = []
enemy_list.append(enemy)

# create sprite group
damage_text_group = pygame.sprite.Group()
arrow_group = pygame.sprite.Group()
item_group = pygame.sprite.Group()

score_coin = Item(constants.SCREEN_WIDTH - 115, 23, 0, coin_images)
item_group.add(score_coin)

potion = Item(200, 200, 1, [red_potion])
item_group.add(potion)
coin = Item(400, 400, 0, coin_images)
item_group.add(coin)

# main game loop
run = True
while run:

    # control frame rate
    clock.tick(constants.FPS)

    # fill screen with white
    screen.fill(constants.BG)

    # draw grid
    # draw_grid()

    # calfulate player movement
    dx = 0
    dy = 0
    if moving_right == True:
        dx = constants.SPEED
    if moving_left == True:
        dx = -constants.SPEED
    if moving_up == True:
        dy = -constants.SPEED
    if moving_down == True:
        dy = constants.SPEED

    # move player
    player.move(dx, dy)

    # update enemy
    for enemy in enemy_list:
        enemy.update()

    # update player animation
    player.update()
    arrow = bow.update(player)
    if arrow:
        arrow_group.add(arrow)
    for arrow in arrow_group:
        damage, damage_pos = arrow.update(enemy_list)
        if damage:
            damage_text = DamageText(damage_pos.centerx, damage_pos.y, str(damage), constants.RED)
            damage_text_group.add(damage_text)
    damage_text_group.update()
    item_group.update(player)

    # draw world
    world.draw(screen)
    
    # draw enemy on screen
    for enemy in enemy_list:
        enemy.draw(screen)

    # draw player on screen
    player.draw(screen)
    bow.draw(screen)
    for arrow in arrow_group:
        arrow.draw(screen)
    damage_text_group.draw(screen)
    item_group.draw(screen)
    draw_info()
    score_coin.draw(screen)


    # event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        
        # take keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_w:
                moving_up = True
            if event.key == pygame.K_s:
                moving_down = True

        # take keyboard releases
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_w:
                moving_up = False
            if event.key == pygame.K_s:
                moving_down = False

    # update display
    pygame.display.update()

pygame.quit()