import pygame
import sys
from tdg_controller import GameController

# Setup
game = GameController(algo='ql')
observation = game.reset()
data = game.get_game_data()
rows, cols = data["rows"], data["cols"]
path_row = data["path_row"]
cell_size = 75
window_width = cols * cell_size
window_height = rows * cell_size + 150

# Colors
GREEN = (34, 139, 34)
GREY = (169, 169, 169)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Tower Defense Game - Animated')

# Assets
tower_images = {
    1: pygame.image.load("../images/watchtower.png").convert_alpha(),
    2: pygame.image.load("../images/watchtower_lvl2.png").convert_alpha(),
    3: pygame.image.load("../images/watchtower_lvl3.png").convert_alpha()
}
enemy_images = {
    0: pygame.image.load("../images/goblinsword.png").convert_alpha(),
    1: pygame.image.load("../images/orc_hig.png").convert_alpha()
}
for key in tower_images:
    tower_images[key] = pygame.transform.scale(tower_images[key], (cell_size, cell_size))
for key in enemy_images:
    enemy_images[key] = pygame.transform.scale(enemy_images[key], (cell_size, cell_size))

grass_tile = pygame.transform.scale(pygame.image.load("../images/grass.png").convert_alpha(), (cell_size, cell_size))
path_tile = pygame.transform.scale(pygame.image.load("../images/cobblestone.png").convert_alpha(), (cell_size, cell_size))

# State
projectiles = []
enemy_projectiles = []
tower_spawn_time = {}
tower_last_fired = {}
enemy_last_fired = {}
fire_delay = 600
enemy_flash = {}
enemy_shrink = {}
last_spawn_time = 0
spawn_delay = 1000
show_cursor = True
selected_tower = 1  # Synced tower selection

# Classes
class EnemyProjectile:
    def __init__(self, start, tower):
        self.x, self.y = start
        self.tx = tower[1] * cell_size + cell_size // 2
        self.ty = tower[0] * cell_size + cell_size // 2
        self.speed = 10
        self.active = True

    def update(self):
        dx, dy = self.tx - self.x, self.ty - self.y
        dist = (dx**2 + dy**2)**0.5
        if dist < self.speed:
            self.active = False
            return
        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed

    def draw(self):
        pygame.draw.circle(screen, (139, 0, 0), (int(self.x), int(self.y)), 6)

class Projectile:
    def __init__(self, start, enemy):
        self.x, self.y = start
        self.tx = enemy['x'] * cell_size + cell_size // 2
        self.ty = path_row * cell_size + cell_size // 2
        self.target = enemy
        self.speed = 10
        self.active = True

    def update(self):
        dx, dy = self.tx - self.x, self.ty - self.y
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist < self.speed:
            self.active = False
            enemy_flash[(self.target['x'] * cell_size, self.target['type'])] = 3
            return
        self.x += dx / dist * self.speed
        self.y += dy / dist * self.speed

    def draw(self):
        pygame.draw.circle(screen, (255, 215, 0), (int(self.x), int(self.y)), 6)

# Drawing
def draw_health_bar(x, y, current_health, max_health, width, height):
    pygame.draw.rect(screen, (255, 0, 0), (x, y, width, height))
    health_ratio = current_health / max_health if max_health > 0 else 0
    pygame.draw.rect(screen, (0, 255, 0), (x, y, int(width * health_ratio), height))

def draw_grid():
    data = game.get_game_data()
    towers = data["towers"]
    enemies = data["enemies"]
    player_pos = data["player_pos"]
    tower_info = data["tower_info"]
    enemy_info = data["enemy_info"]

    for row in range(rows):
        for col in range(cols):
            tile = path_tile if row == path_row else grass_tile
            screen.blit(tile, (col * cell_size, row * cell_size))
            pygame.draw.rect(screen, BLACK, (col * cell_size, row * cell_size, cell_size, cell_size), 1)

    now = pygame.time.get_ticks()

    for pos, tower in towers.items():
        x, y = pos[1] * cell_size, pos[0] * cell_size
        tower_type = tower['type']
        spawn_time = tower_spawn_time.get(pos, now)
        tower_spawn_time[pos] = spawn_time
        scale = min(1.0, (now - spawn_time) / 300)
        img = pygame.transform.scale(tower_images[tower_type], (int(cell_size * scale), int(cell_size * scale)))
        img_rect = img.get_rect(center=(x + cell_size // 2, y + cell_size // 2))
        screen.blit(img, img_rect)
        draw_health_bar(x, y + cell_size - 8, tower['health'], tower_info[tower_type]['health'], cell_size, 5)

    for enemy in enemies:
        ex = enemy['x'] * cell_size
        ey = path_row * cell_size
        etype = enemy['type']
        health = enemy['health']
        max_health = enemy_info[etype]['health']
        key = (ex, etype)
        if health <= 0:
            enemy_shrink[key] = enemy_shrink.get(key, 1.0) - 0.05
            scale = max(enemy_shrink[key], 0.1)
            img = pygame.transform.scale(enemy_images[etype], (int(cell_size * scale), int(cell_size * scale)))
        elif key in enemy_flash:
            img = pygame.Surface((cell_size, cell_size))
            img.fill((255, 255, 255))
            enemy_flash[key] -= 1
            if enemy_flash[key] <= 0:
                del enemy_flash[key]
        else:
            img = enemy_images[etype]
        screen.blit(img, (ex, ey))
        draw_health_bar(ex, ey + cell_size - 8, health, max_health, cell_size, 5)

    # Draw cursor
    if show_cursor:
        pos = tuple(player_pos)
        valid_tile = pos not in towers and player_pos[0] != path_row
        hover_img = tower_images[selected_tower].copy()
        hover_img.set_alpha(150)
        if not valid_tile:
            red_overlay = pygame.Surface((cell_size, cell_size), pygame.SRCALPHA)
            red_overlay.fill((255, 0, 0, 100))
            hover_img.blit(red_overlay, (0, 0))
        screen.blit(hover_img, (player_pos[1] * cell_size, player_pos[0] * cell_size))
        pygame.draw.rect(screen, WHITE, (player_pos[1] * cell_size, player_pos[0] * cell_size, cell_size, cell_size), 2)
        range_radius = tower_info[selected_tower]['range'] * cell_size
        center_x = player_pos[1] * cell_size + cell_size // 2
        center_y = player_pos[0] * cell_size + cell_size // 2
        pygame.draw.circle(screen, (255, 215, 0), (center_x, center_y), range_radius, 2)

    for proj in projectiles:
        proj.update()
        proj.draw()
    projectiles[:] = [p for p in projectiles if p.active]

    for ep in enemy_projectiles:
        ep.update()
        ep.draw()
    enemy_projectiles[:] = [ep for ep in enemy_projectiles if ep.active]


def draw_ui():
    data = game.get_game_data()
    ui_top = rows * cell_size
    ui_height = 200

    panel_color = (245, 245, 245)
    pygame.draw.rect(screen, panel_color, (0, ui_top, window_width, ui_height))

    title_font = pygame.font.SysFont("arial", 28, bold=True)
    label_font = pygame.font.SysFont("arial", 22)
    value_font = pygame.font.SysFont("arial", 22, bold=True)
    small_font = pygame.font.SysFont("arial", 18)

    def draw_label_value(label, value, x, y):
        label_surface = label_font.render(label, True, (50, 50, 50))
        value_surface = value_font.render(str(value), True, (0, 102, 204))
        screen.blit(label_surface, (x, y))
        screen.blit(value_surface, (x + 180, y))

    x_pad = 20
    y_pad = ui_top + 10
    line_gap = 26

    if data["game_over"] or data["current_wave"] > game.env.max_waves:
        msg = "GAME WON!!" if data["current_wave"] > game.env.max_waves else "GAME OVER !!"
        text = title_font.render(msg, True, (200, 0, 0))
        screen.blit(text, (window_width // 2 - 100, y_pad + 20))
        return

    # Info
    draw_label_value("Selected Tower:", selected_tower, x_pad, y_pad)
    draw_label_value("Wave:", f"{data['current_wave']} / {game.env.max_waves}", x_pad, y_pad + line_gap)
    draw_label_value("Coins:", data['coins'], x_pad, y_pad + 2 * line_gap)
    draw_label_value("Towers placed:", len(data['towers']), x_pad, y_pad + 3 * line_gap)

    # Controls
    control_x = window_width // 2 + 50
    control_y = y_pad
    screen.blit(label_font.render("Controls", True, (60, 60, 60)), (control_x, control_y))

    controls = [
        "W / A / S / D  : Move Cursor",
        "1 / 2 / 3      : Select Tower",
        "P              : Place Tower",
        "V              : Start Wave",
    ]
    for i, line in enumerate(controls):
        screen.blit(small_font.render(line, True, (30, 30, 30)), (control_x, control_y + 25 + i * 20))


# Game refresh
def refresh():
    global last_spawn_time, show_cursor
    screen.fill(WHITE)
    now = pygame.time.get_ticks()
    data = game.get_game_data()
    show_cursor = not data["game_started"]
    if data["game_started"] and now - last_spawn_time > spawn_delay:
        game.spawn_enemies()
        last_spawn_time = now

    for pos, tower in data["towers"].items():
        tower_type = tower['type']
        tower_range = data["tower_info"][tower_type]['range']
        tx, ty = pos[1], pos[0]
        last_fired = tower_last_fired.get(pos, 0)
        if now - last_fired < fire_delay:
            continue
        for enemy in data["enemies"]:
            ex = enemy.get('x', cols - 1)
            dist = abs(ty - path_row) + abs(tx - ex)
            if dist <= tower_range:
                start = (tx * cell_size + cell_size // 2, ty * cell_size + cell_size // 2)
                projectiles.append(Projectile(start, enemy))
                tower_last_fired[pos] = now
                break

    for enemy in data["enemies"]:
        ex = enemy['x']
        key = (ex, enemy['type'])
        last_fired = enemy_last_fired.get(key, 0)
        if now - last_fired < fire_delay:
            continue
        for tower_pos in data["towers"]:
            tx, ty = tower_pos[1], tower_pos[0]
            if abs(ty - path_row) + abs(tx - ex) <= 3:
                start = (ex * cell_size + cell_size // 2, path_row * cell_size + cell_size // 2)
                enemy_projectiles.append(EnemyProjectile(start, tower_pos))
                enemy_last_fired[key] = now
                break

    draw_grid()
    draw_ui()
    pygame.display.flip()

# Key processing
def process_key(event):
    global selected_tower
    data = game.get_game_data()
    if data["game_started"] or data["game_over"]:
        return
    if event.type == pygame.KEYDOWN:
        if event.unicode in '123':
            tower = int(event.unicode)
            if tower in data["available_towers"]:
                selected_tower = tower
                game.env.selected_tower = tower
        else:
            key_map = {
                pygame.K_w: 'UP', pygame.K_s: 'DOWN', pygame.K_a: 'LEFT', pygame.K_d: 'RIGHT',
                pygame.K_p: 'PLACE_TOWER', pygame.K_v: 'START_WAVE'
            }
            action = key_map.get(event.key)
            if action:
                game.env.step(action)

# Main loop
clock = pygame.time.Clock()
running = True
agent_mode = False
agent_timer = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not agent_mode:
            process_key(event)

    if agent_mode and not game.get_game_data()["game_over"]:
        agent_timer += clock.get_time()
        if agent_timer >= 1200:
            game.env.step(game.q_learning_step())
            agent_timer = 0

    refresh()
    clock.tick(60)

pygame.quit()
sys.exit()
