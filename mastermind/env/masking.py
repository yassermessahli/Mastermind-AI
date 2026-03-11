import numpy as np

from mastermind.engine.codes import FEEDBACK_TABLE, N_CODES


def get_initial_consistent_set() -> set[int]:
    """Return the set of all code indices {0, 1, ..., N_CODES-1}."""
    return set(range(N_CODES))


def update_consistent_set(
    consistent_set: set[int],
    guess_idx: int,
    feedback: tuple[int, int],
) -> set[int]:
    """Return a new set containing only codes still consistent with the feedback.

    Uses FEEDBACK_TABLE for O(1) per-code consistency check.
    Never mutates the input set.
    """
    blacks, whites = feedback
    return {
        code_idx
        for code_idx in consistent_set
        if (
            FEEDBACK_TABLE[guess_idx, code_idx, 0] == blacks
            and FEEDBACK_TABLE[guess_idx, code_idx, 1] == whites
        )
    }


def get_action_masks(consistent_set: set[int]) -> np.ndarray:
    """Return bool array of shape (N_CODES,); True at index i if i is consistent."""
    mask = np.zeros(N_CODES, dtype=np.bool_)
    mask[sorted(consistent_set)] = True
    return mask
