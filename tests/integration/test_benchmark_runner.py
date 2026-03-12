import pytest

from mastermind.agents.consistent_agent import ConsistentAgent
from mastermind.agents.knuth_agent import KnuthAgent
from mastermind.agents.random_agent import RandomAgent
from mastermind.env.mastermind_env import MastermindEnv
from mastermind.evaluation.benchmarks import run_benchmark
from mastermind.evaluation.metrics import compute_metrics

N_EPISODES = 20


@pytest.fixture(scope="module")
def env() -> MastermindEnv:
    return MastermindEnv()


def test_run_benchmark_completes_all_agents(env: MastermindEnv) -> None:
    for agent_class in [RandomAgent, ConsistentAgent, KnuthAgent]:
        results = run_benchmark(agent_class(), env, n_episodes=N_EPISODES)
        assert len(results["guess_counts"]) == N_EPISODES
        assert len(results["wins"]) == N_EPISODES
        assert len(results["total_rewards"]) == N_EPISODES


def test_compute_metrics_returns_expected_keys(env: MastermindEnv) -> None:
    results = run_benchmark(RandomAgent(), env, n_episodes=20)
    metrics = compute_metrics(results)
    assert "avg_guesses" in metrics
    assert "win_rate" in metrics
    assert "worst_case_guesses" in metrics
    assert "guess_distribution" in metrics


def test_random_averages_more_guesses_than_consistent(env: MastermindEnv) -> None:
    random_metrics = compute_metrics(
        run_benchmark(RandomAgent(), env, n_episodes=N_EPISODES)
    )
    consistent_metrics = compute_metrics(
        run_benchmark(ConsistentAgent(), env, n_episodes=N_EPISODES)
    )
    assert random_metrics["avg_guesses"] > consistent_metrics["avg_guesses"]


def test_knuth_worst_case_at_most_five(env: MastermindEnv) -> None:
    results = run_benchmark(KnuthAgent(), env, n_episodes=N_EPISODES)
    metrics = compute_metrics(results)
    assert metrics["worst_case_guesses"] <= 5


def test_knuth_perfect_win_rate(env: MastermindEnv) -> None:
    results = run_benchmark(KnuthAgent(), env, n_episodes=N_EPISODES)
    metrics = compute_metrics(results)
    assert metrics["win_rate"] == 1.0
