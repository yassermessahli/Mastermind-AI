import numpy as np
import pytest

from mastermind.agents.random_agent import RandomAgent
from mastermind.engine.codes import N_CODES


@pytest.fixture
def agent() -> RandomAgent:
    return RandomAgent()


@pytest.fixture
def dummy_obs() -> np.ndarray:
    return np.zeros(262, dtype=np.float32)


def test_returns_valid_action_index(agent: RandomAgent, dummy_obs: np.ndarray) -> None:
    mask = np.ones(N_CODES, dtype=np.bool_)
    action = agent.select_action(dummy_obs, mask)
    assert 0 <= action < N_CODES


def test_ignores_mask(agent: RandomAgent, dummy_obs: np.ndarray) -> None:
    # Only index 0 is valid — random agent ignores the mask and selects freely
    mask = np.zeros(N_CODES, dtype=np.bool_)
    mask[0] = True
    actions = {agent.select_action(dummy_obs, mask) for _ in range(200)}
    assert len(actions) > 1


def test_no_crash_on_any_obs(agent: RandomAgent) -> None:
    rng = np.random.default_rng(0)
    for _ in range(20):
        obs = rng.random(262).astype(np.float32)
        mask = rng.integers(0, 2, size=N_CODES).astype(np.bool_)
        action = agent.select_action(obs, mask)
        assert 0 <= action < N_CODES


def test_nondeterministic(agent: RandomAgent, dummy_obs: np.ndarray) -> None:
    mask = np.ones(N_CODES, dtype=np.bool_)
    actions = {agent.select_action(dummy_obs, mask) for _ in range(50)}
    assert len(actions) > 1
