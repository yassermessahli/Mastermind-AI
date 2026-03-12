import numpy as np
import pytest

from mastermind.agents.knuth_agent import KnuthAgent
from mastermind.engine.codes import CODE_TO_IDX, N_CODES
from mastermind.env.mastermind_env import MastermindEnv


@pytest.fixture(scope="module")
def env() -> MastermindEnv:
    return MastermindEnv()


@pytest.fixture
def agent() -> KnuthAgent:
    return KnuthAgent()


@pytest.fixture
def dummy_obs() -> np.ndarray:
    return np.zeros(262, dtype=np.float32)


def test_returns_valid_action_index(agent: KnuthAgent, dummy_obs: np.ndarray) -> None:
    mask = np.ones(N_CODES, dtype=np.bool_)
    action = agent.select_action(dummy_obs, mask)
    assert 0 <= action < N_CODES


def test_first_guess_is_canonical_opener(
    agent: KnuthAgent, dummy_obs: np.ndarray
) -> None:
    mask = np.ones(N_CODES, dtype=np.bool_)
    assert agent.select_action(dummy_obs, mask) == CODE_TO_IDX[(0, 0, 1, 1)]


def test_solves_in_five_or_fewer_guesses(env: MastermindEnv) -> None:
    agent = KnuthAgent()
    obs, _ = env.reset(seed=123)
    agent.reset()
    terminated = truncated = False
    guesses = 0
    while not (terminated or truncated):
        action = agent.select_action(obs, env.action_masks())
        obs, _, terminated, truncated, _ = env.step(action)  # type: ignore[arg-type]
        guesses += 1
    assert terminated
    assert guesses <= 5


def test_selects_single_remaining_consistent_code(
    agent: KnuthAgent, dummy_obs: np.ndarray
) -> None:
    mask = np.zeros(N_CODES, dtype=np.bool_)
    mask[42] = True
    # First move must be consumed so Knuth skips the opener
    agent.select_action(dummy_obs, np.ones(N_CODES, dtype=np.bool_))
    action = agent.select_action(dummy_obs, mask)
    assert action == 42
