import numpy as np

from mastermind.agents.base_agent import BaseAgent
from mastermind.engine.codes import CODE_TO_IDX, FEEDBACK_TABLE, N_CODES

_OPENER: int = CODE_TO_IDX[(0, 0, 1, 1)]


class KnuthAgent(BaseAgent):
    """Minimax agent. Guaranteed to solve in =< 5 guesses.

    First guess is always the canonical Knuth opener (0, 0, 1, 1).
    From round 2 on, selects the guess that minimises the worst-case
    partition size over the current consistent set, preferring consistent
    codes when scores are equal.
    """

    def __init__(self) -> None:
        self._is_first_move = True

    def reset(self) -> None:
        self._is_first_move = True

    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        if self._is_first_move:
            self._is_first_move = False
            return _OPENER

        consistent_arr = np.where(action_masks)[0]

        if len(consistent_arr) == 1:
            return int(consistent_arr[0])

        consistent_set = set(int(i) for i in consistent_arr)
        best_guess = int(consistent_arr[0])
        best_score = (float("inf"), True)  # (worst_case, not_in_consistent)

        for guess_idx in range(N_CODES):
            # Vectorised: feedbacks shape (|consistent|, 2)
            feedbacks = FEEDBACK_TABLE[guess_idx, consistent_arr]
            _, counts = np.unique(feedbacks, axis=0, return_counts=True)
            worst_case = int(counts.max())
            score = (worst_case, guess_idx not in consistent_set)
            if score < best_score:
                best_score = score
                best_guess = guess_idx

        return best_guess
