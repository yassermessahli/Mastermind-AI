"""MastermindGame — stateful single-episode game session."""

import random

from mastermind.engine.codes import N_CODES
from mastermind.engine.feedback import compute_feedback


class MastermindGame:
    """Manage one game episode: hold the secret, accept guesses, track history.

    Parameters
    ----------
    secret_idx:
        Index into ALL_CODES for the secret code.  If ``None`` (default), a
        random code is chosen uniformly from [0, N_CODES).
    """

    def __init__(self, secret_idx: int | None = None) -> None:
        self._secret_idx: int = (
            secret_idx if secret_idx is not None else random.randrange(N_CODES)
        )
        self._history: list[tuple[int, tuple[int, int]]] = []
        self._solved: bool = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def secret_idx(self) -> int:
        """Index of the secret code in ALL_CODES."""
        return self._secret_idx

    @property
    def history(self) -> list[tuple[int, tuple[int, int]]]:
        """Ordered list of ``(guess_idx, (blacks, whites))`` pairs."""
        return self._history

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def is_solved(self) -> bool:
        """Return ``True`` if the last guess was an exact match."""
        return self._solved

    def n_guesses(self) -> int:
        """Return the number of guesses made so far."""
        return len(self._history)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def guess(self, guess_idx: int) -> tuple[int, int]:
        """Submit a guess and receive feedback.

        Parameters
        ----------
        guess_idx:
            Index into ALL_CODES for the guessed code.

        Returns
        -------
        tuple[int, int]
            ``(blacks, whites)`` feedback.

        Raises
        ------
        ValueError
            If the game is already solved.
        """
        if self._solved:
            raise ValueError(
                "Game is already solved. Call reset() to start a new episode."
            )

        feedback = compute_feedback(guess_idx, self._secret_idx)
        self._history.append((guess_idx, feedback))

        if feedback[0] == 4:  # N_PEGS blacks → perfect match
            self._solved = True

        return feedback

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def reset(self, secret_idx: int | None = None) -> None:
        """Reset the game state for a new episode.

        Parameters
        ----------
        secret_idx:
            New secret code index.  If ``None``, a random code is chosen.
        """
        self._secret_idx = (
            secret_idx if secret_idx is not None else random.randrange(N_CODES)
        )
        self._history = []
        self._solved = False
