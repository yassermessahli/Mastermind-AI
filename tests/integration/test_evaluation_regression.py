"""Regression gate: RL agent must beat baselines on three quality metrics.

The test discovers a local sweep model automatically (in priority order):
  1. SWEEP_ID env var   → outputs/sweep/$SWEEP_ID/model.zip
  2. Preferred runs     → best-known sweep IDs from scripts/run_bests.sh
  3. Auto-discover      → last alphabetically-sorted outputs/sweep/*/model.zip
  4. No model found     → test suite is skipped (never fails CI on a clean clone)
"""

from __future__ import annotations

import glob
import os
from pathlib import Path
from typing import Any

import numpy as np
import pytest
from sb3_contrib import MaskablePPO

from mastermind.agents.base_agent import BaseAgent
from mastermind.agents.consistent_agent import ConsistentAgent
from mastermind.agents.knuth_agent import KnuthAgent
from mastermind.env.mastermind_env import MastermindEnv
from mastermind.evaluation.benchmarks import run_benchmark
from mastermind.evaluation.metrics import compute_metrics

N_EVAL = 500


class _PPOAdapter(BaseAgent):
    def __init__(self, model: MaskablePPO) -> None:
        self._model = model

    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        action, _ = self._model.predict(
            obs, action_masks=action_masks, deterministic=True
        )
        return int(action)


_PREFERRED_SWEEP_IDS = [
    "rosy-sweep-30",
    "fluent-sweep-18",
    "glowing-sweep-29",
    "hearty-sweep-20",
    "earnest-sweep-11",
]


def _find_model_path() -> Path | None:
    """Return path to the best available local model, or None.

    Priority:
      1. SWEEP_ID env var
      2. Best-known sweep runs (from scripts/run_bests.sh)
      3. Last alphabetically-sorted match in outputs/sweep/
    """
    sweep_id = os.environ.get("SWEEP_ID")
    if sweep_id:
        p = Path("outputs") / "sweep" / sweep_id / "model.zip"
        if p.exists():
            return p

    for preferred in _PREFERRED_SWEEP_IDS:
        p = Path("outputs") / "sweep" / preferred / "model.zip"
        if p.exists():
            return p

    matches = sorted(glob.glob(str(Path("outputs") / "sweep" / "*" / "model.zip")))
    if matches:
        return Path(matches[-1])
    return None


@pytest.fixture(scope="module")
def model_path() -> Path:
    p = _find_model_path()
    if p is None:
        pytest.skip("No local sweep model found — set SWEEP_ID or run a sweep first.")
    return p


_TRAIN_ENV_CONFIG = {"max_steps": 8}


@pytest.fixture(scope="module")
def eval_env() -> MastermindEnv:
    return MastermindEnv(config=_TRAIN_ENV_CONFIG)


@pytest.fixture(scope="module")
def rl_metrics(model_path: Path, eval_env: MastermindEnv) -> dict[str, Any]:
    model = MaskablePPO.load(str(model_path))
    agent = _PPOAdapter(model)
    return compute_metrics(run_benchmark(agent, eval_env, N_EVAL))


@pytest.fixture(scope="module")
def consistent_metrics(eval_env: MastermindEnv) -> dict[str, Any]:
    return compute_metrics(run_benchmark(ConsistentAgent(), eval_env, N_EVAL))


@pytest.fixture(scope="module")
def knuth_metrics(eval_env: MastermindEnv) -> dict[str, Any]:
    return compute_metrics(run_benchmark(KnuthAgent(), eval_env, N_EVAL))


def test_rl_beats_consistent_avg_guesses(
    rl_metrics: dict[str, Any],
    consistent_metrics: dict[str, Any],
) -> None:
    """RL agent must need fewer guesses on average than ConsistentAgent."""
    assert rl_metrics["avg_guesses"] < consistent_metrics["avg_guesses"], (
        f"RL avg_guesses={rl_metrics['avg_guesses']:.3f} must be < "
        f"ConsistentAgent avg_guesses={consistent_metrics['avg_guesses']:.3f}"
    )


def test_rl_win_rate_at_least_95_percent(rl_metrics: dict[str, Any]) -> None:
    """RL agent must win at least 95 % of games."""
    assert rl_metrics["win_rate"] >= 0.95, (
        f"RL win_rate={rl_metrics['win_rate']:.3f} < 0.95"
    )


def test_rl_worst_case_no_worse_than_knuth(
    rl_metrics: dict[str, Any],
    knuth_metrics: dict[str, Any],
) -> None:
    """RL worst-case guess count must not exceed Knuth's worst-case."""
    assert rl_metrics["worst_case_guesses"] <= knuth_metrics["worst_case_guesses"], (
        f"RL worst_case={rl_metrics['worst_case_guesses']} "
        f"> Knuth worst_case={knuth_metrics['worst_case_guesses']}"
    )
