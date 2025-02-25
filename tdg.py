# # Tower Defense Game with Pygame - Code Explanation

# import pygame  # Importing Pygame for game development
# import sys     # Importing sys to exit the game

# pygame.init()  # Initializing Pygame

# # Screen and grid settings
# width, height = 800, 450  # Window dimensions
# cell_size = 32           # Size of each grid cell
# rows, cols = 10, 25      # Number of grid rows and columns

# # Creating Pygame window
# screen = pygame.display.set_mode((width, height))
# pygame.display.set_caption('Tower Defense')  # Window title

# # Colors for display
# GREEN, GREY, WHITE, BLACK = (34,139,34), (169,169,169), (255,255,255), (0,0,0)
# tower_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,165,0),(128,0,128)]  # Unique colors for 6 towers
# path_row = 5  # Path is on row 5
# towers = {}   # Dictionary to store tower placements
# selected_tower = None  # Currently selected tower
# timer = pygame.time.Clock()  # Game clock
# player_pos = [0, 0]  # Player's cursor/grid position
# running = True       # Game loop control

# # Function to draw the grid and towers
# def draw_grid():
#     for row in range(rows):
#         for col in range(cols):
#             color = towers.get((col, row), GREY if row == path_row else GREEN)  # Path or grass color
#             pygame.draw.rect(screen, color, (col * cell_size, row * cell_size, cell_size, cell_size))  # Draw cell
#             pygame.draw.rect(screen, BLACK, (col * cell_size, row * cell_size, cell_size, cell_size), 1)  # Grid lines
#     pygame.draw.rect(screen, WHITE, (player_pos[0] * cell_size, player_pos[1] * cell_size, cell_size, cell_size), 3)  # Player cursor

# # Function to display selected tower
# def draw_ui():
#     font = pygame.font.SysFont(None, 36)
#     text = font.render(f'Selected Tower: {selected_tower if selected_tower else "None"}', True, BLACK)
#     screen.blit(text, (10, rows * cell_size + 10))

# # Function to handle keyboard inputs
# def handle_input(event):
#     global selected_tower
#     if event.type == pygame.KEYDOWN:
#         if event.unicode in '123456':
#             selected_tower = int(event.unicode)  # Select tower 1-6
#         elif event.key == pygame.K_w and player_pos[1] > 0:
#             player_pos[1] -= 1  # Move up
#         elif event.key == pygame.K_s and player_pos[1] < rows - 1:
#             player_pos[1] += 1  # Move down
#         elif event.key == pygame.K_a and player_pos[0] > 0:
#             player_pos[0] -= 1  # Move left
#         elif event.key == pygame.K_d and player_pos[0] < cols - 1:
#             player_pos[0] += 1  # Move right
#         elif event.key == pygame.K_p and selected_tower and tuple(player_pos) not in towers and player_pos[1] != path_row:
#             towers[tuple(player_pos)] = tower_colors[selected_tower - 1]  # Place tower

# # Main game loop
# while running:
#     screen.fill(WHITE)  # Clear screen
#     draw_grid()        # Draw grid and towers
#     draw_ui()          # Display selected tower info
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             running = False  # Exit on close
#         handle_input(event)
#     pygame.display.flip()  # Update display
#     timer.tick(60)         # Limit to 60 FPS

# pygame.quit()  # Quit Pygame
# sys.exit()     # Exit program

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
game_over = False

GREEN, GREY, WHITE, BLACK = (34,139,34), (169,169,169), (255,255,255), (0,0,0)
tower_colors = [(255,0,0),(0,255,0),(0,0,255),(255,255,0),(255,165,0),(128,0,128)]
tower_info = {
    0: {
        'color': (255,0,0),
        'damage': 1
    },
    1: {
        'color': (0,255,0),
        'damage': 2
    },
    2: {
        'color': (0,0,255),
        'damage': 3
    },
    3: {
        'color': (255,255,0),
        'damage': 4
    },
    4: {
        'color': (255,165,0),
        'damage': 5
    },
    5: {
        'color': (128,0,128),
        'damage': 6
    }
}
enemy_colors = [(0,128,128),(128,0,0),(0,128,0),(128,128,0),(0,0,128),(128,0,128)]
enemy_info = {
    0: {
        'color': (0,128,128),
        'health': 10
    },
    1: {
        'color': (128,0,0),
        'health': 20
    },
    2: {
        'color': (0,128,0),
        'health': 30
    },
    3: {
        'color': (128,128,0),
        'health': 40
    },
    4: {
        'color': (0,0,128),
        'health': 50
    },
    5: {
        'color': (128,0,128),
        'health': 60
    }
}
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
    #Display available and locked towers based on current wave
    available_towers = [str(i) for i in range(1, 7) if i <= wave_number]
    locked_towers = [str(i) for i in range(1, 7) if i > wave_number]
    avail_text = font.render(f'Available Towers: {",".join(available_towers)}', True, BLACK)
    screen.blit(avail_text, (10, rows * cell_size + 50))
    locked_text = font.render(f'Locked Towers: {",".join(locked_towers)}', True, BLACK)
    screen.blit(locked_text, (10, rows * cell_size + 80))

    #Display Enemy type range allowed in current wave
    # allowed_enemy_types = f'Enemy Types: 1 to {min(wave_number, 6)}'
    # enemy_text = font.render(allowed_enemy_types, True, BLACK)
    # screen.blit(enemy_text, (10, rows * cell_size + 110))

    #Display counts for Towers place and enemies on screen
    towers_count = font.render(f'Towers placed: {len(towers)}', True, BLACK)
    screen.blit(towers_count, (400, rows * cell_size + 50))
    # enemies_count = font.render(f'Enemies: {len(enemies)}', True, BLACK)
    # screen.blit(enemies_count, (400, rows * cell_size + 80))

def handle_input(event):
    global selected_tower
    global allow_tower_placement, game_started
    global start_time
    if event.type == pygame.KEYDOWN:
        if event.unicode in '123456':
            # selected_tower = int(event.unicode)
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
            towers[tuple(player_pos)] = tower_info[selected_tower - 1]['color']
        elif event.key == pygame.K_v:
            allow_tower_placement = False
            game_started = True
            start_time = time.time()
        # elif event.key == pygame.K_r and game_over:
        #     reset_game()

last_move_time = 0  # Track last movement update

# def reset_game():
#     global towers, enemies, selected_tower, wave_number, player_pos
#     global start_time, enemy_count, game_started, allow_tower_placement, game_over

#     towers = {}
#     enemies = []
#     selected_tower = None
#     wave_number = 1
#     player_pos = [0, 0]
#     start_time = None
#     enemy_count = 0
#     allow_tower_placement = True
#     game_started = False
#     game_over = False

def update_enemies():
    global enemy_count, last_move_time, start_time
    global game_started, allow_tower_placement
    global game_over, wave_number, max_enemies
    if start_time is None:
        return
    current_time = int(time.time() - start_time)

    # Spawn enemies once per second
    if enemy_count < max_enemies and current_time >= enemy_count:
        allowed_enemy_max = wave_number if wave_number <= 6 else 6
        enemy_type = random.randint(1, allowed_enemy_max)
        # enemy_type = random.randint(1, 6)
        for enemy in enemies:
            enemy['x'] -= 1
        enemies.append({'x': cols, 'color': enemy_colors[enemy_type - 1]})
        enemy_count += 1

    for enemy in enemies:
        if enemy['x'] == 0:
            game_started = False
            allow_tower_placement = True
            game_over = True
            break

    # Move all enemies left only once per second after spawning is complete
    if enemy_count >= max_enemies and current_time > last_move_time:
        for enemy in enemies:
            enemy['x'] -= 1
        last_move_time = current_time  # Update last move time

    # Remove enemies that moved off-screen
    enemies[:] = [enemy for enemy in enemies if enemy['x'] >= 0]

    if enemy_count >= max_enemies and len(enemies) == 0:
        wave_number += 1
        enemy_count = 0
        max_enemies = 10 + (wave_number - 1) * 5 #10, 15, 20, 25, 30, 35 ......

        allow_tower_placement = True
        game_started = False
        start_time = None

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