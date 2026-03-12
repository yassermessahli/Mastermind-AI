"""Unit tests for mastermind.engine.game.MastermindGame."""

import pytest

from mastermind.engine.codes import N_CODES, N_PEGS
from mastermind.engine.game import MastermindGame

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_wrong_idx(secret_idx: int) -> int:
    """Return any index that is different from secret_idx."""
    return (secret_idx + 1) % N_CODES


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------


def test_init_secret_idx_in_range() -> None:
    game = MastermindGame()
    assert 0 <= game.secret_idx < N_CODES


def test_init_history_empty() -> None:
    game = MastermindGame()
    assert game.history == []


def test_init_n_guesses_zero() -> None:
    game = MastermindGame()
    assert game.n_guesses() == 0


def test_init_not_solved() -> None:
    game = MastermindGame()
    assert game.is_solved() is False


def test_init_with_specific_secret() -> None:
    game = MastermindGame(secret_idx=42)
    assert game.secret_idx == 42


def test_init_with_zero_secret() -> None:
    game = MastermindGame(secret_idx=0)
    assert game.secret_idx == 0


def test_init_with_max_secret() -> None:
    game = MastermindGame(secret_idx=N_CODES - 1)
    assert game.secret_idx == N_CODES - 1


# ---------------------------------------------------------------------------
# Correct guess
# ---------------------------------------------------------------------------


def test_correct_guess_returns_n_pegs_zero() -> None:
    game = MastermindGame(secret_idx=7)
    blacks, whites = game.guess(7)
    assert blacks == N_PEGS
    assert whites == 0


def test_correct_guess_sets_solved() -> None:
    game = MastermindGame(secret_idx=7)
    game.guess(7)
    assert game.is_solved() is True


def test_correct_guess_n_guesses_one() -> None:
    game = MastermindGame(secret_idx=7)
    game.guess(7)
    assert game.n_guesses() == 1


def test_correct_guess_recorded_in_history() -> None:
    game = MastermindGame(secret_idx=7)
    game.guess(7)
    assert len(game.history) == 1
    guess_idx, feedback = game.history[0]
    assert guess_idx == 7
    assert feedback == (N_PEGS, 0)


# ---------------------------------------------------------------------------
# Incorrect guess
# ---------------------------------------------------------------------------


def test_incorrect_guess_not_solved() -> None:
    game = MastermindGame(secret_idx=0)
    wrong = find_wrong_idx(0)
    game.guess(wrong)
    assert game.is_solved() is False


def test_incorrect_guess_history_one_entry() -> None:
    game = MastermindGame(secret_idx=0)
    wrong = find_wrong_idx(0)
    game.guess(wrong)
    assert len(game.history) == 1


def test_incorrect_guess_returns_valid_feedback() -> None:
    game = MastermindGame(secret_idx=0)
    wrong = find_wrong_idx(0)
    blacks, whites = game.guess(wrong)
    assert 0 <= blacks <= N_PEGS
    assert 0 <= whites <= N_PEGS
    assert blacks + whites <= N_PEGS
    # An incorrect guess cannot return N_PEGS blacks
    assert blacks < N_PEGS


# ---------------------------------------------------------------------------
# History integrity
# ---------------------------------------------------------------------------


def test_history_entries_are_correct_structure() -> None:
    game = MastermindGame(secret_idx=10)
    game.guess(5)
    game.guess(20)
    for entry in game.history:
        guess_idx, feedback = entry
        assert isinstance(guess_idx, int)
        assert isinstance(feedback, tuple)
        assert len(feedback) == 2


def test_history_grows_correctly() -> None:
    game = MastermindGame(secret_idx=100)
    assert len(game.history) == 0
    game.guess(0)
    assert len(game.history) == 1
    game.guess(1)
    assert len(game.history) == 2
    game.guess(2)
    assert len(game.history) == 3


def test_history_guess_indices_match() -> None:
    game = MastermindGame(secret_idx=100)
    guesses = [0, 50, 200]
    for g in guesses:
        game.guess(g)
    for i, (g_idx, _) in enumerate(game.history):
        assert g_idx == guesses[i]


def test_n_guesses_matches_history_length() -> None:
    game = MastermindGame(secret_idx=50)
    for g in [0, 1, 2]:
        game.guess(g)
    assert game.n_guesses() == len(game.history)


# ---------------------------------------------------------------------------
# Reset
# ---------------------------------------------------------------------------


def test_reset_clears_history() -> None:
    game = MastermindGame(secret_idx=0)
    game.guess(1)
    game.guess(2)
    game.reset()
    assert game.history == []
    assert game.n_guesses() == 0


def test_reset_resets_solved_state() -> None:
    game = MastermindGame(secret_idx=0)
    game.guess(0)  # correct guess
    assert game.is_solved() is True
    game.reset()
    assert game.is_solved() is False


def test_reset_with_specific_secret() -> None:
    game = MastermindGame(secret_idx=0)
    game.reset(secret_idx=42)
    assert game.secret_idx == 42


def test_reset_none_assigns_valid_secret() -> None:
    game = MastermindGame(secret_idx=0)
    game.reset()
    assert 0 <= game.secret_idx < N_CODES


def test_reset_none_can_change_secret() -> None:
    # Over many resets at least one should differ (probabilistic — essentially certain)
    game = MastermindGame(secret_idx=0)
    secrets = set()
    for _ in range(20):
        game.reset()
        secrets.add(game.secret_idx)
    # With 1296 possibilities and 20 trials, >1 value is virtually certain
    assert len(secrets) > 1


# ---------------------------------------------------------------------------
# Guard: guess after solved raises ValueError
# ---------------------------------------------------------------------------


def test_guess_after_solved_raises_value_error() -> None:
    game = MastermindGame(secret_idx=42)
    game.guess(42)  # correct guess → solved
    with pytest.raises(ValueError):
        game.guess(42)


def test_guess_after_solved_raises_on_different_guess_too() -> None:
    game = MastermindGame(secret_idx=42)
    game.guess(42)
    with pytest.raises(ValueError):
        game.guess(0)


# ---------------------------------------------------------------------------
# Determinism
# ---------------------------------------------------------------------------


def test_determinism_same_secret_same_feedback() -> None:
    game1 = MastermindGame(secret_idx=42)
    game2 = MastermindGame(secret_idx=42)
    fb1 = game1.guess(10)
    fb2 = game2.guess(10)
    assert fb1 == fb2


def test_determinism_reset_to_same_secret() -> None:
    game = MastermindGame(secret_idx=42)
    fb_first = game.guess(10)
    game.reset(secret_idx=42)
    fb_second = game.guess(10)
    assert fb_first == fb_second


def test_different_secrets_may_differ() -> None:
    # Use guess_idx=1 → code (0,0,0,1).
    # vs secret 0 (0,0,0,0): 3 blacks → (3, 0)
    # vs secret 1 (0,0,0,1): 4 blacks → (4, 0)  — guaranteed to differ.
    game = MastermindGame(secret_idx=0)
    fb0 = game.guess(1)
    game.reset(secret_idx=1)
    fb1 = game.guess(1)
    assert fb0 != fb1


# ---------------------------------------------------------------------------
# secret_idx property is read-only view
# ---------------------------------------------------------------------------


def test_secret_idx_property_type() -> None:
    game = MastermindGame(secret_idx=0)
    assert isinstance(game.secret_idx, int)


def test_history_property_type() -> None:
    game = MastermindGame(secret_idx=0)
    assert isinstance(game.history, list)
