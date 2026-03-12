from typing import Any

import numpy as np

from mastermind.agents.base_agent import BaseAgent
from mastermind.env.mastermind_env import MastermindEnv


def run_benchmark(
    agent: BaseAgent,
    env: MastermindEnv,
    n_episodes: int = 1000,
) -> dict[str, Any]:
    """Run agent for n_episodes and return raw results.

    Returns a dict with:
    - guess_counts: number of guesses per episode
    - wins: True if the agent solved the episode
    - total_rewards: cumulative reward per episode
    """
    guess_counts: list[int] = []
    wins: list[bool] = []
    total_rewards: list[float] = []

    for _ in range(n_episodes):
        obs, _ = env.reset()
        agent.reset()
        terminated = truncated = False
        episode_reward = 0.0
        guesses = 0
        while not (terminated or truncated):
            masks = env.action_masks()
            action = agent.select_action(obs, masks)
            obs, reward, terminated, truncated, _ = env.step(np.intp(action))
            episode_reward += float(reward)
            guesses += 1
        guess_counts.append(guesses)
        wins.append(bool(terminated))
        total_rewards.append(episode_reward)

    return {
        "guess_counts": guess_counts,
        "wins": wins,
        "total_rewards": total_rewards,
    }
