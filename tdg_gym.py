import gym
from gym import spaces
import pygame
import sys
import random
import time
import numpy as np

# ----- Global Game Parameters -----
width, height = 800, 450
cell_size = 32
rows, cols = 10, 25
path_row = 5
max_waves = 10  # Total number of waves in the game

# Colors
GREEN = (34, 139, 34)
GREY = (169, 169, 169)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
UI_BG = (200, 200, 200)

# Tower and Enemy definitions
tower_info = {
    0: {'color': (255, 0, 0),   'health': 10, 'damage': 1, 'range': 1, 'cost': 10},
    1: {'color': (0, 255, 0),   'health': 20, 'damage': 2, 'range': 2, 'cost': 15},
    2: {'color': (0, 0, 255),   'health': 30, 'damage': 3, 'range': 3, 'cost': 20},
    3: {'color': (255, 255, 0), 'health': 40, 'damage': 4, 'range': 4, 'cost': 25},
    4: {'color': (255, 165, 0), 'health': 50, 'damage': 5, 'range': 5, 'cost': 30},
    5: {'color': (128, 0, 128), 'health': 60, 'damage': 6, 'range': 6, 'cost': 35}
}
enemy_info = {
    0: {'color': (0, 128, 128), 'health': 10, 'damage': 1, 'range': 1},
    1: {'color': (128, 0, 0),   'health': 20, 'damage': 2, 'range': 2},
    2: {'color': (0, 128, 0),   'health': 30, 'damage': 3, 'range': 3},
    3: {'color': (128, 128, 0), 'health': 40, 'damage': 4, 'range': 4},
    4: {'color': (0, 0, 128),   'health': 50, 'damage': 5, 'range': 5},
    5: {'color': (128, 0, 128), 'health': 60, 'damage': 6, 'range': 6}
}

# ----- Gym Environment Wrapper -----
class TowerDefenseEnv(gym.Env):
    metadata = {'render.modes': ['human']}
    
    def __init__(self):
        super(TowerDefenseEnv, self).__init__()
        # pygame.init()
        # self.screen = pygame.display.set_mode((width, height))
        # pygame.display.set_caption('Tower Defense - Gym Env')
        # self.width, self.height = 800, 450
        self.rows, self.cols = 10, 25
        self.path_row = 5
        self.max_waves = 10  # Total number of waves in the game
        self.tower_info = {
            0: {'color': (255, 0, 0),   'health': 10, 'damage': 1, 'range': 1, 'cost': 10},
            1: {'color': (0, 255, 0),   'health': 20, 'damage': 2, 'range': 2, 'cost': 15},
            2: {'color': (0, 0, 255),   'health': 30, 'damage': 3, 'range': 3, 'cost': 20},
            3: {'color': (255, 255, 0), 'health': 40, 'damage': 4, 'range': 4, 'cost': 25},
            4: {'color': (255, 165, 0), 'health': 50, 'damage': 5, 'range': 5, 'cost': 30},
            5: {'color': (128, 0, 128), 'health': 60, 'damage': 6, 'range': 6, 'cost': 35}
        }
        self.enemy_info = {
            0: {'color': (0, 128, 128), 'health': 10, 'damage': 1, 'range': 1},
            1: {'color': (128, 0, 0),   'health': 20, 'damage': 2, 'range': 2},
            2: {'color': (0, 128, 0),   'health': 30, 'damage': 3, 'range': 3},
            3: {'color': (128, 128, 0), 'health': 40, 'damage': 4, 'range': 4},
            4: {'color': (0, 0, 128),   'health': 50, 'damage': 5, 'range': 5},
            5: {'color': (128, 0, 128), 'health': 60, 'damage': 6, 'range': 6}
        }
        self.rewards = {
            'tower_placed_success': 10,
            'tower_placed_fail_insuffienct_coins': -10,
            'tower_placed_fail_placement_on_path': -10,
            'wave_won': 1000,
            'wave_lost': -1000,
        }
        self.actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'TOWER_1', 'TOWER_2', 'TOWER_3', 'TOWER_4', 'TOWER_5', 'TOWER_6',
                        'PLACE_TOWER', 'START_WAVE']
        self.action_space = spaces.Discrete(len(self.actions))

        obs_space_dict = {
            'current_position': spaces.Tuple((spaces.Discrete(self.rows), spaces.Discrete(self.cols))),
            'current_selected_tower': spaces.Discrete(len(self.tower_info)),
            'remaining_coins': spaces.Discrete(np.inf)  # None is not directly representable, so we use Discrete(len(tower_info))
            # 'player_position': spaces.Tuple((spaces.Discrete(self.grid_size), spaces.Discrete(self.grid_size))),
            # 'player_health': spaces.Discrete(len(self.health_states)),
            # 'guard_positions': spaces.Dict({
            #     guard: spaces.Tuple((spaces.Discrete(self.grid_size), spaces.Discrete(self.grid_size)))
            #     for guard in self.guards
            # })
        }
        self.observation_space = spaces.Dict(obs_space_dict)

        # Set initial state
        # self.reset()
        
        # Observation: grid image (rows x cols x 3 RGB)
        # self.observation_space = spaces.Box(low=0, high=255, shape=(rows, cols, 3), dtype=np.uint8)
        # Action space: Discrete actions: 
        # 0: up, 1: down, 2: left, 3: right, 4: place tower, 5: start wave
        # self.action_space = spaces.Discrete(6)
        
        self.clock = pygame.time.Clock()
        self.reset()

    # def is_valid_position_to_place(self, position):
    #     pass
        
    def reset(self):
        self.towers = {}           # Towers stored by (col, row): {'type': int, 'health': int}
        self.enemies = []          # Enemies stored as dicts; enemy positions as floats
        self.selected_tower = None
        self.wave_number = 1
        self.player_pos = [0, 0]
        self.coins = 100
        self.enemy_count = 0
        self.max_enemies = 10      # Always 10 enemies per wave.
        self.allow_tower_placement = True
        self.game_started = False
        self.game_over = False
        self.enemy_won = False     # Flag to indicate enemy reached end.
        self.agent_won = False     # Flag to indicate agent survived all waves.
        self.start_time = None     # Time when wave starts
        # self.last_spawn_time = None  # For enemy spawn timing
        # self.last_update_time = time.time()  # For dt calculation
        self.current_state = {
            'current_position': (0, 0),
            'current_selected_tower': None,
            'remaining_coins': 100
        }
        # Return obs, rew, done, info
        return self._get_observation(), 0, False, {}
    
    def _get_observation(self):
        # obs = np.zeros((rows, cols, 3), dtype=np.uint8)
        # for r in range(rows):
        #     for c in range(cols):
        #         if (c, r) in self.towers:
        #             obs[r, c] = np.array(tower_info[self.towers[(c, r)]['type']]['color'])
        #         else:
        #             obs[r, c] = np.array(GREY if r == path_row else GREEN)
        obs = {
            'current_position': self.current_state['current_position'],
            'current_selected_tower': self.current_state['current_selected_tower'],
            'remaining_coins': self.current_state['remaining_coins']
        }
        return obs
    
    def is_terminal(self):
        if self.wave_number == max_waves:
            return True
        elif self.game_over:
            return True
        return False
    
    def step(self, action):
        reward = 0
        done = False
        info = {}
        
        # Process discrete actions:
        # 0: up, 1: down, 2: left, 3: right, 4: place tower, 5: start wave
        if action == 0 and self.player_pos[1] > 0:
            self.player_pos[1] -= 1
        elif action == 1 and self.player_pos[1] < rows - 1:
            self.player_pos[1] += 1
        elif action == 2 and self.player_pos[0] > 0:
            self.player_pos[0] -= 1
        elif action == 3 and self.player_pos[0] < cols - 1:
            self.player_pos[0] += 1
        elif action == 4:
            # Place tower (only allowed during placement phase and not on enemy path)
            if self.allow_tower_placement and tuple(self.player_pos) not in self.towers and self.player_pos[1] != path_row:
                cost = tower_info[0]['cost']  # Using tower type 0 for simplicity
                if self.coins >= cost:
                    self.coins -= cost
                    self.towers[tuple(self.player_pos)] = {'type': 0, 'health': tower_info[0]['health']}
                    reward += 1
                else:
                    reward -= 1
        elif action == 5:
            if not self.game_started:
                self.allow_tower_placement = False
                self.game_started = True
                self.start_time = time.time()
                self.last_spawn_time = self.start_time
        
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        if self.game_started:
            self._update_enemies(dt)
        
        # Check for end-of-game conditions:
        # If any enemy reaches the left edge, game over (enemy wins)
        if self.enemy_won:
            done = True
        # If agent completes all waves, agent wins.
        if self.wave_number > max_waves and not self.enemy_won:
            self.agent_won = True
            done = True
        
        obs = self._get_observation()
        return obs, reward, done, info
    
    def _update_enemies(self, dt):
        speed = 1.0  # cells per second
        for enemy in self.enemies:
            enemy['x'] -= speed * dt
        
        # Resolve combat between towers and enemies.
        self.resolve_combat()
        
        if self.enemy_count < self.max_enemies:
            if time.time() - self.last_spawn_time >= 1.0:
                allowed_enemy_max = self.wave_number if self.wave_number <= 6 else 6
                enemy_type = random.randint(0, allowed_enemy_max - 1)
                new_enemy = {
                    'x': float(cols),  # Spawn at rightmost cell (as float)
                    'type': enemy_type,
                    'health': enemy_info[enemy_type]['health'],
                    'color': enemy_info[enemy_type]['color']
                }
                self.enemies.append(new_enemy)
                self.enemy_count += 1
                self.last_spawn_time = time.time()
        
        # Check for game over: if any enemy reaches or passes the left edge.
        for enemy in self.enemies:
            if enemy['x'] <= 0:
                self.enemy_won = True
                self.game_over = True
                self.game_started = False
                self.allow_tower_placement = False
                print("Enemy reached the end. GAME OVER!")
                return
        
        # Remove enemies that have moved off-screen (x < 0)
        self.enemies = [enemy for enemy in self.enemies if enemy['x'] >= 0]
        
        # If all 10 enemies have been spawned and none remain, complete the wave.
        if self.enemy_count >= self.max_enemies and len(self.enemies) == 0:
            self.wave_number += 1
            self.enemy_count = 0
            # For this version, max_enemies remains 10 every wave.
            self.coins += self.wave_number * 20
            self.allow_tower_placement = True
            self.game_started = False
            self.start_time = None
    
    def resolve_combat(self):
        enemies_to_remove = []
        towers_to_remove = []
        for (tower_x, tower_y), info in self.towers.items():
            tower_type = info['type']
            tower_range = tower_info[tower_type]['range']
            tower_damage = tower_info[tower_type]['damage']
            for enemy in self.enemies:
                enemy_x, enemy_y = enemy['x'], path_row  # Enemies are on the path_row.
                distance = abs(tower_x - enemy_x) + abs(tower_y - enemy_y)
                if distance <= tower_range:
                    enemy['health'] -= tower_damage  # Tower attacks enemy.
                    if enemy['health'] <= 0:
                        enemies_to_remove.append(enemy)
                if distance <= enemy_info[enemy['type']]['range']:
                    info['health'] -= enemy_info[enemy['type']]['damage']  # Enemy attacks tower.
                    if info['health'] <= 0:
                        towers_to_remove.append((tower_x, tower_y))
        self.enemies = [enemy for enemy in self.enemies if enemy not in enemies_to_remove]
        for tower in towers_to_remove:
            if tower in self.towers:
                del self.towers[tower]
    
    def render(self, mode='human'):
        self.screen.fill(WHITE)
        self._draw_grid()
        self._draw_ui()
        if self.game_over:
            self._draw_game_over()
        pygame.display.flip()
        self.clock.tick(60)
    
    def _draw_grid(self):
        font = pygame.font.SysFont(None, 24)
        for r in range(rows):
            for c in range(cols):
                pos = (c * cell_size, r * cell_size, cell_size, cell_size)
                if (c, r) in self.towers:
                    tower_type = self.towers[(c, r)]['type']
                    tower_color = tower_info[tower_type]['color']
                    pygame.draw.rect(self.screen, tower_color, pos)
                    text = font.render(str(self.towers[(c, r)]['health']), True, BLACK)
                    self.screen.blit(text, (c * cell_size + cell_size // 3, r * cell_size + cell_size // 4))
                else:
                    color = GREY if r == path_row else GREEN
                    pygame.draw.rect(self.screen, color, pos)
                pygame.draw.rect(self.screen, BLACK, pos, 1)
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(int(enemy['x'] * cell_size), path_row * cell_size, cell_size, cell_size)
            pygame.draw.rect(self.screen, enemy['color'], enemy_rect)
            text = font.render(str(int(enemy['health'])), True, WHITE)
            self.screen.blit(text, (enemy_rect.x + cell_size // 3, enemy_rect.y + cell_size // 4))
        pygame.draw.rect(self.screen, WHITE, (self.player_pos[0] * cell_size, self.player_pos[1] * cell_size, cell_size, cell_size), 3)
    
    def _draw_ui(self):
        font = pygame.font.SysFont(None, 36)
        self.screen.blit(font.render(f'Selected Tower: {self.selected_tower if self.selected_tower is not None else "None"}', True, BLACK), (10, rows * cell_size + 10))
        self.screen.blit(font.render(f'Wave: {self.wave_number}', True, BLACK), (300, rows * cell_size + 10))
        self.screen.blit(font.render(f'Coins: {self.coins}', True, BLACK), (425, rows * cell_size + 10))
        if self.game_started and self.start_time:
            self.screen.blit(font.render(f'Time: {int(time.time()-self.start_time)}', True, BLACK), (650, rows * cell_size + 10))
        self.screen.blit(font.render(f'Towers placed: {len(self.towers)}', True, BLACK), (10, rows * cell_size + 50))
        if not self.game_started:
            start_button_rect = pygame.Rect(650, rows * cell_size + 10, 140, 40)
            pygame.draw.rect(self.screen, GREY, start_button_rect)
            button_text = font.render("Start Wave", True, BLACK)
            self.screen.blit(button_text, (start_button_rect.centerx - button_text.get_width() // 2,
                                            start_button_rect.centery - button_text.get_height() // 2))
    
    def _draw_game_over(self):
        font = pygame.font.SysFont(None, 72)
        if self.enemy_won:
            text = font.render("Enemy Won!", True, (255, 0, 0))
        elif self.agent_won:
            text = font.render("Agent Won!", True, (0, 255, 0))
        else:
            text = font.render("GAME OVER", True, (255, 0, 0))
        text_rect = text.get_rect(center=(width // 2, height // 2))
        self.screen.blit(text, text_rect)
    
    def close(self):
        pygame.quit()

if __name__ == '__main__':
    env = TowerDefenseEnv()
    obs = env.reset()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                env.close()
                sys.exit()
        action = env.action_space.sample()  # we replace with the agaent later
        obs, reward, done, info = env.step(action)
        env.render()
        if done:
            # If game is over, check winner condition.
            if env.enemy_won:
                print("Enemy Won!")
            elif env.agent_won:
                print(f"Agent Won! Waves Completed: {max_waves}")
            time.sleep(2)
            break
    env.close()
    sys.exit()
