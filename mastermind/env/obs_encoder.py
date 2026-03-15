import numpy as np
from gymnasium import spaces

from mastermind.engine.codes import ALL_CODES


class ObservationEncoder:
    """Encodes a Mastermind game history into a flat float32 observation vector.

    Layout (default: 6 colors, 4 pegs, 8 max steps):

    - ``max_steps`` step blocks of ``n_pegs * n_colors + 2`` floats each:
        - ``n_pegs * n_colors`` one-hot color values (avoids false ordinal encoding)
        - normalized blacks (blacks / n_pegs)
        - normalized whites (whites / n_pegs)
    - 1 float: fraction of consistent codes remaining (remaining / n_codes)
    - 1 float: normalized step progress (current_step / max_steps)

    Total dimension: ``max_steps * (n_pegs * n_colors + 2) + 2``
    (210 for the default configuration).  All values in [0, 1].
    Unseen future steps are zero-padded.

    Parameters
    ----------
    n_colors:
        Number of distinct peg colors.
    n_pegs:
        Number of pegs per code.
    max_steps:
        Maximum number of guesses per episode.
    """

    def __init__(self, n_colors: int, n_pegs: int, max_steps: int) -> None:
        self._n_colors = n_colors
        self._n_pegs = n_pegs
        self._max_steps = max_steps
        self._dims_per_step = n_pegs * n_colors + 2
        self._n_codes = n_colors**n_pegs
        self._obs_dim = max_steps * self._dims_per_step + 2

    @property
    def obs_dim(self) -> int:
        """Total observation vector length.

        Formula: ``max_steps * (n_pegs * n_colors + 2) + 2``
        """
        return self._obs_dim

    def observation_space(self) -> spaces.Box:
        """Return the Gymnasium Box space: shape ``(obs_dim,)``, values in [0, 1]."""
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
        """Return a flat float32 observation vector of shape ``(obs_dim,)``.

        Parameters
        ----------
        history:
            List of ``(guess_idx, (blacks, whites))`` tuples in guess order.
            ``guess_idx`` is resolved to a code tuple via ``ALL_CODES``.
        remaining_valid:
            Number of codes still consistent with all feedback so far.
        current_step:
            Number of guesses made so far (0 at episode start).

        Returns
        -------
        np.ndarray
            Float32 array of shape ``(obs_dim,)``.  Steps beyond
            ``len(history)`` are zero-padded.
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
