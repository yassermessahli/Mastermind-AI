"""CLI tool for manually playing a Mastermind game.

Usage:
    uv run python -m mastermind.engine.play
    uv run python -m mastermind.engine.play --max-guesses 10
    uv run python -m mastermind.engine.play --secret 1 2 3 4  # known secret
"""

import argparse

from mastermind.engine.codes import ALL_CODES, CODE_TO_IDX, N_CODES, N_COLORS, N_PEGS
from mastermind.engine.game import MastermindGame


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Play Mastermind in the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            f"Colors: 0–{N_COLORS - 1}  |  Pegs: {N_PEGS}  |  Total codes: {N_CODES}"
        ),
    )
    parser.add_argument(
        "--max-guesses",
        type=int,
        default=8,
        metavar="N",
        help="Maximum number of guesses allowed (default: 8)",
    )
    parser.add_argument(
        "--secret",
        nargs=N_PEGS,
        type=int,
        metavar="C",
        help=(
            f"Fix the secret code for testing, e.g. --secret 0 1 2 3"
            f" (each 0–{N_COLORS - 1})"
        ),
    )
    return parser.parse_args()


def parse_guess(raw: str) -> tuple[int, ...] | None:
    """Parse a space- or comma-separated string into a code tuple, or return None."""
    parts = raw.replace(",", " ").split()
    if len(parts) != N_PEGS:
        return None
    try:
        values = tuple(int(p) for p in parts)
    except ValueError:
        return None
    if not all(0 <= v < N_COLORS for v in values):
        return None
    return values


def main() -> None:
    args = parse_args()

    # Resolve secret index
    secret_idx: int | None = None
    if args.secret is not None:
        secret_code = tuple(int(v) for v in args.secret)
        if not all(0 <= v < N_COLORS for v in secret_code):
            print(f"Error: secret values must be in 0–{N_COLORS - 1}.")
            raise SystemExit(1)
        secret_idx = CODE_TO_IDX[secret_code]

    game = MastermindGame(secret_idx=secret_idx)
    max_guesses: int = args.max_guesses

    print(
        f"Mastermind — {N_PEGS} pegs, colors 0–{N_COLORS - 1},"
        f" max {max_guesses} guesses"
    )
    print(f"Enter your guess as {N_PEGS} space-separated digits, e.g.: 0 1 2 3")
    if args.secret:
        print(f"[DEBUG] Secret: {ALL_CODES[game.secret_idx]}")
    print()

    while game.n_guesses() < max_guesses:
        remaining = max_guesses - game.n_guesses()
        try:
            raw = input(
                f"Guess {game.n_guesses() + 1}/{max_guesses} ({remaining} left): "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted.")
            return

        if not raw:
            continue

        guess = parse_guess(raw)
        if guess is None:
            print(
                f"  Invalid input. Enter {N_PEGS} integers each in 0–{N_COLORS - 1}, "
                "separated by spaces."
            )
            continue

        guess_idx = CODE_TO_IDX[guess]
        blacks, whites = game.guess(guess_idx)

        print(f"  Feedback: {blacks} black, {whites} white")

        if game.is_solved():
            print(f"\nSolved in {game.n_guesses()} guess(es)!")
            return

        print()

    print(f"\nOut of guesses. The secret was: {ALL_CODES[game.secret_idx]}")


if __name__ == "__main__":
    main()
