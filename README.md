# Tower Defense RL Agent Project

![Final UI](/assets/v3.gif)  
*The latest version of the Tower Defense game UI with integrated RL agent and full gameplay flow.*

## Overview

This project aims to develop an RL (Reinforcement Learning) agent that efficiently plays a Tower Defense game. The primary objective is to design a system where the agent defends the territory by strategically managing towers along enemy paths. If time permits, additional attacking capabilities may be integrated.

## Tower Defense Game Summary

- **Objective:** Protect your territory by preventing enemy attackers from reaching your base or exit points.
- **Gameplay:**  
  - Strategically place the defensive towers along enemy paths.
  - Earn money by defeating enemies, which is used to purchase and upgrade towers.
- **Winning Condition:**  
  - Successfully defend against all waves of attackers.
  - If any enemy breaches the defenses, the opposing side wins.
- **Challenge Factors:**  
  - Limited funds and available placement spots make resource management a key strategic element.

## Project Objectives

- **Key Goal:** Develop an RL agent that efficiently plays the Tower Defense game in defense (and attacking if time permits).
- **End-to-End Workflow:**  
  - **Environment Setup:**  
    - Utilize **Pygame** for game visualization.
    - Employ **Gymnasium** to create the landscape and define enemy paths.
  - **Algorithms & Models:**  
    - **Deep Learning:** To build and train the RL agent’s decision-making system.
    - **Genetic Algorithms:** To evolve and optimize tower placement strategies.
  - **Approach:**  
    1. **Environment Construction:** Build the game map and enemy paths using Pygame and Gymnasium.
    2. **RL Agent Development:** Create a deep learning-based model to control tower placements and defense actions.
    3. **Strategy Optimization:** Integrate genetic algorithms to improve the agent’s strategies iteratively.
    4. **Integration:** Combine all components into an end-to-end workflow with a simple UI.

## Ways to Run The Game?

NOTE: Before running either the manual or the agent mode, ensure that all the requirements have been installed in your python environment using the following command in your terminal:
```
pip install -r requirements.txt
```

### Manual Mode
- Make sure you are inside the **Q-learning/UI** directory
- Before running either of the following files make the following changes to ensure manual mode is set:
```
agent_mode = False
```
- If you want to use the V2 UI, run **tdg_view.py** and if you want to run the V3 UI (consisting of attacking animations) **tdg_view_animated.py**
- Following are the game controls:
    1. W: Up
    2. A: Left
    3. S: Down
    4. D: Right
    5. P: Place Tower
    6. V: Start Wave

### Agent Mode
- Make sure you are inside the **Q-learning/UI** directory
- Before running either of the following files make the following changes to ensure manual mode is set:
```
agent_mode = True
```
- If you want to use the V2 UI, run **tdg_view.py** and if you want to run the V3 UI (consisting of attacking animations) **tdg_view_animated.py**
- To choose the type of agent (Q-learning agent or DQN agent), you can modify the following lines in either of the above two files that is being used:
```
# To use Q-learning agent
game = GameController(algo='ql')
# To use DQN agent
game = GameController(algo='dqn')
```
- Finally set the correct path to the saved parameters file of the agent being used inside the **tdg_controller.py**:
```
# For the DQN agent, put the correct path of the params file present inside the train folder, inside line 16 of tdg_controller.py
model.load_state_dict(torch.load(<DQN_PARAMS_PATH>))
# For the Q-learning agent, put the correct path of the params file present inside the train folder, inside line 26 of tdg_controller.py
with open(<Q_LEARNING_PARAMS_PATH>, 'rb') as f:
```
- Finally run either **tdg_view.py** or **tdg_view_animated.py** as needed

## UI Evolution

### Version 1 – Basic Layout
![UI v1](/assets/v1.png)  
*Simple `25×10`  grid-based board with basic tower/enemy placing using colored cells.*

### Version 2 – Enhanced Visuals & Logic
![UI v2](/assets/v2.gif)  
*Introduced sprites, improved health bar logic, and better enemy animations. Grid size is `7×7`*

### Version 3 – RL Integration + Game Polish
![UI v3](/assets/v3.gif)  
*Full integration of RL agent logic, cursor dynamics during waves, tower range animations, and overall polish.*

## Project Roadmap

- **Division of Work:**  
  - Two dedicated teams will work in parallel:
    - **Team Deep Learning:** Focus on developing and training the RL agent.
    - **Team Genetic Algorithms:** Focus on implementing and optimizing evolutionary strategies.
- **Timeline:**  
  - **Duration:** 14 weeks.
- **Soft Deliverables:**  
  - A simple, functional UI.
  - A working RL agent capable of playing the Tower Defense game.

## Assets Attribution

- Goblin sprite by William.Thompsonj and Redshrike  
  - Source: [LPC Goblin](https://opengameart.org/content/lpc-goblin)  
  - License: [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/)

- Guard Tower sprite by Blarumyrran  
  - Source: [Medieval Stone Guard Tower (isometric 2.5D)](https://opengameart.org/content/medieval-stone-guard-tower-isometric-25d)  
  - License: [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/)

- Orc sprite by wulax  
  - Source: [Orc Static 64x64](https://opengameart.org/content/orc-static-64x64)  
  - License: [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/)

- Grass tile by ansimuz  
  - Source: [Grass Tile 0](https://opengameart.org/content/grass-tile-0)  
  - License: [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/)

- Cobblestone tile by Bleed  
  - Source: [Cobblestone Tile](https://opengameart.org/content/cobblestone-tile)  
  - License: [CC-BY 3.0](https://creativecommons.org/licenses/by/3.0/)

- Watchtower Level 2 and Level 3 sprites generated with the assistance of ChatGPT (March 2025 version) by OpenAI  
  - Source: Generated via prompt-based image assistance in ChatGPT  
  - License: Used with permission under OpenAI’s terms for generated content
