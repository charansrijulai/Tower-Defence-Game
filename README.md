# Tower Defense RL Agent Project

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

## Project Roadmap

- **Division of Work:**  
  - Two dedicated teams will work in parallel:
    - **Team Deep Learning:** Focus on developing and training the RL agent.
    - **Team Genetic Algorithms:** Focus on implementing and optimizing evolutionary strategies.
- **Timeline:**  
  - **Duration:** 2 weeks.
- **Soft Deliverables:**  
  - A simple, functional UI.
  - A working RL agent capable of playing the Tower Defense game.
