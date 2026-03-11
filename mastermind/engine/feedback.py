"""Feedback computation — O(1) FEEDBACK_TABLE lookup.

The single public function ``compute_feedback`` is the only interface the rest
of the codebase should use to obtain (blacks, whites) for a guess/secret pair.
"""

from mastermind.engine.codes import FEEDBACK_TABLE


def compute_feedback(guess_idx: int, secret_idx: int) -> tuple[int, int]:
    """Return (blacks, whites) for the given guess and secret indices.

    Parameters
    ----------
    guess_idx:
        Index into ALL_CODES for the guessed code.
    secret_idx:
        Index into ALL_CODES for the secret code.

    Returns
    -------
    tuple[int, int]
        ``(blacks, whites)`` where blacks is the count of pegs that are the
        correct colour in the correct position, and whites is the count of
        pegs that are the correct colour in the wrong position.
    """
    entry = FEEDBACK_TABLE[guess_idx, secret_idx]
    return int(entry[0]), int(entry[1])
