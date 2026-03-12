"""Unit tests for mastermind.engine.codes.

Covers ALL_CODES, CODE_TO_IDX, and FEEDBACK_TABLE invariants.
Note: 6 colors × 4 pegs → 6^4 = 1296 total codes (not 625 — the step-02
spec comment was incorrect; copilot-instructions.md is the source of truth).
"""

import numpy as np

from mastermind.engine.codes import (
    ALL_CODES,
    CODE_TO_IDX,
    FEEDBACK_TABLE,
    N_CODES,
    N_COLORS,
    N_PEGS,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------


def test_n_colors() -> None:
    assert N_COLORS == 6


def test_n_pegs() -> None:
    assert N_PEGS == 4


def test_n_codes() -> None:
    assert N_CODES == 1296  # 6^4


# ---------------------------------------------------------------------------
# ALL_CODES
# ---------------------------------------------------------------------------


def test_all_codes_length() -> None:
    assert len(ALL_CODES) == 1296


def test_all_codes_are_tuples_of_length_4() -> None:
    assert all(isinstance(c, tuple) and len(c) == N_PEGS for c in ALL_CODES)


def test_all_codes_values_in_range() -> None:
    assert all(0 <= v < N_COLORS for code in ALL_CODES for v in code)


def test_all_codes_no_duplicates() -> None:
    assert len(set(ALL_CODES)) == len(ALL_CODES)


def test_all_codes_first_element() -> None:
    assert ALL_CODES[0] == (0, 0, 0, 0)


def test_all_codes_last_element() -> None:
    # With itertools.product(range(6), repeat=4), last code is (5,5,5,5)
    assert ALL_CODES[1295] == (5, 5, 5, 5)


def test_all_codes_ordering() -> None:
    # Lexicographic order: (0,0,0,1) is at index 1, (0,0,1,0) at index 6
    assert ALL_CODES[1] == (0, 0, 0, 1)
    assert ALL_CODES[6] == (0, 0, 1, 0)


# ---------------------------------------------------------------------------
# CODE_TO_IDX
# ---------------------------------------------------------------------------


def test_code_to_idx_length() -> None:
    assert len(CODE_TO_IDX) == 1296


def test_code_to_idx_round_trip_all() -> None:
    for i, code in enumerate(ALL_CODES):
        assert CODE_TO_IDX[code] == i


def test_code_to_idx_reverse_round_trip() -> None:
    for code, idx in CODE_TO_IDX.items():
        assert ALL_CODES[idx] == code


def test_code_to_idx_sample_values() -> None:
    assert CODE_TO_IDX[(0, 0, 0, 0)] == 0
    assert CODE_TO_IDX[(5, 5, 5, 5)] == 1295


# ---------------------------------------------------------------------------
# FEEDBACK_TABLE
# ---------------------------------------------------------------------------


def test_feedback_table_shape() -> None:
    assert FEEDBACK_TABLE.shape == (1296, 1296, 2)


def test_feedback_table_dtype() -> None:
    assert FEEDBACK_TABLE.dtype == np.int8


def test_feedback_table_diagonal_blacks() -> None:
    # Every code against itself must return N_PEGS blacks
    assert all(FEEDBACK_TABLE[i, i, 0] == N_PEGS for i in range(N_CODES))


def test_feedback_table_diagonal_whites() -> None:
    # Every code against itself must return 0 whites
    assert all(FEEDBACK_TABLE[i, i, 1] == 0 for i in range(N_CODES))


def test_feedback_table_all_values_non_negative() -> None:
    assert int(FEEDBACK_TABLE.min()) >= 0


def test_feedback_table_blacks_plus_whites_le_n_pegs() -> None:
    totals = FEEDBACK_TABLE[:, :, 0].astype(np.int16) + FEEDBACK_TABLE[:, :, 1].astype(
        np.int16
    )
    assert int(totals.max()) <= N_PEGS


def test_feedback_table_blacks_le_n_pegs() -> None:
    assert int(FEEDBACK_TABLE[:, :, 0].max()) <= N_PEGS


def test_feedback_table_whites_le_n_pegs() -> None:
    assert int(FEEDBACK_TABLE[:, :, 1].max()) <= N_PEGS


def test_feedback_table_perfect_match_only_on_diagonal() -> None:
    # FEEDBACK_TABLE[i, j, 0] == N_PEGS implies i == j (same code)
    blacks = FEEDBACK_TABLE[:, :, 0]
    rows, cols = np.where(blacks == N_PEGS)
    assert all(r == c for r, c in zip(rows.tolist(), cols.tolist()))
