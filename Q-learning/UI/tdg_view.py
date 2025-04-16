import pygame
import time
from tdg_controller import GameController

# game = GameController('dqn')
game = GameController()
observation = game.reset()

data = game.get_game_data()
rows, cols = data["rows"], data["cols"]
path_row = data["path_row"]

cell_size = 75
window_width = cols * cell_size
window_height = rows * cell_size + 150 

GREEN = (34, 139, 34)
GREY = (169, 169, 169)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Tower Defense Game')

enemy_move_time = time.time()

# Towers and enemies
tower_images = {
    1: pygame.image.load("../images/watchtower.png").convert_alpha(),
    2: pygame.image.load("../images/watchtower_lvl2.png").convert_alpha(),
    3: pygame.image.load("../images/watchtower_lvl3.png").convert_alpha()
}
enemy_images = {
    0: pygame.image.load("../images/goblinsword.png").convert_alpha(),
    1: pygame.image.load("../images/orc_hig.png").convert_alpha()
}
# Scale images to fit the cell size.
for key in tower_images:
    tower_images[key] = pygame.transform.scale(tower_images[key], (cell_size, cell_size))
for key in enemy_images:
    enemy_images[key] = pygame.transform.scale(enemy_images[key], (cell_size, cell_size))

#Load Textured Tiles for the Grid
grass_tile = pygame.image.load("../images/grass.png").convert_alpha()
grass_tile = pygame.transform.scale(grass_tile, (cell_size, cell_size))
path_tile = pygame.image.load("../images/cobblestone.png").convert_alpha()
path_tile = pygame.transform.scale(path_tile, (cell_size, cell_size))

#Health Bar Helper Function
def draw_health_bar(x, y, current_health, max_health, width, height):

    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))

    health_ratio = current_health / max_health if max_health > 0 else 0
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(width * health_ratio), height))

def draw_grid():
    
    font = pygame.font.SysFont(None, 24)
    data = game.get_game_data()
    towers = data["towers"]
    enemies = data["enemies"]
    player_pos = data["player_pos"]
    tower_info = data["tower_info"]
    enemy_info = data["enemy_info"]
    
    for row in range(rows):
        for col in range(cols):
            pos = (row, col)  # Towers are stored with (row, col)
            # Instead of drawing a colored rectangle, blit the appropriate textured tile.
            if row == path_row:
                screen.blit(path_tile, (col * cell_size, row * cell_size))
            else:
                screen.blit(grass_tile, (col * cell_size, row * cell_size))
            pygame.draw.rect(screen, BLACK, (col * cell_size, row * cell_size, cell_size, cell_size), 1)
            
            # Draw towers.
            if pos in towers:
                tower = towers[pos]
                tower_type = tower['type']
                current_health = tower['health']
                max_health = tower_info[tower_type]['health']
                img = tower_images.get(tower_type)
                if img:
                    screen.blit(img, (col * cell_size, row * cell_size))
                else:
                    pygame.draw.rect(screen, tower_info[tower_type]['color'],
                                     (col * cell_size, row * cell_size, cell_size, cell_size))
                # Draw health bar below the tower image.
                bar_y = row * cell_size + cell_size - 10  # Adjust as needed
                draw_health_bar(col * cell_size, bar_y, current_health, max_health, cell_size, 5)
            
    # Draw enemies.
    font_small = pygame.font.SysFont(None, 20)
    for enemy in enemies:
        enemy_x = enemy.get('x', cols - 1)
        enemy_y = path_row
        enemy_type = enemy.get('type', 0)
        current_health = enemy['health']
        max_health = enemy_info[enemy_type]['health']
        img = enemy_images.get(enemy_type)
        if img:
            screen.blit(img, (enemy_x * cell_size, enemy_y * cell_size))
        else:
            pygame.draw.rect(screen, enemy_info[enemy_type]['color'],
                             (enemy_x * cell_size, enemy_y * cell_size, cell_size, cell_size))
        # Draw enemy health bar below the image.
        bar_y = enemy_y * cell_size + cell_size - 10
        draw_health_bar(enemy_x * cell_size, bar_y, current_health, max_health, cell_size, 5)
    
    # Draw player position (optional outline).
    pygame.draw.rect(screen, WHITE,
                     (player_pos[1] * cell_size, player_pos[0] * cell_size, cell_size, cell_size), 3)

def draw_ui():
    font = pygame.font.SysFont(None, 24)
    data = game.get_game_data()
    
    # Check win condition
    if data["game_over"] or data["current_wave"] >  game.env.max_waves:
        win_text = "GAME WON" if data["current_wave"] > game.env.max_waves else "GAME OVER"
        screen.blit(font.render(win_text, True, (255, 0, 0)), (10, rows * cell_size + 10))
        screen.blit(font.render(f"Final Wave: {data['current_wave']}", True, BLACK), (10, rows * cell_size + 40))
        screen.blit(font.render(f"Final Coins: {data['coins']}", True, BLACK), (10, rows * cell_size + 70))
        return

    # Normal UI display
    ui_lines = [
        f"Selected Tower: {data['selected_tower']}",
        f"Wave: {data['current_wave']}",
        f"Coins: {data['coins']}",
        f"Towers placed: {len(data['towers'])}",
    ]
    available = [str(t) for t in data["available_towers"]]
    locked = [str(t) for t in range(1, 4) if t not in data["available_towers"]]
    ui_lines.append("Available Towers: " + ",".join(available))
    ui_lines.append("Locked Towers: " + ",".join(locked))

    for i, line in enumerate(ui_lines):
        screen.blit(font.render(line, True, BLACK), (10, rows * cell_size + 10 + i * 20))

    if data["game_started"] and data.get("start_time"):
        screen.blit(font.render(f"Time: {int(time.time() - data['start_time'])}", True, BLACK),
                    (window_width - 150, rows * cell_size + 10))

def draw_game_over():
    """
    Displays a GAME OVER overlay if the game is over.
    """
    data = game.get_game_data()
    if data["game_over"]:
        font = pygame.font.SysFont(None, 72)
        text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(window_width // 2, window_height // 2))
        screen.blit(text, text_rect)

def process_key(event):
    if game.get_game_data()["game_over"]:
        return

    # Numeric keys for tower selection.
    if event.type == pygame.KEYDOWN and event.unicode in '123':
        tower_choice = int(event.unicode)
        data = game.get_game_data()
        if tower_choice in data["available_towers"]:
            game.env.selected_tower = tower_choice
        else:
            print("Tower locked for current wave")
    elif event.type == pygame.KEYDOWN:
        action = None
        if event.key == pygame.K_w:
            action = 'UP'
        elif event.key == pygame.K_s:
            action = 'DOWN'
        elif event.key == pygame.K_a:
            action = 'LEFT'
        elif event.key == pygame.K_d:
            action = 'RIGHT'
        elif event.key == pygame.K_p:
            if not game.get_game_data()["game_started"]:
                action = 'PLACE_TOWER'
        elif event.key == pygame.K_v:
            if not game.get_game_data()["game_started"]:
                action = 'START_WAVE'
                for idx, enemy in enumerate(game.env.enemies):
                    enemy['x'] = cols - 1 + idx * 2
                game.env.start_time = time.time()
        if action:
            print("[DEBUG] Action detected:", action)
            game.env.step(action)


def refresh():
    screen.fill(WHITE)
    # Only spawn enemies if the wave is active
    if game.get_game_data()["game_started"]:
        game.spawn_enemies()
    draw_grid()
    draw_ui()
    draw_game_over()
    pygame.display.flip()


clock = pygame.time.Clock()
running = True
agent_mode = True  # Set to True to activate RL agent
agent_timer = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not agent_mode:
            process_key(event)  # Allow manual control only if not agent_mode

    # AGENT ACTION
    if agent_mode and not game.get_game_data()["game_over"]:
        agent_timer += clock.get_time()
        if agent_timer >= 1500:  # Agent acts every 1.5 seconds
            action_to_do = game.q_learning_step()
            agent_timer = 0

            # Debug: print towers after each action
            print("Towers on the map:", game.get_game_data()["towers"])

            game.env.step(action_to_do)

    refresh()
    clock.tick(5)  # Maintain 10 FPS