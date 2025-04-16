import pickle
import numpy as np
from test_gym_train import TowerDefenseEnv

env = TowerDefenseEnv()
def hash(obs):
    x, y = obs['current_position']
    h = obs['current_selected_tower']

    return x * (7 * 3) + y * 3 + h

def Q_learning(num_episodes=10000, gamma=0.9, epsilon=1, decay_rate=0.999):
	Q_table = {i: np.zeros(len(env.actions)) for i in range(148)}
	no_of_updates = {i: np.zeros(len(env.actions)) for i in range(148)}
	temp_dict = {
		1: 0,
		2: 0,
		3: 0,
		4: 0,
		5: 0,
		6: 0,
	}
	for episode in range(num_episodes):
		if episode % 5000 == 0:
			print("epsiode number ",episode)
			print(temp_dict)
		obs, reward, done, info = env.reset()
		state = hash(obs)
		while not done:
			if np.random.rand() < epsilon:
				action = env.action_space.sample()
			else:
				action = np.argmax(Q_table[state])
			eta = 1/(1 + no_of_updates[state][action])
			next_obs, reward, done, info = env.step(action)
			next_state = hash(next_obs)
			Q_table[state][action] = ((1 - eta) * Q_table[state][action] + eta * (reward + (gamma * np.max(Q_table[next_state]))))
			no_of_updates[state][action] += 1
			state = next_state
		temp_dict[env.current_wave] += 1
		epsilon *= decay_rate
	return Q_table

decay_rate = 0.99999993

Q_table = Q_learning(num_episodes=1000000, gamma=0.9, epsilon=1, decay_rate=decay_rate) # Run Q-learning

with open('Q_table.pickle', 'wb') as handle:
    pickle.dump(Q_table, handle, protocol=pickle.HIGHEST_PROTOCOL)

# Q_table = np.load('Q_table.pickle', allow_pickle=True)
#
# obs, reward, done, info = env.reset()
# print(obs, reward, done, info)
# total_reward = 0
# while not done:
# 	state = hash(obs)
# 	print(state)
# 	action = np.argmax(Q_table[state])
# 	print(action)
# 	obs, reward, done, info = env.step(action)
# 	print(obs, reward, done, info)
# 	total_reward += reward
# 	# if gui_flag:
# 	# 	refresh(obs, reward, done, info)  # Update the game screen [GUI only]
#
# print("Total reward:", total_reward)
#
# # Close the
# env.close()