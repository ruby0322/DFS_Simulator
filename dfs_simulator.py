import pygame
import sys
from time import sleep
import threading
import random
import time


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BROWN = (133, 68, 16)
GREEN = (34, 201, 54)
YELLOW = (255, 196, 0)
LIGHT_GREEN = (0, 255, 187)

PIXEL_PER_BLOCK: int = 40
BORDER_PIXEL: int = 3

SCREEN_HEIGHT: int = 1000
SCREEN_WIDTH: int  = 1000

TOTAL_BLOCKS = (SCREEN_HEIGHT//PIXEL_PER_BLOCK) * (SCREEN_WIDTH//PIXEL_PER_BLOCK)

DISCOVERED_ROAD: int = 0
UNTOUCHED_ROAD: int = 1
WALL: int = 2
GOAL: int = 3
WORKING_BLOCK: int = 4

SEARCH_TIME: float = .02
DELTA_TIME: float = .0004

pygame.init()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('DFS Simulator')
buffer = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

screen.fill(BLACK)
timer = 0
font = pygame.font.Font('my_font.ttf', 120)
small_font = pygame.font.Font('my_font.ttf', 58)
search_time_text_surf = small_font.render(f'SearchTime: {SEARCH_TIME*1000:.2f}(ms/block)', True, BLACK)

success_sound_effect = pygame.mixer.Sound('success.mp3')

maze = []
goal_found = False

all_sprites = pygame.sprite.Group()
text_group = pygame.sprite.Group()

class Block(pygame.sprite.Sprite):
    
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((PIXEL_PER_BLOCK-BORDER_PIXEL, PIXEL_PER_BLOCK-BORDER_PIXEL))
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x*PIXEL_PER_BLOCK + BORDER_PIXEL
        self.rect.y = y*PIXEL_PER_BLOCK + BORDER_PIXEL
        
    def update(self):
        global goal_found
        if maze[self.y][self.x] == UNTOUCHED_ROAD:
            self.image.fill(WHITE)
        elif maze[self.y][self.x] == WALL:
            self.image.fill(BROWN)
        elif maze[self.y][self.x] == GOAL:
            if goal_found:
                self.image.fill(LIGHT_GREEN)
            else:
                self.image.fill(GREEN)
        elif maze[self.y][self.x] == WORKING_BLOCK:
            self.image.fill(YELLOW)
        else:
            self.image.fill(RED)

class DisplayText(pygame.sprite.Sprite):
    
    LIFE_TIME = 300  # Frames
    
    def __init__(self, text, font, x, y) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(text, True, BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.timer = 0
        
    def update(self) -> None:
        self.timer += 1
        self.rect.y -= 1
        self.image.set_alpha((1 - (self.timer/DisplayText.LIFE_TIME)) * 255)
        
        if self.timer >= DisplayText.LIFE_TIME:
            self.kill()
        

for y in range(SCREEN_HEIGHT//PIXEL_PER_BLOCK):
    for x in range(SCREEN_WIDTH//PIXEL_PER_BLOCK):
        all_sprites.add(Block(x, y))
        
def generate_maze():
    maze = []
    for _ in range(SCREEN_HEIGHT//PIXEL_PER_BLOCK):
        row = []
        for _ in range(SCREEN_WIDTH//PIXEL_PER_BLOCK):
            row.append(UNTOUCHED_ROAD)
        maze.append(row)
    
    for _ in range(100):
        maze[random.randrange(0, SCREEN_WIDTH//PIXEL_PER_BLOCK)][random.randrange(0, SCREEN_WIDTH//PIXEL_PER_BLOCK)] = WALL
    
    goal_x, goal_y = (0, 0)
    while ((not goal_x) and (not goal_y)):
        goal_x, goal_y = random.randrange(0, SCREEN_WIDTH//PIXEL_PER_BLOCK), random.randrange(0, SCREEN_WIDTH//PIXEL_PER_BLOCK)
    
    maze[goal_y][goal_x] = GOAL

    return maze


def count_block(matrix: list[list[int]]) -> tuple[int, int]:
    wall: int = 0
    discovered: int = 0
    for row in matrix:
        for elem in row:
            if elem == DISCOVERED_ROAD:
                discovered += 1
            elif elem == WALL:
                wall += 1
    return (discovered, wall)


def dfs(matrix: list[list[int]], entry_x: int, entry_y: int) -> None:
    global goal_found, success_sound_effect
    sleep(SEARCH_TIME*.8)
    matrix_size = len(matrix)
    matrix[entry_y][entry_x] = WORKING_BLOCK

    if ((entry_y-1 >= 0 and matrix[entry_y-1][entry_x] == GOAL)
    or (entry_x+1 < matrix_size and matrix[entry_y][entry_x+1] == GOAL)
    or (entry_y+1 < matrix_size and matrix[entry_y+1][entry_x] == GOAL)
    or (entry_x-1 >= 0 and matrix[entry_y][entry_x-1] == GOAL)):
        goal_found = True
        success_sound_effect.play()

    if not goal_found and entry_y-1 >= 0 and matrix[entry_y-1][entry_x] == UNTOUCHED_ROAD:
        dfs(matrix, entry_x, entry_y-1)
    
    if not goal_found and entry_x+1 < matrix_size and matrix[entry_y][entry_x+1] == UNTOUCHED_ROAD:
        dfs(matrix, entry_x+1, entry_y)

    if not goal_found and entry_y+1 < matrix_size and matrix[entry_y+1][entry_x] == UNTOUCHED_ROAD:
        dfs(matrix, entry_x, entry_y+1)     
        
    if not goal_found and entry_x-1 >= 0 and matrix[entry_y][entry_x-1] == UNTOUCHED_ROAD:
        dfs(matrix, entry_x-1, entry_y)
        
    sleep(SEARCH_TIME*.2)
    matrix[entry_y][entry_x] = DISCOVERED_ROAD
    

def dfs_loop():
    global maze, goal_found, timer, my_font
    while True:
        goal_found = False
        timer = time.time()
        maze = generate_maze()
        dfs(maze, 0, 0)
        discovered, wall = count_block(maze)
        
        display_text = 'Found In' if goal_found else 'Unable To Find'
        display_text_sprite = DisplayText(display_text, font, SCREEN_WIDTH//2, SCREEN_HEIGHT//2-100)
        all_sprites.add(display_text_sprite)
        text_group.add(display_text_sprite)

        display_text = f'{(time.time() - timer)*1000:0.2f}ms'
        display_text_sprite = DisplayText(display_text, font, SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
        all_sprites.add(display_text_sprite)
        text_group.add(display_text_sprite)

        display_text = f'({(discovered/(TOTAL_BLOCKS-wall))*100:0.2f}% Touched)'
        display_text_sprite = DisplayText(display_text, font, SCREEN_WIDTH//2, SCREEN_HEIGHT//2+100)
        all_sprites.add(display_text_sprite)
        text_group.add(display_text_sprite)

        sleep(2)
    

# DFS Loop 
maze = generate_maze()
dfs_thread = threading.Thread(target=dfs_loop)
dfs_thread.start()

# Main Game Loop
speeding_up = False
slowing_down = False
while True:
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                speeding_up = True
            if event.key == pygame.K_DOWN:
                slowing_down = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_UP:
                speeding_up = False
            if event.key == pygame.K_DOWN:
                slowing_down = False
    
    if speeding_up and SEARCH_TIME - DELTA_TIME >= 0:
        SEARCH_TIME -= DELTA_TIME
        search_time_text_surf = small_font.render(f'SearchTime: {SEARCH_TIME*1000:.2f}(ms/block)', True, BLACK)
        
    if slowing_down:
        SEARCH_TIME += DELTA_TIME
        search_time_text_surf = small_font.render(f'SearchTime: {SEARCH_TIME*1000:.2f}(ms/block)', True, BLACK)
    
    all_sprites.update()
    
    all_sprites.draw(buffer)
    buffer.blit(search_time_text_surf, (10, SCREEN_HEIGHT - 45))
    screen.blit(buffer, (0, 0))
    pygame.display.update()

