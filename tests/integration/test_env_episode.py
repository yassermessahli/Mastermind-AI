import numpy as np

from mastermind.engine.codes import N_CODES, N_PEGS
from mastermind.env.mastermind_env import MastermindEnv

OBS_DIM = 262  # 10 * (4 * 6 + 2) + 2


def test_reset_returns_valid_obs_and_info() -> None:
    env = MastermindEnv()
    obs, info = env.reset(seed=42)
    assert obs.shape == (OBS_DIM,)
    assert obs.dtype == np.float32
    assert info["consistent_remaining"] == N_CODES


def test_step_correct_guess_terminates() -> None:
    env = MastermindEnv()
    env.reset(seed=0)
    secret_idx = env._game.secret_idx
    obs, reward, terminated, truncated, info = env.step(secret_idx)
    assert terminated is True
    assert truncated is False
    assert reward > 0.0
    assert info["blacks"] == N_PEGS


def test_step_wrong_guess_continues() -> None:
    env = MastermindEnv()
    env.reset(seed=0)
    secret_idx = env._game.secret_idx
    wrong_idx = (secret_idx + 1) % N_CODES
    obs, reward, terminated, truncated, info = env.step(wrong_idx)
    assert terminated is False
    assert truncated is False
    assert info["consistent_remaining"] < N_CODES


def test_action_masks_shape_and_updates() -> None:
    env = MastermindEnv()
    env.reset(seed=0)
    masks = env.action_masks()
    assert masks.shape == (N_CODES,)
    assert masks.dtype == np.bool_
    assert int(masks.sum()) == N_CODES

    secret_idx = env._game.secret_idx
    wrong_idx = (secret_idx + 1) % N_CODES
    env.step(wrong_idx)
    masks_after = env.action_masks()
    assert masks_after.shape == (N_CODES,)
    assert int(masks_after.sum()) < N_CODES


def test_full_episode_cycle() -> None:
    env = MastermindEnv()
    obs, _ = env.reset(seed=7)
    assert obs.shape == (OBS_DIM,)
    terminated = truncated = False
    step_count = 0
    while not (terminated or truncated):
        masks = env.action_masks()
        action = int(np.where(masks)[0][0])
        obs, reward, terminated, truncated, info = env.step(action)
        assert obs.shape == (OBS_DIM,)
        assert isinstance(reward, float)
        step_count += 1
    assert step_count > 0
