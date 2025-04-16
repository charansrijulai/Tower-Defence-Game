import pygame
import sys
import random
import time

width, height = 800, 450
cell_size = 32
rows, cols = 10, 25
game_over = False
path_row = 5
towers, enemies = {}, []
selected_tower = None
wave_number = 1
player_pos = [0, 0]
start_time = None
enemy_count, max_enemies = 0, 10
enemy_speed = 20
running = True
allow_tower_placement = True
game_started = False
coins = 100
MAX_TOWERS = 5

pygame.init()
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Tower Defense')

GREEN, GREY, WHITE, BLACK = (34,139,34), (169,169,169), (255,255,255), (0,0,0)

tower_info = {
    0: {'color': (255,0,0), 'health': 10, 'damage': 1, 'range': 1, 'cost': 10},
    1: {'color': (0,255,0), 'health': 20, 'damage': 2, 'range': 2, 'cost': 15},
    2: {'color': (0,0,255), 'health': 30, 'damage': 3, 'range': 3, 'cost': 20},
    3: {'color': (255,255,0), 'health': 40, 'damage': 4, 'range': 4, 'cost': 25},
    4: {'color': (255,165,0), 'health': 50, 'damage': 5, 'range': 5, 'cost': 30},
    5: {'color': (128,0,128), 'health': 60, 'damage': 6, 'range': 6, 'cost': 35}
}
enemy_info = {
    0: {'color': (0,128,128), 'health': 10, 'damage': 1, 'range': 1},
    1: {'color': (128,0,0), 'health': 20, 'damage': 2, 'range': 2},
    2: {'color': (0,128,0), 'health': 30, 'damage': 3, 'range': 3},
    3: {'color': (128,128,0), 'health': 40, 'damage': 4, 'range': 4},
    4: {'color': (0,0,128), 'health': 50, 'damage': 5, 'range': 5},
    5: {'color': (128,0,128), 'health': 60, 'damage': 6, 'range': 6}
}

def draw_grid():
    font = pygame.font.SysFont(None, 24)

    for row in range(rows):
        for col in range(cols):
            if (col, row) in towers:
                tower_color = tower_info[towers[(col, row)]['type']]['color']
                tower_type = next((key for key, info in tower_info.items() if info['color'] == tower_color), None)
                tower_health = towers[(col, row)]['health']

                pygame.draw.rect(screen, tower_color, (col * cell_size, row * cell_size, cell_size, cell_size))
                text = font.render(str(tower_health), True, BLACK)
                screen.blit(text, (col * cell_size + cell_size // 3, row * cell_size + cell_size // 4))
            else:
                color = GREY if row == path_row else GREEN
                pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size))

            pygame.draw.rect(screen, BLACK, (col * cell_size, row * cell_size, cell_size, cell_size), 1)

    for enemy in enemies:
        pygame.draw.rect(screen, enemy['color'], (enemy['x'] * cell_size, path_row * cell_size, cell_size, cell_size))
        enemy_type = next((key for key, info in enemy_info.items() if info['color'] == enemy['color']), None)
        # enemy_health = enemy_info[enemy_type]['health'] if enemy_type is not None else 1
        enemy_health = enemy['health']

        text = font.render(str(enemy_health), True, WHITE)
        screen.blit(text, (enemy['x'] * cell_size + cell_size // 3, path_row * cell_size + cell_size // 4))

    pygame.draw.rect(screen, WHITE, (player_pos[0] * cell_size, player_pos[1] * cell_size, cell_size, cell_size), 3)

def draw_ui():
    font = pygame.font.SysFont(None, 36)

    screen.blit(font.render(f'Selected Tower: {selected_tower if selected_tower else "None"}', True, BLACK), (10, rows*cell_size+10))
    screen.blit(font.render(f'Wave: {wave_number}', True, BLACK), (300, rows*cell_size+10))
    screen.blit(font.render(f'Coins: {coins}', True, BLACK), (425, rows * cell_size + 10))

    if game_started:
        screen.blit(font.render(f'Time: {int(time.time()-start_time)}', True, BLACK), (650, rows*cell_size+10))

    available_towers = [str(i) for i in range(1, 7) if i <= wave_number]
    locked_towers = [str(i) for i in range(1, 7) if i > wave_number]
    avail_text = font.render(f'Available Towers: {",".join(available_towers)}', True, BLACK)
    screen.blit(avail_text, (10, rows * cell_size + 50))
    locked_text = font.render(f'Locked Towers: {",".join(locked_towers)}', True, BLACK)
    screen.blit(locked_text, (10, rows * cell_size + 80))

    towers_count = font.render(f'Towers placed: {len(towers)}', True, BLACK)
    screen.blit(towers_count, (400, rows * cell_size + 50))

def handle_input(event):
    global selected_tower
    global allow_tower_placement, game_started
    global start_time
    global coins
    if event.type == pygame.KEYDOWN:
        if event.unicode in '123456':
            tower_choice = int(event.unicode)
            if tower_choice <= wave_number:
                selected_tower = tower_choice
            else:
                print('Tower locked for current wave')
        elif event.key == pygame.K_w and player_pos[1] > 0:
            player_pos[1] -= 1
        elif event.key == pygame.K_s and player_pos[1] < rows - 1:
            player_pos[1] += 1
        elif event.key == pygame.K_a and player_pos[0] > 0:
            player_pos[0] -= 1
        elif event.key == pygame.K_d and player_pos[0] < cols - 1:
            player_pos[0] += 1
        elif event.key == pygame.K_p and selected_tower and tuple(player_pos) not in towers and player_pos[1] != path_row and allow_tower_placement:
            cost = tower_info[selected_tower - 1]['cost']
            if coins >= cost:
                coins -= cost
                towers[tuple(player_pos)] = {'type': selected_tower - 1, 'health': tower_info[selected_tower - 1]['health']}
            else:
                print("Not enough coins to purchase this tower")
        elif event.key == pygame.K_v:
            allow_tower_placement = False
            game_started = True
            start_time = time.time()

last_move_time = 0  # Track last movement update

def update_enemies():
    global enemy_count, last_move_time, start_time
    global game_started, allow_tower_placement
    global game_over, wave_number, max_enemies
    global coins
    if start_time is None:
        return
    current_time = int(time.time() - start_time)

    # Spawn enemies once per second
    if enemy_count < max_enemies and current_time >= enemy_count:
        last_move_time = current_time
        allowed_enemy_max = wave_number if wave_number <= 6 else 6
        enemy_type = random.randint(1, allowed_enemy_max)
        resolve_combat()
        for enemy in enemies:
            enemy['x'] -= 1
        enemies.append({'x': cols, 'type': enemy_type - 1, 'health': enemy_info[enemy_type - 1]['health'], 'color': enemy_info[enemy_type - 1]['color']})
        enemy_count += 1

    for enemy in enemies:
        if enemy['x'] == 0:
            game_started = False
            allow_tower_placement = True
            game_over = True
            break

    # Move all enemies left only once per second after spawning is complete
    if enemy_count >= max_enemies and current_time > last_move_time:
        resolve_combat()
        for enemy in enemies:
            enemy['x'] -= 1
        last_move_time = current_time  # Update last move time

    # Remove dead enemies
    enemies[:] = [enemy for enemy in enemies if enemy['health'] > 0]

    if enemy_count >= max_enemies and len(enemies) == 0:
        wave_number += 1
        enemy_count = 0
        max_enemies = 10 + (wave_number - 1) * 5
        coins += wave_number * 20
        allow_tower_placement = True
        game_started = False
        start_time = None

def resolve_combat():
    global enemies, towers

    enemies_to_remove = []
    towers_to_remove = []

    for (tower_x, tower_y), info in towers.items():
        tower_type = info['type']
        tower_range = tower_info[tower_type]['range']
        tower_damage = tower_info[tower_type]['damage']
        tower_health = tower_info[tower_type]['health']

        for enemy in enemies:
            enemy_x, enemy_y = enemy['x'], path_row

            enemy_type = enemy['type']

            # Calculate Manhattan distance
            distance = abs(tower_x - enemy_x) + abs(tower_y - enemy_y)

            # Tower attacks enemy
            if distance <= tower_range:
                enemy['health'] -= tower_damage  # Enemy takes damage
                if enemy['health'] <= 0:
                    enemies_to_remove.append(enemy)  # Mark enemy for removal

            # Enemy attacks tower
            if distance <= enemy_info[enemy_type]['range']:
                info['health'] -= enemy_info[enemy_type]['damage']  # Tower takes damage
                if info['health'] <= 0:
                    towers_to_remove.append((tower_x, tower_y))  # Mark tower for removal

    # Remove dead enemies
    enemies = [enemy for enemy in enemies if enemy not in enemies_to_remove]

    # Remove destroyed towers
    for tower in towers_to_remove:
        if tower in towers:
            del towers[tower]

def draw_game_over():
    if game_over:
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(width // 2, height // 2))
        screen.blit(text, text_rect)

clock = pygame.time.Clock()
while running:
    screen.fill(WHITE)
    draw_grid()
    draw_ui()
    if game_started:
        update_enemies()
    draw_game_over()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        handle_input(event)
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()