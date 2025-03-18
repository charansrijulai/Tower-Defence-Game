from test_gym_new import TowerDefenseEnv
class GameController:
    def __init__(self):
        self.env = TowerDefenseEnv()
        self.current_observation, _, _, _ = self.env.reset()
    
    def step(self, action):
       
        observation, reward, done, info = self.env.step(action)
        self.current_observation = observation
        return observation, reward, done, info
    
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
    
    def reset(self):
        self.current_observation, _, _, _ = self.env.reset()
        return self.current_observation
    
    def close(self):
        self.env.close()
