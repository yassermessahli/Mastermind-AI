import numpy as np
import pytest

from mastermind.agents.consistent_agent import ConsistentAgent
from mastermind.engine.codes import N_CODES


@pytest.fixture
def agent() -> ConsistentAgent:
    return ConsistentAgent()


@pytest.fixture
def dummy_obs() -> np.ndarray:
    return np.zeros(262, dtype=np.float32)


def test_always_within_mask(agent: ConsistentAgent, dummy_obs: np.ndarray) -> None:
    rng = np.random.default_rng(42)
    for _ in range(30):
        mask = np.zeros(N_CODES, dtype=np.bool_)
        indices = rng.choice(N_CODES, size=50, replace=False)
        mask[indices] = True
        action = agent.select_action(dummy_obs, mask)
        assert mask[action]


def test_never_outside_mask(agent: ConsistentAgent, dummy_obs: np.ndarray) -> None:
    mask = np.zeros(N_CODES, dtype=np.bool_)
    mask[100:200] = True
    for _ in range(50):
        action = agent.select_action(dummy_obs, mask)
        assert 100 <= action < 200


def test_single_valid_always_selected(
    agent: ConsistentAgent, dummy_obs: np.ndarray
) -> None:
    mask = np.zeros(N_CODES, dtype=np.bool_)
    mask[42] = True
    for _ in range(20):
        assert agent.select_action(dummy_obs, mask) == 42


def test_reset_does_not_crash(agent: ConsistentAgent, dummy_obs: np.ndarray) -> None:
    mask = np.ones(N_CODES, dtype=np.bool_)
    agent.select_action(dummy_obs, mask)
    agent.reset()
    action = agent.select_action(dummy_obs, mask)
    assert 0 <= action < N_CODES
