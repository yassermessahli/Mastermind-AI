"""W&B sweep entry point — wraps train.py for hyperparameter search."""

from __future__ import annotations  # noqa: I001

import sys
from pathlib import Path
from typing import Any

import yaml
from omegaconf import DictConfig, OmegaConf

import wandb

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scripts.train import train  # noqa: E402

BASE_CONFIG = ROOT / "configs" / "train" / "ppo_baseline.yaml"
SWEEP_CONFIG = ROOT / "configs" / "sweep" / "ppo_sweep.yaml"
REWARD_DIR = ROOT / "configs" / "reward"

PPO_KEYS = {
    "learning_rate",
    "n_steps",
    "batch_size",
    "n_epochs",
    "ent_coef",
    "gae_lambda",
    "clip_range",
    "vf_coef",
    "max_grad_norm",
}

TRAINING_KEYS = {
    "total_timesteps",
    "eval_freq",
    "n_eval_episodes",
    "seed",
}


def _load_reward_params(variant: str) -> dict[str, Any]:
    """Load reward parameters from the variant YAML file."""
    reward_cfg = OmegaConf.load(str(REWARD_DIR / f"{variant}.yaml"))
    assert isinstance(reward_cfg, DictConfig)
    return {
        "reward_variant": str(reward_cfg.reward_variant),
        "win_bonus": float(reward_cfg.win_bonus),
        "step_penalty": float(reward_cfg.step_penalty),
        "lose_penalty": float(reward_cfg.lose_penalty),
    }


def _build_config(sweep_params: dict[str, Any]) -> DictConfig:
    """Merge sweep parameters into the baseline training config."""
    base_cfg = OmegaConf.load(str(BASE_CONFIG))
    assert isinstance(base_cfg, DictConfig)

    overrides: dict[str, Any] = {"ppo": {}, "env": {}, "training": {}}

    for key in PPO_KEYS:
        if key in sweep_params:
            overrides["ppo"][key] = sweep_params[key]

    for key in TRAINING_KEYS:
        if key in sweep_params:
            overrides["training"][key] = sweep_params[key]

    if "reward_variant" in sweep_params:
        reward_params = _load_reward_params(str(sweep_params["reward_variant"]))
        overrides["env"].update(reward_params)

    run_name = (wandb.run.name or "unknown") if wandb.run else "unknown"
    overrides["training"]["output_dir"] = str(ROOT / "outputs" / "sweep" / run_name)
    overrides["wandb"] = {"enabled": True}

    cfg = OmegaConf.merge(base_cfg, overrides)
    assert isinstance(cfg, DictConfig)
    return cfg


def sweep_train() -> None:
    """Single sweep trial — called by wandb.agent for each run."""
    wandb.init()
    cfg = _build_config(dict(wandb.config))
    train(cfg)


def main() -> None:
    """Create sweep from config and launch the agent."""
    with open(SWEEP_CONFIG) as f:
        sweep_config: dict[str, Any] = yaml.safe_load(f)

    project = str(
        OmegaConf.load(str(BASE_CONFIG)).wandb.project  # type: ignore[union-attr]
    )
    sweep_id: str = wandb.sweep(sweep_config, project=project)

    run_cap: int = int(sweep_config.get("run_cap", 20))
    wandb.agent(sweep_id, function=sweep_train, count=run_cap)


if __name__ == "__main__":
    main()
