import itertools

import numpy as np

from mastermind.agents.consistent_agent import ConsistentAgent

_agent = ConsistentAgent()


def all_codes_for(n_colors: int, n_pegs: int) -> list[tuple[int, ...]]:
    return list(itertools.product(range(n_colors), repeat=n_pegs))


def _raw_feedback(
    guess: tuple[int, ...], secret: tuple[int, ...], n_colors: int
) -> tuple[int, int]:
    blacks = sum(g == s for g, s in zip(guess, secret))
    whites = sum(min(guess.count(c), secret.count(c)) for c in range(n_colors)) - blacks
    return blacks, whites


def game_feedback(
    all_codes: list[tuple[int, ...]],
    guess_idx: int,
    secret_idx: int,
    n_colors: int,
) -> tuple[int, int]:
    return _raw_feedback(all_codes[guess_idx], all_codes[secret_idx], n_colors)


def filter_consistent_set(
    all_codes: list[tuple[int, ...]],
    consistent_set: list[int],
    guess_idx: int,
    blacks: int,
    whites: int,
    n_colors: int,
) -> list[int]:
    guess = all_codes[guess_idx]
    return [
        idx
        for idx in consistent_set
        if _raw_feedback(guess, all_codes[idx], n_colors) == (blacks, whites)
    ]


def get_ai_guess(
    consistent_set: list[int],
    n_colors: int,
    n_pegs: int,
) -> int:
    n_codes = n_colors**n_pegs
    mask = np.zeros(n_codes, dtype=np.bool_)
    indices = consistent_set if consistent_set else list(range(n_codes))
    mask[indices] = True
    return int(_agent.select_action(np.zeros(1, dtype=np.float32), mask))
