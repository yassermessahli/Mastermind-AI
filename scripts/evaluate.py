"""Evaluation entry point — benchmark the prod RL model against all baselines.

Usage (from project root):
    uv run python scripts/evaluate.py                           # auto-discover model
    uv run python scripts/evaluate.py sweep_id=rosy-sweep-30   # specific sweep run
    uv run python scripts/evaluate.py model_path=outputs/model.zip
    uv run python scripts/evaluate.py wandb.enabled=false       # skip W&B
"""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Any

import hydra
import numpy as np
from omegaconf import DictConfig
from sb3_contrib import MaskablePPO

from mastermind.agents.base_agent import BaseAgent
from mastermind.agents.consistent_agent import ConsistentAgent
from mastermind.agents.knuth_agent import KnuthAgent
from mastermind.agents.random_agent import RandomAgent
from mastermind.env.mastermind_env import MastermindEnv
from mastermind.evaluation.benchmarks import run_benchmark
from mastermind.evaluation.metrics import compute_metrics
from mastermind.evaluation.plots import (
    plot_avg_guesses_comparison,
    plot_guess_distribution,
    plot_win_rate_comparison,
    plot_worst_case_distribution,
)


class _PPOAdapter(BaseAgent):
    """Thin wrapper so a trained MaskablePPO satisfies the BaseAgent interface."""

    def __init__(self, model: MaskablePPO) -> None:
        self._model = model

    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        action, _ = self._model.predict(
            obs, action_masks=action_masks, deterministic=True
        )
        return int(action)


def _resolve_model_path(cfg: DictConfig) -> Path:
    """Return the model path from config, or auto-discover the first sweep model."""
    if cfg.model_path is not None:
        return Path(str(cfg.model_path))
    if cfg.sweep_id is not None:
        return Path("outputs") / "sweep" / str(cfg.sweep_id) / "model.zip"
    matches = sorted(glob.glob(str(Path("outputs") / "sweep" / "*" / "model.zip")))
    if not matches:
        raise FileNotFoundError(
            "No model found. Pass sweep_id=<id> or model_path=<path> via CLI."
        )
    return Path(matches[0])


def evaluate(cfg: DictConfig) -> dict[str, dict[str, Any]]:
    """Core evaluation logic — callable independently of the Hydra entry point."""
    model_path = _resolve_model_path(cfg)
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    model = MaskablePPO.load(str(model_path))

    env_config: dict[str, Any] = {
        "n_colors": int(cfg.env.n_colors),
        "n_pegs": int(cfg.env.n_pegs),
        "max_steps": int(cfg.env.max_steps),
        "reward_variant": str(cfg.env.reward_variant),
        "win_bonus": float(cfg.env.win_bonus),
        "step_penalty": float(cfg.env.step_penalty),
        "lose_penalty": float(cfg.env.lose_penalty),
    }
    env = MastermindEnv(config=env_config)
    n_episodes = int(cfg.evaluation.n_episodes)

    agents: dict[str, BaseAgent] = {
        "RandomAgent": RandomAgent(),
        "ConsistentAgent": ConsistentAgent(),
        "KnuthAgent": KnuthAgent(),
        "RLAgent": _PPOAdapter(model),
    }

    all_results: dict[str, dict[str, Any]] = {}
    all_metrics: dict[str, dict[str, Any]] = {}
    for name, agent in agents.items():
        results = run_benchmark(agent, env, n_episodes)
        all_results[name] = results
        all_metrics[name] = compute_metrics(results)

    _print_table(all_metrics)

    output_dir = Path(str(cfg.evaluation.output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)

    plot_guess_distribution(all_results, output_dir)
    plot_avg_guesses_comparison(all_metrics, output_dir)
    plot_win_rate_comparison(all_metrics, output_dir)
    plot_worst_case_distribution(all_results, output_dir)
    print(f"\nPlots saved → {output_dir}/")

    if cfg.wandb.enabled:
        _log_to_wandb(cfg, all_metrics, output_dir)

    return all_metrics


def _print_table(all_metrics: dict[str, dict[str, Any]]) -> None:
    col_w = (20, 14, 10, 12)
    sep = "─" * (sum(col_w) + 6)
    header = (
        f"{'Agent':<{col_w[0]}} {'avg_guesses':>{col_w[1]}} "
        f"{'win_rate':>{col_w[2]}} {'worst_case':>{col_w[3]}}"
    )
    print(f"\n{sep}\n{header}\n{sep}")
    for name, m in all_metrics.items():
        print(
            f"{name:<{col_w[0]}} {m['avg_guesses']:>{col_w[1]}.3f} "
            f"{m['win_rate']:>{col_w[2]}.3f} {m['worst_case_guesses']:>{col_w[3]}}"
        )
    print(sep)


def _log_to_wandb(
    cfg: DictConfig,
    all_metrics: dict[str, dict[str, Any]],
    output_dir: Path,
) -> None:
    import wandb

    entity = str(cfg.wandb.entity) if cfg.wandb.entity else None
    run = wandb.init(
        project=str(cfg.wandb.project),
        entity=entity,
        job_type="evaluation",
    )
    flat: dict[str, Any] = {}
    for name, m in all_metrics.items():
        flat[f"{name}/avg_guesses"] = m["avg_guesses"]
        flat[f"{name}/win_rate"] = m["win_rate"]
        flat[f"{name}/worst_case_guesses"] = m["worst_case_guesses"]
    wandb.log(flat)

    for stem in [
        "guess_distribution",
        "avg_guesses_comparison",
        "win_rate_comparison",
        "worst_case_distribution",
    ]:
        img_path = output_dir / f"{stem}.png"
        if img_path.exists():
            wandb.log({stem: wandb.Image(str(img_path))})

    run.finish()


@hydra.main(
    config_path="../configs/eval",
    config_name="evaluate",
    version_base=None,
)
def main(cfg: DictConfig) -> None:
    evaluate(cfg)


if __name__ == "__main__":
    main()
