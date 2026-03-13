import sys
from pathlib import Path
from typing import Any

import numpy as np
from omegaconf import DictConfig, OmegaConf

ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT))

from scripts.train import train  # noqa: E402

CONFIG_PATH = ROOT / "configs" / "train" / "ppo_baseline.yaml"
REWARD_DIR = ROOT / "configs" / "reward"


def _base_cfg(tmp_path: Path, extra: dict[str, Any] | None = None) -> DictConfig:
    cfg = OmegaConf.load(str(CONFIG_PATH))
    assert isinstance(cfg, DictConfig)
    base: dict[str, Any] = {
        "training": {
            "total_timesteps": 100,
            "eval_freq": 200,
            "n_eval_episodes": 5,
            "output_dir": str(tmp_path),
        },
        "ppo": {
            "n_steps": 32,
            "batch_size": 16,
        },
        "wandb": {"enabled": False},
    }
    cfg = OmegaConf.merge(cfg, base)
    assert isinstance(cfg, DictConfig)
    if extra:
        cfg = OmegaConf.merge(cfg, extra)
        assert isinstance(cfg, DictConfig)
    return cfg


def test_training_runs_100_steps_no_crash(tmp_path: Path) -> None:
    cfg = _base_cfg(tmp_path)
    train(cfg)
    model_files = list(tmp_path.glob("**/*.zip"))
    assert len(model_files) > 0


def test_maskableppo_uses_action_masks() -> None:
    from sb3_contrib import MaskablePPO
    from stable_baselines3.common.monitor import Monitor

    from mastermind.env.mastermind_env import MastermindEnv

    env_config: dict[str, Any] = {"max_steps": 8, "reward_variant": "sparse"}
    train_env = Monitor(MastermindEnv(env_config))  # type: ignore
    model = MaskablePPO("MlpPolicy", train_env, verbose=0, seed=42)

    test_env = MastermindEnv(env_config)
    obs, _ = test_env.reset(seed=0)

    selected: list[tuple[int, np.ndarray]] = []

    for _ in range(50):
        masks = test_env.action_masks()
        action, _ = model.predict(obs, action_masks=masks, deterministic=False)
        action_int = int(action)
        selected.append((action_int, masks.copy()))
        obs, _, terminated, truncated, _ = test_env.step(np.intp(action_int))
        if terminated or truncated:
            obs, _ = test_env.reset()

    for action_int, masks in selected:
        assert masks[action_int], f"Action {action_int} violates action mask"


def test_all_reward_variants_train_without_crash(tmp_path: Path) -> None:
    for variant in ["sparse", "step_penalty", "shaped", "information"]:
        reward_cfg = OmegaConf.load(str(REWARD_DIR / f"{variant}.yaml"))
        assert isinstance(reward_cfg, DictConfig)
        env_override: dict[str, Any] = {
            "env": {
                "reward_variant": str(reward_cfg.reward_variant),
                "win_bonus": float(reward_cfg.win_bonus),
                "step_penalty": float(reward_cfg.step_penalty),
                "lose_penalty": float(reward_cfg.lose_penalty),
            }
        }
        cfg = _base_cfg(tmp_path / variant, env_override)
        train(cfg)


def test_model_save_and_load(tmp_path: Path) -> None:
    from sb3_contrib import MaskablePPO

    from mastermind.env.mastermind_env import MastermindEnv

    cfg = _base_cfg(tmp_path)
    train(cfg)

    model_files = list(tmp_path.glob("**/*.zip"))
    assert len(model_files) > 0

    env = MastermindEnv(config={"max_steps": int(cfg.env.max_steps)})
    model = MaskablePPO.load(str(model_files[0]), env=env)

    obs, _ = env.reset(seed=1)
    masks = env.action_masks()
    action, _ = model.predict(obs, action_masks=masks, deterministic=True)
    assert 0 <= int(action) < 1296
