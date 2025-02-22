import pygame
import sys
import random
import time

pygame.init()
width, height = 800, 450
cell_size = 32
rows, cols = 10, 25
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tower Defense')

GREEN, GREY, WHITE, BLACK = (34,139,34), (169,169,169), (255,255,255), (0,0,0)
tower_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,165,0),(128,0,128)]
enemy_colors = [(0,128,128),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128)]
path_row = 5
towers, enemies = {}, []
selected_tower, wave_number = None, 1
player_pos = [0, 0]
start_time = None
enemy_count, max_enemies = 0, 10
enemy_speed = 20
running = True
allow_tower_placement = True
game_started = False

def draw_grid():
    for row in range(rows):
        for col in range(cols):
            color = towers.get((col, row), GREY if row == path_row else GREEN) # Get color of tower if placed else path or grass color
            pygame.draw.rect(screen, color, (col*cell_size, row*cell_size, cell_size, cell_size))
            pygame.draw.rect(screen, BLACK, (col*cell_size, row*cell_size, cell_size, cell_size), 1)
    for enemy in enemies:
        pygame.draw.rect(screen, enemy['color'], (enemy['x']*cell_size, path_row*cell_size, cell_size, cell_size))
    pygame.draw.rect(screen, WHITE, (player_pos[0]*cell_size, player_pos[1]*cell_size, cell_size, cell_size), 3)

def draw_ui():
    font = pygame.font.SysFont(None, 36)
    screen.blit(font.render(f'Selected Tower: {selected_tower if selected_tower else "None"}', True, BLACK), (10, rows*cell_size+10))
    screen.blit(font.render(f'Wave: {wave_number}', True, BLACK), (300, rows*cell_size+10))
    if game_started:
        screen.blit(font.render(f'Time: {int(time.time()-start_time)}', True, BLACK), (500, rows*cell_size+10))

def handle_input(event):
    global selected_tower
    global allow_tower_placement, game_started
    global start_time
    if event.type == pygame.KEYDOWN:
        if event.unicode in '123456':
            selected_tower = int(event.unicode)
        elif event.key == pygame.K_w and player_pos[1] > 0:
            player_pos[1] -= 1
        elif event.key == pygame.K_s and player_pos[1] < rows - 1:
            player_pos[1] += 1
        elif event.key == pygame.K_a and player_pos[0] > 0:
            player_pos[0] -= 1
        elif event.key == pygame.K_d and player_pos[0] < cols - 1:
            player_pos[0] += 1
        elif event.key == pygame.K_p and selected_tower and tuple(player_pos) not in towers and player_pos[1] != path_row and allow_tower_placement:
            towers[tuple(player_pos)] = tower_colors[selected_tower - 1]
        elif event.key == pygame.K_v:
            allow_tower_placement = False
            game_started = True
            start_time = time.time()

last_move_time = 0  # Track last movement update

def update_enemies():
    global enemy_count, last_move_time
    current_time = int(time.time() - start_time)

    # Spawn enemies once per second
    if enemy_count < max_enemies and current_time >= enemy_count:
        enemy_type = random.randint(1, 6)
        for enemy in enemies:
            enemy['x'] -= 1
        enemies.append({'x': cols, 'color': enemy_colors[enemy_type - 1]})
        enemy_count += 1

    # Move all enemies left only once per second after spawning is complete
    if enemy_count >= max_enemies and current_time > last_move_time:
        for enemy in enemies:
            enemy['x'] -= 1
        last_move_time = current_time  # Update last move time

    # Remove enemies that moved off-screen
    enemies[:] = [enemy for enemy in enemies if enemy['x'] >= 0]

clock = pygame.time.Clock()
while running:
    screen.fill(WHITE)
    draw_grid()
    draw_ui()
    if game_started:
        update_enemies()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        handle_input(event)
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()