# TaxiMDP-RL

A reinforcement-learning playground for the classic grid-based Taxi domain—augmented with fuel constraints, passenger capacities, and gas-station refueling.

## 🚖 Project Highlights

- **Markov Decision Process (MDP)**: Defines states, actions, transitions, and rewards for a realistic taxi dispatch scenario with fuel management and capacity limits.  
- **State Encoding & Hashability**: Converts rich nested-dictionary observations into immutable tuples for efficient lookup in replay buffers and hash tables.  
- **Action Space**  
  - Drive (N/S/E/W): Move one cell, consuming fuel and carrying onboard passengers.  
  - Pick Up / Drop Off: Board or alight passengers only at correct locations.  
  - Refuel: Recharge at designated gas-station tiles.  
  - Wait: Idle action for no-op policies.  
- **Reward Engineering**: Customizable shaping for passenger deliveries, fuel-efficiency penalties, out-of-fuel penalties, exploration bonuses, and sparse-goal incentives.  
- **Plug-and-Play with RL Frameworks**: Adapt the core environment to OpenAI Gym’s Env interface or integrate directly with TorchRL, Stable Baselines3, and RLlib.  
- **Baseline Heuristics**: Includes admissible heuristics (Manhattan distance, passenger counts) for hybrid heuristic-guided RL and Dyna-style planning.  
