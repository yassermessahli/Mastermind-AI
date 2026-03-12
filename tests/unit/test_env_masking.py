import numpy as np

from mastermind.engine.codes import CODE_TO_IDX, N_CODES, N_PEGS
from mastermind.engine.feedback import compute_feedback
from mastermind.env.masking import (
    get_action_masks,
    get_initial_consistent_set,
    update_consistent_set,
)

# Initial consistent set


def test_initial_consistent_set_size_and_contents() -> None:
    s = get_initial_consistent_set()
    assert len(s) == N_CODES
    assert min(s) == 0
    assert max(s) == N_CODES - 1
    assert s == set(range(N_CODES))


# update_consistent_set — elimination


def test_update_eliminates_inconsistent_codes() -> None:
    initial = get_initial_consistent_set()
    guess_idx = CODE_TO_IDX[(0, 0, 0, 0)]
    # Feedback (0, 0) means no colors match — (0,0,0,0) itself is eliminated
    updated = update_consistent_set(initial, guess_idx, (0, 0))
    assert guess_idx not in updated
    assert len(updated) < N_CODES


def test_update_correct_guess_leaves_only_secret() -> None:
    initial = get_initial_consistent_set()
    secret_idx = CODE_TO_IDX[(0, 0, 0, 0)]
    # Guessing the exact secret yields blacks=N_PEGS → only the secret is consistent
    updated = update_consistent_set(initial, secret_idx, (N_PEGS, 0))
    assert updated == {secret_idx}


# update_consistent_set — secret invariant


def test_update_always_retains_secret() -> None:
    initial = get_initial_consistent_set()
    cases = [
        ((0, 0, 0, 0), (1, 2, 3, 4)),
        ((0, 1, 2, 3), (3, 2, 1, 0)),
        ((5, 5, 5, 5), (0, 0, 0, 0)),
    ]
    for guess_code, secret_code in cases:
        guess_idx = CODE_TO_IDX[guess_code]
        secret_idx = CODE_TO_IDX[secret_code]
        feedback = compute_feedback(guess_idx, secret_idx)
        updated = update_consistent_set(initial, guess_idx, feedback)
        assert (
            secret_idx in updated
        ), f"secret {secret_code} dropped after guess {guess_code} feedback {feedback}"


# update_consistent_set — immutability


def test_update_does_not_mutate_input() -> None:
    initial = get_initial_consistent_set()
    snapshot = set(initial)
    guess_idx = CODE_TO_IDX[(0, 1, 2, 3)]
    feedback = compute_feedback(guess_idx, CODE_TO_IDX[(5, 4, 3, 2)])
    update_consistent_set(initial, guess_idx, feedback)
    assert initial == snapshot


# action masks


def test_action_masks_shape_and_dtype() -> None:
    mask = get_action_masks(get_initial_consistent_set())
    assert mask.shape == (N_CODES,)
    assert mask.dtype == np.bool_


def test_action_masks_true_count_matches_set() -> None:
    s = get_initial_consistent_set()
    mask = get_action_masks(s)
    assert int(mask.sum()) == len(s)


def test_action_masks_all_true_at_start() -> None:
    mask = get_action_masks(get_initial_consistent_set())
    assert mask.all()


# single code remaining


def test_single_code_remaining_mask() -> None:
    secret_idx = CODE_TO_IDX[(3, 1, 4, 2)]
    singleton = {secret_idx}
    mask = get_action_masks(singleton)
    assert int(mask.sum()) == 1
    assert mask[secret_idx]
