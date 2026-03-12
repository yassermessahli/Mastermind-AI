import numpy as np

from mastermind.agents.base_agent import BaseAgent


class ConsistentAgent(BaseAgent):
    """Selects uniformly at random from only the consistent (masked) codes."""

    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        valid = np.where(action_masks)[0]
        return int(np.random.choice(valid))
