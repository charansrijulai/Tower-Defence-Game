import torch
import torch.nn as nn

# Neural Network for Q-value approximation
class QNetwork(nn.Module):
    def __init__(self, observation_space, action_space, internal_nodes=128):
        super(QNetwork, self).__init__()
        self.dense1 = nn.Linear(observation_space, internal_nodes)
        self.dense2 = nn.Linear(internal_nodes, internal_nodes)
        self.q_values = nn.Linear(internal_nodes, action_space)

    def forward(self, state):
        x = torch.relu(self.dense1(state))
        x = torch.relu(self.dense2(x))
        return self.q_values(x)