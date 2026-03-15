# MastermindAI — RL Agent for Mastermind

A reinforcement learning agent that learns to play Mastermind (4 pegs, 6 colors) using MaskablePPO. The agent optimizes average-case performance rather than worst-case (Knuth). A full-stack web app lets you play against the AI directly in the browser.

---

## Project Structure

```
mastermind-rl/
├── mastermind/          # Core Python package: engine, Gymnasium env, agents, evaluation
├── web/
│   ├── server/          # Django REST Framework backend
│   └── frontend/        # React + TypeScript + Vite frontend
├── scripts/             # train.py, evaluate.py, sweep.py, serve.py
├── configs/             # Hydra configs: training, reward variants, sweep
├── tests/               # unit/, integration/
├── docker/              # Dockerfile.backend, Dockerfile.frontend
├── docker-compose.yml   # Full stack: backend + frontend
└── docs/                # architecture.md, mdp_definition.md
```

---

## Quick Start

### Web App (Docker)

```bash
cp .env.example .env          # set DJANGO_SECRET_KEY
docker compose up --build
```

Open http://localhost:3000.

### RL Training

**Requirements**: Python 3.13, [uv](https://docs.astral.sh/uv/)

```bash
make install      # install all dependencies
make train        # train with default config
make evaluate     # benchmark against baselines
make serve        # start FastAPI prediction server
```

---

## Game Modes

### Codebreaker
You guess the secret code. After each guess the game shows black and white peg feedback. Black = correct color in correct position. White = correct color in wrong position. Guess correctly within the limit to win.

### Codekeeper
You pick a secret code in your head — never entered. The AI makes guesses. After each AI guess, you enter the correct black/white feedback. The AI uses your feedback to narrow down candidates and guess again. See how many guesses it takes the AI to crack your code.

---

## Baseline Benchmarks

| Agent           | Avg Guesses | Win Rate | Notes                  |
|-----------------|-------------|----------|------------------------|
| RandomAgent     | ~7–8        | low      | Floor — no constraints |
| ConsistentAgent | ~5–6        | medium   | Respects feedback      |
| KnuthAgent      | ≤5 (worst)  | 100%     | Minimax ceiling        |
| **RL Agent**    | **~4.3–4.5**| **~99%** | Target after training  |

---

## Screenshots

![Codebreaker](docs/screenshots/codebreaker.png)

*Screenshot placeholder — run the app to see the UI.*

---

## Tech Stack

| Concern               | Tool                         |
|-----------------------|------------------------------|
| Language (RL)         | Python 3.13                  |
| RL environment        | Gymnasium                    |
| RL algorithm          | MaskablePPO (sb3-contrib)    |
| Training tracking     | Weights & Biases             |
| Config management     | Hydra                        |
| Backend framework     | Django 5 + DRF               |
| Frontend framework    | React 18 + TypeScript + Vite |
| Styling               | Tailwind CSS                 |
| Deployment            | Docker + Nginx               |
| Dependency management | uv                           |
| Linting / formatting  | Ruff                         |
| Type checking         | Mypy                         |
| Testing               | Pytest + pytest-cov          |
| CI/CD                 | GitHub Actions               |

---

## Development

```bash
make lint           # ruff check .
make format         # ruff format .
make typecheck      # mypy mastermind/
make test           # pytest tests/
make test-cov       # pytest --cov=mastermind tests/

make backend-serve  # Django dev server on :8001
make frontend-dev   # Vite dev server on :5173
```
