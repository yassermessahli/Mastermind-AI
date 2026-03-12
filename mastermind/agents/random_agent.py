import numpy as np

from mastermind.agents.base_agent import BaseAgent
from mastermind.engine.codes import N_CODES


class RandomAgent(BaseAgent):
    """Selects uniformly at random from all codes — ignores the mask entirely."""

    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        return int(np.random.randint(0, N_CODES))
