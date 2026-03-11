import numpy as np
from gymnasium import spaces

from mastermind.engine.codes import ALL_CODES


class ObservationEncoder:
    def __init__(self, n_colors: int, n_pegs: int, max_steps: int) -> None:
        self._n_colors = n_colors
        self._n_pegs = n_pegs
        self._max_steps = max_steps
        self._dims_per_step = n_pegs * n_colors + 2
        self._n_codes = n_colors**n_pegs
        self._obs_dim = max_steps * self._dims_per_step + 2

    @property
    def obs_dim(self) -> int:
        """max_steps * (n_pegs * n_colors + 2) + 2"""
        return self._obs_dim

    def observation_space(self) -> spaces.Box:
        """low=0.0, high=1.0, shape=(obs_dim,), dtype=np.float32"""
        return spaces.Box(
            low=0.0,
            high=1.0,
            shape=(self._obs_dim,),
            dtype=np.float32,
        )

    def encode(
        self,
        history: list[tuple[int, tuple[int, int]]],
        remaining_valid: int,
        current_step: int,
    ) -> np.ndarray:
        """Return flat float32 array of shape (obs_dim,).

        history: [(guess_idx, (blacks, whites)), ...]
        guess_idx is resolved to a code tuple via ALL_CODES internally.
        Unseen steps are zero-padded.
        """
        obs = np.zeros(self._obs_dim, dtype=np.float32)

        # History block
        for step_i, (guess_idx, (blacks, whites)) in enumerate(history):
            code = ALL_CODES[guess_idx]
            base = step_i * self._dims_per_step
            for peg, color in enumerate(code):
                obs[base + peg * self._n_colors + color] = 1.0
            obs[base + self._n_pegs * self._n_colors] = blacks / self._n_pegs
            obs[base + self._n_pegs * self._n_colors + 1] = whites / self._n_pegs

        # Constraint signal
        obs[-2] = remaining_valid / self._n_codes
        obs[-1] = current_step / self._max_steps

        return obs
