"""Matplotlib visualisations for the evaluation report."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

_PALETTE = ["#4C72B0", "#DD8452", "#55A868", "#C44E52"]


def plot_guess_distribution(
    results_per_agent: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    """Grouped bar chart: normalised guess-count distribution for every agent."""
    agent_names = list(results_per_agent.keys())
    n_agents = len(agent_names)

    all_counts: set[int] = set()
    for r in results_per_agent.values():
        all_counts.update(r["guess_counts"])
    x_vals = sorted(all_counts)
    bar_width = 0.8 / n_agents

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (name, results) in enumerate(results_per_agent.items()):
        counts = results["guess_counts"]
        n = len(counts)
        freq = [counts.count(k) / n for k in x_vals]
        offsets = np.array(x_vals, dtype=float) + (i - n_agents / 2 + 0.5) * bar_width
        ax.bar(
            offsets,
            freq,
            width=bar_width,
            label=name,
            color=_PALETTE[i % len(_PALETTE)],
            alpha=0.87,
        )

    ax.set_xlabel("Number of Guesses")
    ax.set_ylabel("Fraction of Episodes")
    ax.set_title("Guess Count Distribution by Agent")
    ax.set_xticks(x_vals)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(output_dir / "guess_distribution.png", dpi=150)
    plt.close(fig)


def plot_avg_guesses_comparison(
    metrics_per_agent: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    """Horizontal bar chart: mean guesses per agent."""
    names = list(metrics_per_agent.keys())
    avgs = [metrics_per_agent[n]["avg_guesses"] for n in names]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(
        names,
        avgs,
        color=[_PALETTE[i % len(_PALETTE)] for i in range(len(names))],
    )
    ax.set_xlabel("Average Number of Guesses")
    ax.set_title("Average Guesses Comparison")
    ax.bar_label(bars, fmt="%.3f", padding=5)
    ax.set_xlim(0, max(avgs) * 1.18)
    ax.grid(axis="x", linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(output_dir / "avg_guesses_comparison.png", dpi=150)
    plt.close(fig)


def plot_win_rate_comparison(
    metrics_per_agent: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    """Vertical bar chart: win rate (%) per agent with a 95 % threshold line."""
    names = list(metrics_per_agent.keys())
    rates = [metrics_per_agent[n]["win_rate"] * 100.0 for n in names]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(
        names,
        rates,
        color=[_PALETTE[i % len(_PALETTE)] for i in range(len(names))],
    )
    ax.set_ylabel("Win Rate (%)")
    ax.set_title("Win Rate Comparison")
    ax.set_ylim(0, 113)
    ax.bar_label(bars, fmt="%.1f%%", padding=4)
    ax.axhline(
        y=95,
        color="red",
        linestyle="--",
        linewidth=1.2,
        alpha=0.75,
        label="95 % deployment threshold",
    )
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(output_dir / "win_rate_comparison.png", dpi=150)
    plt.close(fig)


def plot_worst_case_distribution(
    results_per_agent: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    """Grouped bar chart: fraction of episodes requiring each possible guess count.

    Emphasises the high-guess tail — the worst-case behaviour of each agent.
    """
    agent_names = list(results_per_agent.keys())
    n_agents = len(agent_names)

    all_counts: set[int] = set()
    for r in results_per_agent.values():
        all_counts.update(r["guess_counts"])
    x_vals = sorted(all_counts)
    bar_width = 0.8 / n_agents

    fig, ax = plt.subplots(figsize=(12, 6))
    for i, (name, results) in enumerate(results_per_agent.items()):
        counts = results["guess_counts"]
        n = len(counts)
        freq = [counts.count(k) / n for k in x_vals]
        offsets = np.array(x_vals, dtype=float) + (i - n_agents / 2 + 0.5) * bar_width
        ax.bar(
            offsets,
            freq,
            width=bar_width,
            label=name,
            color=_PALETTE[i % len(_PALETTE)],
            alpha=0.87,
        )

    ax.set_xlabel("Number of Guesses")
    ax.set_ylabel("Fraction of Episodes")
    ax.set_title("Worst-Case Distribution (Episodes per Guess Count)")
    ax.set_xticks(x_vals)
    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.45)
    fig.tight_layout()
    fig.savefig(output_dir / "worst_case_distribution.png", dpi=150)
    plt.close(fig)
