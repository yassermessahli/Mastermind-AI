from abc import ABC, abstractmethod

import numpy as np


class BaseAgent(ABC):
    @abstractmethod
    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        """Select a code index given current observation and valid action mask."""

    def reset(self) -> None:
        """Called at the start of each episode. Override if agent has state."""
