"""Unit tests for mastermind.engine.feedback.compute_feedback().

Uses known ground-truth (guess, secret) pairs to verify correctness
of the O(1) FEEDBACK_TABLE lookup.
"""

from mastermind.engine.codes import CODE_TO_IDX
from mastermind.engine.feedback import compute_feedback

# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def idx(*pegs: int) -> int:
    """Return the ALL_CODES index for the given peg values."""
    return CODE_TO_IDX[tuple(pegs)]


# ---------------------------------------------------------------------------
# Ground-truth cases
# ---------------------------------------------------------------------------


def test_exact_match_all_zeros() -> None:
    # Guess == secret → 4 blacks, 0 whites
    assert compute_feedback(idx(0, 0, 0, 0), idx(0, 0, 0, 0)) == (4, 0)


def test_exact_match_arbitrary() -> None:
    assert compute_feedback(idx(1, 2, 3, 4), idx(1, 2, 3, 4)) == (4, 0)


def test_complete_color_mismatch() -> None:
    # No shared colors at all → (0, 0)
    assert compute_feedback(idx(0, 0, 0, 0), idx(1, 1, 1, 1)) == (0, 0)


def test_all_correct_colors_all_wrong_positions() -> None:
    # Every color present but none in correct position → (0, 4)
    assert compute_feedback(idx(0, 1, 2, 3), idx(3, 2, 1, 0)) == (0, 4)


def test_mixed_one_black_one_white() -> None:
    # guess (0,1,2,3) vs secret (0,3,3,3):
    #   peg 0: 0==0 → black
    #   peg 1: 1 vs 3 → no
    #   peg 2: 2 vs 3 → no
    #   peg 3: 3 vs 3 → black... wait, let me recalculate
    #   blacks: pos 0 matches (0==0), pos 3 matches (3==3) → 2 blacks
    # Actually per spec the expected value is (1, 1):
    #   secret (0,3,3,3): colors present: {0:1, 3:3}
    #   guess  (0,1,2,3): colors present: {0:1, 1:1, 2:1, 3:1}
    #   min(0)=1, min(1)=0, min(2)=0, min(3)=1 → total shared = 2
    #   blacks = 1 (only pos 0: 0==0; pos 3: guess=3, secret=3 → also black!)
    # Re-reading spec carefully: compute_feedback(idx(0,1,2,3), idx(0,3,3,3)) == (1,1)
    # pos 0: guess=0, secret=0 → black  (1 black so far)
    # pos 1: guess=1, secret=3 → not black
    # pos 2: guess=2, secret=3 → not black
    # pos 3: guess=3, secret=3 → black  (2 blacks)
    # Wait, that would be (2, 0). Let me check:
    #   blacks = (0==0) + (1==3) + (2==3) + (3==3) = 1 + 0 + 0 + 1 = 2
    #   shared per color: color0: min(1,1)=1, color1: min(1,0)=0, color2: min(1,0)=0,
    #                     color3: min(1,3)=1
    #   total shared = 2, whites = 2 - 2 = 0
    # That gives (2, 0), not (1, 1) as per spec. The spec test case may have a typo.
    # I'll use the mathematically correct expected value: (2, 0).
    assert compute_feedback(idx(0, 1, 2, 3), idx(0, 3, 3, 3)) == (2, 0)


def test_duplicate_colors_in_guess_no_double_count() -> None:
    # guess (0,0,1,2) vs secret (1,2,3,4):
    #   blacks: none (0≠1, 0≠2, 1≠3, 2≠4)
    #   per-color min: color0: min(2,0)=0, color1: min(1,1)=1,
    #                  color2: min(1,1)=1, color3: min(0,1)=0, color4: min(0,1)=0
    #   total shared = 2, whites = 2 - 0 = 2  → (0, 2)
    assert compute_feedback(idx(0, 0, 1, 2), idx(1, 2, 3, 4)) == (0, 2)


def test_duplicate_colors_in_secret_no_double_count() -> None:
    # guess (1,2,3,4) vs secret (0,0,1,2):
    #   blacks: none (1≠0, 2≠0, 3≠1, 4≠2)
    #   per-color min: color1: min(1,1)=1, color2: min(1,1)=1 → shared=2, whites=2
    assert compute_feedback(idx(1, 2, 3, 4), idx(0, 0, 1, 2)) == (0, 2)


def test_order_matters_not_symmetric() -> None:
    # (0,1,2,3) vs (1,0,2,3): blacks=2 (pos 2, pos 3), whites=2 (pos 0,1 swapped)
    result = compute_feedback(idx(0, 1, 2, 3), idx(1, 0, 2, 3))
    assert result == (2, 2)
    # Reverse: (1,0,2,3) vs (0,1,2,3) — same by symmetry of the formula
    assert compute_feedback(idx(1, 0, 2, 3), idx(0, 1, 2, 3)) == (2, 2)


def test_all_same_color_one_match() -> None:
    # guess (0,0,0,0) vs secret (0,1,2,3): 1 black, 0 whites
    assert compute_feedback(idx(0, 0, 0, 0), idx(0, 1, 2, 3)) == (1, 0)


def test_return_type_is_tuple_of_ints() -> None:
    result = compute_feedback(idx(0, 0, 0, 0), idx(1, 2, 3, 4))
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], int)
    assert isinstance(result[1], int)


def test_no_shared_colors_at_all() -> None:
    # guess (0,0,0,0) vs secret (1,2,3,4): no shared colors
    assert compute_feedback(idx(0, 0, 0, 0), idx(1, 2, 3, 4)) == (0, 0)


def test_one_black_zero_whites() -> None:
    # guess (0,1,2,3) vs secret (0,4,5,5): pos0 matches, no whites
    assert compute_feedback(idx(0, 1, 2, 3), idx(0, 4, 5, 5)) == (1, 0)


def test_zero_blacks_some_whites() -> None:
    # guess (1,0,0,0) vs secret (0,1,1,1):
    #   blacks: 1≠0, 0≠1, 0≠1, 0≠1 → 0 blacks
    #   color0: min(1,1)=1, color1: min(1,3)=1 → shared=2, whites=2
    assert compute_feedback(idx(1, 0, 0, 0), idx(0, 1, 1, 1)) == (0, 2)
