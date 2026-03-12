from collections import Counter
from typing import Any


def compute_metrics(results: dict[str, Any]) -> dict[str, Any]:
    """Compute summary metrics from raw benchmark results.

    Returns a dict with:
    - avg_guesses: mean number of guesses per episode
    - win_rate: fraction of episodes solved
    - worst_case_guesses: maximum guesses in any episode
    - guess_distribution: count per number of guesses
    """
    guess_counts: list[int] = results["guess_counts"]
    wins: list[bool] = results["wins"]

    avg_guesses = sum(guess_counts) / len(guess_counts)
    win_rate = sum(wins) / len(wins)
    worst_case_guesses = max(guess_counts)
    guess_distribution = dict(Counter(guess_counts))

    return {
        "avg_guesses": avg_guesses,
        "win_rate": win_rate,
        "worst_case_guesses": worst_case_guesses,
        "guess_distribution": guess_distribution,
    }
