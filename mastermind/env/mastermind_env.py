import math
from typing import Any

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from mastermind.engine.codes import N_CODES, N_COLORS, N_PEGS
from mastermind.engine.game import MastermindGame
from mastermind.env.masking import (
    get_action_masks,
    get_initial_consistent_set,
    update_consistent_set,
)
from mastermind.env.obs_encoder import ObservationEncoder

_DEFAULTS: dict[str, Any] = {
    "n_colors": N_COLORS,
    "n_pegs": N_PEGS,
    "max_steps": 10,
    "reward_variant": "step_penalty",
    "win_bonus": 1.0,
    "step_penalty": -0.1,
    "lose_penalty": 0.0,
}


class MastermindEnv(gym.Env[np.ndarray, np.intp]):
    """Gymnasium environment for the Mastermind code-breaking game.

    The agent guesses a hidden code from a discrete action space of size
    ``n_colors ** n_pegs`` (default 1296). After each guess the environment
    returns an observation encoding the full guess/feedback history and the
    size of the remaining consistent set.  Invalid actions (codes already
    eliminated by feedback) are masked out via ``action_masks()``.

    Parameters
    ----------
    config:
        Optional dict of overrides for the defaults defined in ``_DEFAULTS``.
        Keys: ``n_colors``, ``n_pegs``, ``max_steps``, ``reward_variant``,
        ``win_bonus``, ``step_penalty``, ``lose_penalty``.
    """

    metadata: dict[str, list[Any]] = {"render_modes": []}

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        cfg: dict[str, Any] = {**_DEFAULTS, **(config or {})}
        self._n_colors: int = int(cfg["n_colors"])
        self._n_pegs: int = int(cfg["n_pegs"])
        self._max_steps: int = int(cfg["max_steps"])
        self._reward_variant: str = str(cfg["reward_variant"])
        self._win_bonus: float = float(cfg["win_bonus"])
        self._step_penalty: float = float(cfg["step_penalty"])
        self._lose_penalty: float = float(cfg["lose_penalty"])

        self._encoder = ObservationEncoder(
            n_colors=self._n_colors,
            n_pegs=self._n_pegs,
            max_steps=self._max_steps,
        )

        self.observation_space = self._encoder.observation_space()
        self.action_space = spaces.Discrete(N_CODES)

        self._game = MastermindGame()
        self._consistent_set: set[int] = get_initial_consistent_set()
        self._before_consistent_size: int = N_CODES

    def reset(
        self,
        seed: int | None = None,
        options: dict[str, Any] | None = None,
    ) -> tuple[np.ndarray, dict[str, Any]]:
        """Start a new episode with a freshly sampled secret code.

        Parameters
        ----------
        seed:
            If provided, the secret is derived deterministically from this
            seed via ``np_random``.  If ``None``, the secret is chosen
            uniformly at random by ``MastermindGame``.
        options:
            Unused; present for Gymnasium API compatibility.

        Returns
        -------
        obs:
            Zero-padded observation vector of shape ``(obs_dim,)``.
        info:
            ``{"consistent_remaining": 1296}`` at episode start.
        """
        super().reset(seed=seed)
        if seed is not None:
            secret_idx = int(self.np_random.integers(0, N_CODES))
            self._game.reset(secret_idx=secret_idx)
        else:
            self._game.reset()
        self._consistent_set = get_initial_consistent_set()
        obs = self._encoder.encode(
            history=[],
            remaining_valid=len(self._consistent_set),
            current_step=0,
        )
        return obs, {"consistent_remaining": len(self._consistent_set)}

    def step(
        self, action: np.intp
    ) -> tuple[np.ndarray, float, bool, bool, dict[str, Any]]:
        """Apply one guess and return the next observation, reward, and flags.

        Parameters
        ----------
        action:
            Index into ``ALL_CODES`` representing the guessed code.

        Returns
        -------
        obs:
            Updated observation encoding the full guess history.
        reward:
            Scalar reward computed by the configured reward variant.
        terminated:
            ``True`` when ``blacks == n_pegs`` (correct guess).
        truncated:
            ``True`` when the guess limit is reached without solving.
        info:
            ``{"blacks", "whites", "consistent_remaining", "n_guesses"}``.
        """
        self._before_consistent_size = len(self._consistent_set)
        feedback = self._game.guess(int(action))
        blacks, whites = feedback

        self._consistent_set = update_consistent_set(
            self._consistent_set, int(action), feedback
        )
        after_size = len(self._consistent_set)

        terminated = blacks == self._n_pegs
        truncated = (not terminated) and (self._game.n_guesses() >= self._max_steps)

        reward = self._compute_reward(blacks, whites)
        if truncated and self._reward_variant == "shaped":
            reward = float(self._lose_penalty)

        obs = self._encoder.encode(
            history=self._game.history,
            remaining_valid=after_size,
            current_step=self._game.n_guesses(),
        )
        info = {
            "blacks": blacks,
            "whites": whites,
            "consistent_remaining": after_size,
            "n_guesses": self._game.n_guesses(),
        }
        return obs, reward, terminated, truncated, info

    def action_masks(self) -> np.ndarray:
        """Return a bool mask of shape ``(1296,)`` for use with MaskablePPO.

        ``True`` at index ``i`` means code ``ALL_CODES[i]`` is still consistent
        with all feedback received so far.  At least one entry is always ``True``.
        """
        return get_action_masks(self._consistent_set)

    def _compute_reward(self, blacks: int, whites: int) -> float:
        """Applies the configured reward variant."""
        if blacks == self._n_pegs:
            return float(self._win_bonus)

        if self._reward_variant == "sparse":
            return 0.0

        base = float(self._step_penalty)

        if self._reward_variant == "information":
            after_size = len(self._consistent_set)
            if self._before_consistent_size > 0 and after_size > 0:
                info_gain = math.log2(
                    self._before_consistent_size / after_size
                ) / math.log2(N_CODES)
                return base + info_gain

        return base
