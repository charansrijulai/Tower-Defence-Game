import time

import gym
from gym import spaces
import random
import numpy as np


class TowerDefenseEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        super(TowerDefenseEnv, self).__init__()
        # self.rows, self.cols = 7, 15
        self.rows, self.cols = 7, 7
        self.path_row = 3
        self.max_waves = 5  # Increased max waves for multiple waves.
        self.current_wave = 1
        self.available_towers = [1]
        self.selected_tower = 1
        self.max_enemies = 4
        self.coins = 70
        self.wave_ready = False
        self.enemy_count = 0
        self.game_started = False
        self.game_over = False
        self.game_running = False
        self.allow_tower_placement = True  # Initialized here.
        self.towers = {}  # Towers are stored as a dictionary with keys (row, col)
        self.enemies = []

        self.tower_info = {
            # 1: {'color': (0, 255, 0), 'health': 20, 'damage': 2, 'range': 2, 'cost': 15},
            1: {'color': (0, 255, 0), 'health': 20, 'damage': 10, 'range': 2, 'cost': 15},
            # 2: {'color': (0, 0, 255), 'health': 30, 'damage': 3, 'range': 3, 'cost': 20},
            2: {'color': (0, 0, 255), 'health': 25, 'damage': 15, 'range': 3, 'cost': 20},
            # 3: {'color': (255, 255, 0), 'health': 40, 'damage': 4, 'range': 4, 'cost': 25}
            3: {'color': (255, 255, 0), 'health': 30, 'damage': 20, 'range': 3, 'cost': 25}
        }

        self.enemy_info = {
            # 0: {'color': (0, 128, 128), 'health': 10, 'damage': 1, 'range': 1},
            0: {'color': (0, 128, 128), 'health': 10, 'damage': 10, 'range': 1},
            # 1: {'color': (128, 0, 0), 'health': 20, 'damage': 2, 'range': 2}
            1: {'color': (128, 0, 0), 'health': 20, 'damage': 13, 'range': 2}
        }

        self.rewards = {
            'tower_placed_success': 10,
            'tower_placed_fail': -10,
            'wave_won': 1000,
            # 'wave_lost': -1000,
            'wave_lost': -5000,
            'game_won': 5000,
        }

        # self.actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'SWITCH_TOWER', 'PLACE_TOWER', 'START_WAVE']
        self.actions = ['UP', 'DOWN', 'LEFT', 'RIGHT', 'PLACE_TOWER', 'START_WAVE']
        self.action_space = spaces.Discrete(len(self.actions))

        self.observation_space = spaces.Dict({
            'current_position': spaces.Tuple((spaces.Discrete(self.rows), spaces.Discrete(self.cols))),
            # 'current_selected_tower': spaces.Discrete(len(self.tower_info))
            'current_selected_tower': spaces.Discrete(len(self.tower_info) + 1)
        })

        self.reset()

    def reset(self):
        self.towers = {}  # Towers are stored as a dictionary with keys (row, col)
        self.enemies = []
        self.selected_tower = 1
        # self.player_pos = [0, 0]
        self.player_pos = [random.randint(0, self.rows - 1), random.randint(0, self.cols - 1)]  # CHANGE HERE
        self.current_wave = 1
        self.wave_ready = False
        self.enemy_count = 0
        self.max_enemies = 4
        self.allow_tower_placement = True
        self.game_started = False
        self.game_over = False
        self.game_running = False
        self.available_towers = [1]  # Reset tower availability
        self.coins = 70

        return self.get_observation(), 0, False, {}

    def get_observation(self):
        return {
            'current_position': tuple(self.player_pos),
            'current_selected_tower': self.selected_tower
        }

    def is_terminal(self):
        if self.game_over:
            return 'game_over'
        elif self.current_wave > self.max_waves:
            return 'game_won'
        else:
            return "game_running"

    def step(self, action):
        if isinstance(action, str):
            action = self.actions.index(action)

        action_name = self.actions[action]
        # print(f'action: {action_name}')
        result, reward = self.play_turn(action_name)

        if action_name == 'START_WAVE':
            if not self.wave_ready:
                reward -= 500
            else:
                self.wave_ready = False

        info = {'result': result, 'action': action_name}
        done = False
        terminal_state = self.is_terminal()
        # if action_name == 'START_WAVE':
        # print(terminal_state)
        if terminal_state == 'game_won':
            done = True
            # reward += self.rewards['wave_won']
        elif terminal_state == 'game_over':
            done = True
            # reward += self.rewards['wave_lost']
        else:
            done = False

        obs = self.get_observation()
        # print(f'obs: {obs} | reward: {reward} | done: {done} | info: {info}')

        return obs, reward, done, info

    def move_cursor(self, action):
        x, y = self.player_pos
        moves = {'UP': (-1, 0), 'DOWN': (1, 0), 'LEFT': (0, -1), 'RIGHT': (0, 1)}
        if action in moves:
            dx, dy = moves[action]
            new_x, new_y = x + dx, y + dy
            if 0 <= new_x < self.rows and 0 <= new_y < self.cols:
                self.player_pos = [new_x, new_y]
                return f"Moved {action}!", 0
            return "Out of bounds!", -1

    def switch_tower(self):
        idx = self.available_towers.index(self.selected_tower)
        self.selected_tower = self.available_towers[(idx + 1) % len(self.available_towers)]
        return f"Switched to Tower {self.selected_tower}", 0

    def move_cursor_to_random_adjacent(self):
        """Move cursor to a random adjacent cell without going out of bounds"""
        x, y = self.player_pos
        directions = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]

        # Filter out-of-bounds positions
        adjacent_positions = [
            pos for pos in directions
            if 0 <= pos[0] < self.rows and 0 <= pos[1] < self.cols
        ]
        # Move player to a random adjacent position
        if adjacent_positions:
            self.player_pos = random.choice(adjacent_positions)

    def place_tower(self):
        # CHANGE HERE 1 - start
        if self.allow_tower_placement == False:
            return "Cant place tower because wave in progress", 0
        # CHANGE HERE 1 - end
        if np.random.rand() < 0.5 and self.current_wave > 1:
            self.switch_tower()
        pos = tuple(self.player_pos)
        if pos in self.towers:
            # print("check1")
            self.move_cursor_to_random_adjacent()
            # return "Tower already placed here, moved to adjacent cell!", self.rewards['tower_placed_fail']
            return "Tower already placed here, moved to adjacent cell!", 0
        if pos[0] == self.path_row:
            # print("check2")
            self.move_cursor_to_random_adjacent()
            # return "Cannot place on enemy path, moved to adjacent cell!", self.rewards['tower_placed_fail']
            return "Cannot place on enemy path, moved to adjacent cell!", 0
        cost = self.tower_info[self.selected_tower]['cost']
        if self.coins < cost:
            return self.start_wave()
            # self.move_cursor_to_random_adjacent()
            # return "Not enough coins, moved to adjacent cell!", self.rewards['tower_placed_fail']

        self.wave_ready = True
        self.coins -= cost
        self.towers[pos] = {'type': self.selected_tower, 'health': self.tower_info[self.selected_tower]['health']}
        self.move_cursor_to_random_adjacent()
        return "Tower placed and moved to adjacent cell!", self.rewards['tower_placed_success']

    def start_wave(self):
        # CHANGE HERE 2 - start
        self.allow_tower_placement = False
        # CHANGE HERE 2 - end
        # Removed tower-check so the wave always starts.
        self.game_started = True
        self.game_running = True
        temp_wave = self.current_wave
        while self.game_started:
            self.spawn_enemies()
        self.move_cursor_to_random_adjacent()  # CHANGE HERE
        # print(self.current_wave)
        # print('TERMINAL', self.is_terminal())
        self.end_wave(not self.game_over)
        rew = None

        if self.is_terminal() == 'game_won':
            # print(f'GAME_WON - current_wave: {self.current_wave}, max_waves: {self.max_waves}')
            # print(f'game_over: {self.game_over} | game_started: {self.game_started} | allow_tower_placement: {self.allow_tower_placement}')
            # rew = self.max_waves*self.rewards['wave_won']
            rew = self.rewards['game_won']
        elif self.is_terminal() == 'game_running' and self.current_wave == (temp_wave + 1):
            # print(f'WAVE_WON')
            rew = self.rewards['wave_won']
        else:
            rew = self.rewards['wave_lost']
            # print(f'GAME_LOST - current_wave: {self.current_wave}, max_waves: {self.max_waves}')
            # print(f'game_over: {self.game_over} | game_started: {self.game_started} | allow_tower_placement: {self.allow_tower_placement}')
        return "Wave started!", rew

    def spawn_enemies(self):
        """Generates enemies based on the current wave number."""
        # num_enemies = self.current_wave * 2
        # self.enemy_count = num_enemies
        # self.enemies = []
        # for _ in range(num_enemies):
        #     enemy_type = random.choice(list(self.enemy_info.keys()))
        #     enemy = {
        #         'type': enemy_type,
        #         'health': 10 + self.current_wave * 2,
        #         'x': self.cols  # Starting at the rightmost column.
        #     }
        #     self.enemies.append(enemy)
        self.update_enemies()
        return "Enemies spawned!"

    def resolve_combat(self):
        towers_to_remove = []
        enemies_to_remove = []
        for tower_pos, tower in self.towers.items():
            tower_row, tower_col = tower_pos
            tower_range = self.tower_info[tower['type']]['range']
            tower_damage = self.tower_info[tower['type']]['damage']
            for enemy in self.enemies:
                enemy_x = enemy.get('x', self.cols)
                enemy_row = self.path_row  # Enemies move along this row
                distance = abs(tower_row - enemy_row) + abs(tower_col - enemy_x)
                # Tower attacks enemy if within range.
                if distance <= tower_range:
                    enemy['health'] -= tower_damage
                    if enemy['health'] <= 0 and enemy not in enemies_to_remove:
                        enemies_to_remove.append(enemy)
                # Enemy counterattacks if within its range.
                enemy_range = self.enemy_info[enemy['type']]['range']
                enemy_damage = self.enemy_info[enemy['type']]['damage']
                if distance <= enemy_range:
                    tower['health'] -= enemy_damage
                    if tower['health'] <= 0 and tower_pos not in towers_to_remove:
                        towers_to_remove.append(tower_pos)
        for pos in towers_to_remove:
            if pos in self.towers:
                del self.towers[pos]
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

    def update_enemies(self):
        """
        Updates enemy positions and resolves combat.
        Moves each live enemy one cell to the left.
        If any live enemy reaches x < 0, the game is marked as over.
        If no enemies remain while the wave is active, the wave is ended.
        """
        # # First, resolve combat.
        # self.resolve_combat()
        # # Then move enemies.
        # for enemy in self.enemies[:]:
        #     if enemy['health'] > 0:
        #         enemy['x'] -= 1
        #         if enemy['x'] < 0:
        #             self.game_over = True
        #             break
        #     else:
        #         if enemy in self.enemies:
        #             self.enemies.remove(enemy)
        # # If the wave is active and all enemies have been cleared, end the wave.
        # if self.game_started and len(self.enemies) == 0 and not self.game_over:
        #     self.current_wave += 1
        #     # If we've exceeded max waves, game is won.
        #     if self.current_wave >= self.max_waves:
        #         self.game_over = True
        #     else:
        #         self.max_enemies = 10 + (self.current_wave - 1) * 5
        #         self.coins += self.current_wave * 20
        #         self.allow_tower_placement = True
        #         self.game_started = False
        # print(self.enemies)
        # print(self.towers)
        if self.is_terminal() == 'game_won':
            # print('check')
            self.game_started = False
            return

        for enemy in self.enemies:
            if enemy['x'] == 0:
                self.game_started = False
                self.allow_tower_placement = True
                self.game_over = True
                return

        # if self.enemy_count < 10:
        #     print(self.enemy_count, self.max_enemies)

        if self.enemy_count < self.max_enemies:
            # print('enemies')
            allowed_enemy_max = len(self.enemy_info)
            enemy_type = random.randint(1, allowed_enemy_max)
            if self.current_wave == 1:
                enemy_type = 1
            self.resolve_combat()
            for enemy in self.enemies:
                # print('check')
                enemy['x'] -= 1
            self.enemies.append(
                {'x': self.cols - 1, 'type': enemy_type - 1, 'health': self.enemy_info[enemy_type - 1]['health'],
                 'color': self.enemy_info[enemy_type - 1]['color']})
            self.enemy_count += 1
        else:
            self.resolve_combat()
            for enemy in self.enemies:
                # print('check')
                enemy['x'] -= 1

        self.enemies[:] = [enemy for enemy in self.enemies if enemy['health'] > 0]

        if self.enemy_count >= self.max_enemies and len(self.enemies) == 0:
            # self.wave_number += 1
            self.current_wave += 1
            self.enemy_count = 0
            # self.max_enemies = 10 + (self.wave_number - 1) * 5  # 10, 15, 20, 25, 30, 35 ......
            # self.max_enemies = self.wave_number + (self.wave_number - 1) * 5  # 10, 15, 20, 25, 30, 35 ......
            # self.max_enemies = self.current_wave + (self.current_wave - 1) * 5  # 10, 15, 20, 25, 30, 35 ......
            self.coins += self.current_wave * 15
            self.allow_tower_placement = True
            self.game_started = False

    def end_wave(self, won):
        """Handles the end of a wave, unlocking new towers and progressing to the next wave."""
        if won:
            # self.coins += 50
            # self.current_wave += 1
            if self.current_wave == 2:
                self.available_towers.append(2)
            if self.current_wave == 3:
                self.available_towers.append(3)
        #     if self.current_wave > self.max_waves:
        #         self.game_over = True
        #         return "Game Won!", self.rewards['wave_won']
        #     return "Wave won! Next wave starts soon.", self.rewards['wave_won']
        # else:
        #     self.game_over = True
        #     return "Game Over! You lost.", self.rewards['wave_lost']

    def play_turn(self, action):
        if action in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            return self.move_cursor(action)
        # elif action == 'SWITCH_TOWER':
        #     return self.switch_tower()
        elif action == 'PLACE_TOWER':
            return self.place_tower()
        elif action == 'START_WAVE':
            return self.start_wave()
        return "Invalid action!", 0

    def render(self, mode='human'):
        print(
            f"Player Position: {self.player_pos}, Coins: {self.coins}, Towers: {len(self.towers)}, Wave: {self.current_wave}")

    def close(self):
        pass