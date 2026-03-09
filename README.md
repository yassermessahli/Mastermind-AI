# MastermindAI — RL Agent for Mastermind

A reinforcement learning agent that learns to play the Mastermind board game (4 pegs, 6 colors) using MaskablePPO. The agent is trained to beat human expert players by optimizing average-case performance rather than worst-case (Knuth). The final deliverable is a FastAPI service deployed in Docker that a human player can play against.

---

## Setup

**Requirements**: Python 3.13, [uv](https://docs.astral.sh/uv/)

```bash
make install
```

---

## Quick Start

```bash
# Train the agent
make train

# Evaluate against baselines
make evaluate

# Start the API server
make serve
```

---

## Development

```bash
make lint        # ruff check .
make format      # ruff format .
make typecheck   # mypy mastermind/
make test        # pytest tests/
make test-unit   # pytest tests/unit/
make test-cov    # pytest --cov=mastermind tests/
```

---

## Project Structure

```
mastermind-rl/
│
├── mastermind/                   # Core package
│   ├── engine/
│   │   ├── codes.py              # ALL_CODES, CODE_TO_IDX, FEEDBACK_TABLE
│   │   ├── feedback.py           # compute_feedback() wrapping FEEDBACK_TABLE
│   │   └── game.py               # MastermindGame — stateful session
│   │
│   ├── env/
│   │   ├── mastermind_env.py     # Gymnasium env, step/reset/action_masks
│   │   ├── obs_encoder.py        # ObservationEncoder — Option C
│   │   └── masking.py            # Incremental consistent set + action_masks()
│   │
│   ├── agents/
│   │   ├── random_agent.py       # Fully random baseline
│   │   ├── consistent_agent.py   # Random but respects constraints
│   │   └── knuth_agent.py        # Minimax ceiling reference
│   │
│   ├── evaluation/
│   │   ├── benchmarks.py         # Run agent vs all baselines
│   │   ├── metrics.py            # avg_guesses, win_rate, worst_case_dist
│   │   └── plots.py              # Matplotlib result figures
│   │
│   └── api/
│       ├── main.py               # FastAPI application
│       ├── schemas.py            # Pydantic request/response models
│       └── agent_service.py      # Loads prod model, serves predictions
│
├── tests/
│   ├── unit/                     # Fast, isolated, no env/agent deps
│   ├── integration/              # Engine ↔ Env ↔ Masking
│   └── e2e/                      # Full API endpoint tests
│
├── configs/
│   ├── train/ppo_baseline.yaml
│   ├── reward/{sparse,step_penalty,shaped,information}.yaml
│   └── sweep/ppo_sweep.yaml
│
├── scripts/
│   ├── train.py
│   ├── evaluate.py
│   └── serve.py
│
├── docker/
│   ├── Dockerfile.train
│   ├── Dockerfile.serve
│   └── docker-compose.yaml
│
└── docs/
    └── mdp_definition.md
```

---

## Baseline Benchmarks

| Agent           | Avg Guesses | Win Rate | Notes                   |
|-----------------|-------------|----------|-------------------------|
| RandomAgent     | ~7–8        | low      | Floor — no constraints  |
| ConsistentAgent | ~5–6        | medium   | Respects feedback       |
| KnuthAgent      | ≤5 (worst)  | 100%     | Minimax ceiling         |
| **RL Agent**    | **~4.3–4.5**| **~99%** | Target after training   |

---

## Tech Stack

| Concern               | Tool                      |
|-----------------------|---------------------------|
| Language              | Python 3.13               |
| RL environment        | Gymnasium                 |
| RL algorithm          | MaskablePPO (sb3-contrib) |
| Training tracking     | Weights & Biases          |
| Config management     | Hydra                     |
| API                   | FastAPI + Pydantic v2     |
| Deployment            | Docker                    |
| Dependency management | uv                        |
| Linting / formatting  | Ruff                      |
| Type checking         | Mypy                      |
| Testing               | Pytest + pytest-cov       |
| CI/CD                 | GitHub Actions            |
