from test_gym_new import TowerDefenseEnv
import numpy as np
import random
import pickle
import torch
from QNetwork import QNetwork

class GameController:
    def __init__(self, algo='ql'):
        self.algo_used = algo
        self.env = TowerDefenseEnv()

        if algo == 'dqn':
            action_space = self.env.action_space.n
            model = QNetwork(3, action_space)
            model.load_state_dict(torch.load('../train/dqn_tower_defense_model.pth'))
            self.dqn_model = model
        
        self.current_observation, _, _, _ = self.env.reset()

        # Q-Learning setup
        self.num_states = 1000  # Simplified state count
        self.num_actions = self.env.rows * self.env.cols  # One action per grid cell (tower placement)
        if algo == 'ql':
            try:
                with open('../train/Q_table_winning_train_a_lot.pickle', 'rb') as f:
                    self.q_table = pickle.load(f)
                print("Loaded trained Q table successfully!")
            except Exception as e:
                print("Failed to load Q table, initializing a new one.", e)
                self.q_table = np.zeros((self.num_states, self.num_actions))
        self.alpha = 0.1
        self.gamma = 0.95
        self.epsilon = 0

    def encode_state(self):
        """Encode state based on enemies and wave"""
        enemies_count = len(self.env.enemies)
        state = min(enemies_count * 10 + self.env.current_wave, self.num_states - 1)
        return state

    def choose_action(self, state):
        """Epsilon-greedy action selection"""
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        return np.argmax(self.q_table[state])

    def perform_action(self, action):
        row = action // self.env.cols
        col = action % self.env.cols
        msg, reward = self.env.place_tower()
        print(f"[CONTROLLER DEBUG] Agent placing tower at ({row}, {col}): {msg}")
        return reward

    def hash(self, obs):
        x, y = obs['current_position']
        h = obs['current_selected_tower']

        return x * (7 * 3) + y * 3 + h

    def q_learning_step(self):
        if self.algo_used == 'dqn':
            return self.dqn_step()
        obs = self.env.get_observation()
        state = self.hash(obs)
        action = np.argmax(self.q_table[state])

        return action
    
    def dqn_step(self):
        obs = self.env.get_observation()
        state = np.array([obs['current_position'][0], obs['current_position'][1], obs['current_selected_tower']])
        state = torch.tensor(state, dtype=torch.float32)
        q_values = self.dqn_model(state.unsqueeze(0))
        action = torch.argmax(q_values).item()
        return action

    def reset(self):
        self.current_observation, _, _, _ = self.env.reset()
        return self.current_observation

    def spawn_enemies(self):
        self.env.spawn_enemies()

    def get_game_data(self):
        return {
            "towers": self.env.towers,
            "enemies": self.env.enemies,
            "player_pos": self.env.player_pos,
            "selected_tower": self.env.selected_tower,
            "current_wave": self.env.current_wave,
            "coins": self.env.coins,
            "available_towers": self.env.available_towers,
            "game_over": self.env.game_over,
            "game_started": self.env.game_started,
            "start_time": getattr(self.env, "start_time", None),
            "rows": self.env.rows,
            "cols": self.env.cols,
            "path_row": self.env.path_row,
            "tower_info": self.env.tower_info,
            "enemy_info": self.env.enemy_info,
        }

    def close(self):
        self.env.close()
