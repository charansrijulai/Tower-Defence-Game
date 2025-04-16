import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
from collections import deque
from test_gym_train import TowerDefenseEnv

# Hyperparameters
gamma = 0.9
epsilon = 1.0
epsilon_decay = 0.9999932
min_epsilon = 0.1
batch_size = 64
learning_rate = 0.0005
num_episodes = 10000
target_update_freq = 500  # Frequency of target network update
max_memory = 10000  # Max size of experience replay buffer

# Neural Network for Q-value approximation
class QNetwork(nn.Module):
    def __init__(self, observation_space, action_space, internal_nodes=128):
        super(QNetwork, self).__init__()
        self.dense1 = nn.Linear(observation_space, internal_nodes)  # Input size is 3 (current_x, current_y, selected_tower) for the state
        self.dense2 = nn.Linear(internal_nodes, internal_nodes)
        self.q_values = nn.Linear(internal_nodes, action_space)

    def forward(self, state):
        x = torch.relu(self.dense1(state))
        x = torch.relu(self.dense2(x))
        return self.q_values(x)

# Experience Replay Buffer
class ReplayBuffer:
    def __init__(self, max_size):
        self.buffer = deque(maxlen=max_size)

    def add(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def size(self):
        return len(self.buffer)

# Train the model
def train_step(model, target_model, batch, optimizer):
    global gamma

    states, actions, rewards, next_states, dones = zip(*batch)

    states = torch.tensor(np.array(states), dtype=torch.float32)
    actions = torch.tensor(actions, dtype=torch.int64)
    rewards = torch.tensor(rewards, dtype=torch.float32)
    next_states = torch.tensor(np.array(next_states), dtype=torch.float32)
    dones = torch.tensor(dones, dtype=torch.float32)

    # Predict Q-values for current states and next states
    q_values = model(states)
    next_q_values = target_model(next_states)

    # Get the Q-values for the taken actions
    action_indices = actions
    q_values_taken = q_values.gather(1, action_indices.unsqueeze(1))

    # Get the target Q-values for next states
    with torch.no_grad():
        max_next_q_values = next_q_values.max(1)[0]
        target_q_values = rewards + gamma * (1 - dones) * max_next_q_values

    loss = nn.MSELoss()(q_values_taken.squeeze(), target_q_values)

    # Update the model
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()

# Main training loop
def dqn():
    global epsilon
    global epsilon_decay
    global min_epsilon
    global batch_size
    global learning_rate
    global num_episodes
    global target_update_freq
    global max_memory

    print('Hyperparameters:')
    print(f"Epsilon: {epsilon}")
    print(f"Epsilon Decay: {epsilon_decay}")
    print(f"Min Epsilon: {min_epsilon}")
    print(f"Batch Size: {batch_size}")
    print(f"Learning Rate: {learning_rate}")
    print(f"Number of Episodes: {num_episodes}")
    print(f"Target Update Frequency: {target_update_freq}")
    print(f"Max Memory: {max_memory}")
    print("Starting DQN training...")
    
    env = TowerDefenseEnv()

    # Initialize the Q-network and target Q-network
    action_space = env.action_space.n
    model = QNetwork(3, action_space)
    target_model = QNetwork(3, action_space)

    # Optimizer
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    # Initialize replay buffer
    replay_buffer = ReplayBuffer(max_memory)

    # Initialize the target network
    target_model.load_state_dict(model.state_dict())

    total_rewards = []

    for episode in range(num_episodes):
        if episode % 100 == 0:
            print(f"Episode {episode} - DONE")
        obs, reward, done, info = env.reset()
        state = np.array([obs['current_position'][0], obs['current_position'][1], obs['current_selected_tower']])
        state = torch.tensor(state, dtype=torch.float32)
        total_reward = 0

        while not done:
            # Epsilon-greedy action selection
            if np.random.rand() < epsilon:
                action = env.action_space.sample()
            else:
                with torch.no_grad():
                    q_values = model(state.unsqueeze(0))
                    action = torch.argmax(q_values).item()

            # Take action and observe next state
            next_obs, reward, done, info = env.step(action)
            next_state = np.array([next_obs['current_position'][0], next_obs['current_position'][1], next_obs['current_selected_tower']])
            next_state = torch.tensor(next_state, dtype=torch.float32)

            # Store the experience in the replay buffer
            replay_buffer.add((state.numpy(), action, reward, next_state.numpy(), done))

            # Sample a batch of experiences from the replay buffer
            if replay_buffer.size() > batch_size:
                batch = replay_buffer.sample(batch_size)
                loss = train_step(model, target_model, batch, optimizer)

            state = next_state
            total_reward += reward

        # Update the epsilon (decay epsilon for exploration)
        if epsilon > min_epsilon:
            epsilon *= epsilon_decay

        total_rewards.append(total_reward)

        # Periodically update the target network
        if episode % target_update_freq == 0:
            target_model.load_state_dict(model.state_dict())

    return model

# Testing the trained model
def test_model():
    env = TowerDefenseEnv()
    obs, reward, done, info = env.reset()

    action_space = env.action_space.n
    model = QNetwork(3, action_space)
    model.load_state_dict(torch.load('dqn_tower_defense_model.pth'))
    model.eval()

    state = np.array([obs['current_position'][0], obs['current_position'][1], obs['current_selected_tower']])
    state = torch.tensor(state, dtype=torch.float32)
    total_reward = 0

    while not done:
        with torch.no_grad():
            q_values = model(state.unsqueeze(0))
            action = torch.argmax(q_values).item()
        next_obs, reward, done, info = env.step(action)
        print(f'Observation: {next_obs}, Action: {action}, Reward: {reward}, Done: {done}, Info: {info}')
        state = np.array([next_obs['current_position'][0], next_obs['current_position'][1], next_obs['current_selected_tower']])
        state = torch.tensor(state, dtype=torch.float32)
        total_reward += reward

    print("Total reward:", total_reward)
    print("Final wave:", env.current_wave)
    env.close()

is_train = False
if is_train:
    # Training the DQN model
    model = dqn()
    # Saving the trained model
    torch.save(model.state_dict(), "dqn_tower_defense_model.pth")
else:
    # Test the trained model
    test_model()