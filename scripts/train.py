from __future__ import annotations

import random
from pathlib import Path
from typing import Any

import hydra
import numpy as np
import torch
from omegaconf import DictConfig
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor

from mastermind.agents.base_agent import BaseAgent
from mastermind.env.mastermind_env import MastermindEnv
from mastermind.evaluation.benchmarks import run_benchmark
from mastermind.evaluation.metrics import compute_metrics


class _PPOAdapter(BaseAgent):
    """Thin wrapper so a trained MaskablePPO can be used as a BaseAgent."""

    def __init__(self, model: MaskablePPO) -> None:
        self._model = model

    def select_action(self, obs: np.ndarray, action_masks: np.ndarray) -> int:
        action, _ = self._model.predict(
            obs, action_masks=action_masks, deterministic=True
        )
        return int(action)


class _MastermindEvalCallback(BaseCallback):
    """Runs benchmark + logs metrics to W&B at regular intervals."""

    def __init__(
        self,
        eval_env: MastermindEnv,
        eval_freq: int,
        n_eval_episodes: int,
        use_wandb: bool,
        verbose: int = 1,
    ) -> None:
        super().__init__(verbose=verbose)
        self._eval_env = eval_env
        self._eval_freq = eval_freq
        self._n_eval_episodes = n_eval_episodes
        self._use_wandb = use_wandb

    def _on_step(self) -> bool:
        if self.n_calls % self._eval_freq != 0:
            return True

        model: MaskablePPO = self.model  # type: ignore[assignment]
        adapter = _PPOAdapter(model)
        results = run_benchmark(adapter, self._eval_env, self._n_eval_episodes)
        metrics = compute_metrics(results)

        if self.verbose >= 1:
            print(
                f"[eval] step={self.num_timesteps}"
                f"  avg_guesses={metrics['avg_guesses']:.3f}"
                f"  win_rate={metrics['win_rate']:.3f}"
                f"  worst_case={metrics['worst_case_guesses']}"
            )

        if self._use_wandb:
            import wandb

            wandb.log(
                {
                    "eval/avg_guesses": metrics["avg_guesses"],
                    "eval/win_rate": metrics["win_rate"],
                    "eval/worst_case_guesses": metrics["worst_case_guesses"],
                },
                step=self.num_timesteps,
            )
        return True


def train(cfg: DictConfig) -> None:
    """Core training logic — callable from tests or the Hydra entry point."""
    seed: int = int(cfg.training.seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    env_config: dict[str, Any] = {
        "n_colors": int(cfg.env.n_colors),
        "n_pegs": int(cfg.env.n_pegs),
        "max_steps": int(cfg.env.max_steps),
        "reward_variant": str(cfg.env.reward_variant),
        "win_bonus": float(cfg.env.win_bonus),
        "step_penalty": float(cfg.env.step_penalty),
        "lose_penalty": float(cfg.env.lose_penalty),
    }
    train_env: MastermindEnv = MastermindEnv(config=env_config)
    wrapped_env: Monitor[np.ndarray, np.intp] = Monitor(train_env)

    eval_env: MastermindEnv = MastermindEnv(config=env_config)

    use_wandb: bool = bool(cfg.wandb.enabled)
    run: Any = None
    if use_wandb:
        from omegaconf import OmegaConf  # noqa: I001

        import wandb

        tags: list[str] = list(cfg.wandb.tags) if cfg.wandb.tags else []
        entity: str | None = str(cfg.wandb.entity) if cfg.wandb.entity else None
        run = wandb.init(
            project=str(cfg.wandb.project),
            entity=entity,
            tags=tags,
            config=OmegaConf.to_container(cfg, resolve=True),  # type: ignore[arg-type]
        )

    model = MaskablePPO(
        policy="MlpPolicy",
        env=wrapped_env,
        learning_rate=float(cfg.ppo.learning_rate),
        n_steps=int(cfg.ppo.n_steps),
        batch_size=int(cfg.ppo.batch_size),
        n_epochs=int(cfg.ppo.n_epochs),
        gamma=float(cfg.ppo.gamma),
        gae_lambda=float(cfg.ppo.gae_lambda),
        clip_range=float(cfg.ppo.clip_range),
        ent_coef=float(cfg.ppo.ent_coef),
        vf_coef=float(cfg.ppo.vf_coef),
        max_grad_norm=float(cfg.ppo.max_grad_norm),
        seed=seed,
        verbose=0,
    )

    callback = _MastermindEvalCallback(
        eval_env=eval_env,
        eval_freq=int(cfg.training.eval_freq),
        n_eval_episodes=int(cfg.training.n_eval_episodes),
        use_wandb=use_wandb,
    )

    model.learn(
        total_timesteps=int(cfg.training.total_timesteps),
        callback=callback,
    )

    output_dir = Path(str(cfg.training.output_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    model.save(str(output_dir / "model"))

    if use_wandb and run is not None:
        run.finish()


@hydra.main(
    config_path="../configs/train",
    config_name="ppo_baseline",
    version_base=None,
)
def main(cfg: DictConfig) -> None:
    train(cfg)


if __name__ == "__main__":
    main()
