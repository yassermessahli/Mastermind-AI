"""Mastermind code-space constants.

Defines the full enumeration of all the codes, their index mapping,
and the precomputed feedback look-up table.

All three objects are module-level constants computed once at import time.
No other module should recompute them.
"""

import itertools

import numpy as np
import tqdm

# ---------------------------------------------------------------------------
# Dimensions
# ---------------------------------------------------------------------------

N_COLORS: int = 6
N_PEGS: int = 4
N_CODES: int = N_COLORS**N_PEGS  # 6^4 = 1296

# ---------------------------------------------------------------------------
# ALL_CODES
# ---------------------------------------------------------------------------

ALL_CODES: list[tuple[int, ...]] = list(
    itertools.product(range(N_COLORS), repeat=N_PEGS)
)

# ---------------------------------------------------------------------------
# CODE_TO_IDX
# ---------------------------------------------------------------------------

CODE_TO_IDX: dict[tuple[int, ...], int] = {
    code: idx for idx, code in enumerate(ALL_CODES)
}

# ---------------------------------------------------------------------------
# FEEDBACK_TABLE
# ---------------------------------------------------------------------------


def _compute_feedback_raw(
    guess: tuple[int, ...], secret: tuple[int, ...]
) -> tuple[int, int]:
    """Compute (blacks, whites) directly — used only during table construction."""
    blacks = sum(g == s for g, s in zip(guess, secret))
    whites = sum(min(guess.count(c), secret.count(c)) for c in range(N_COLORS)) - blacks
    return blacks, whites


def _build_feedback_table() -> np.ndarray:
    table = np.empty((N_CODES, N_CODES, 2), dtype=np.int8)
    for guess_idx, guess in tqdm.tqdm(
        enumerate(ALL_CODES), total=N_CODES, desc="Setup Game"
    ):
        for secret_idx, secret in enumerate(ALL_CODES):
            blacks, whites = _compute_feedback_raw(guess, secret)
            table[guess_idx, secret_idx, 0] = blacks
            table[guess_idx, secret_idx, 1] = whites
    return table


FEEDBACK_TABLE: np.ndarray = _build_feedback_table()
