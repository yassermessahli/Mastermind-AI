# Architecture

## Layer Diagram

```
mastermind package (Python)
    │
    │  game engine, feedback table, Gymnasium env, agents
    │
    ▼
Django backend  (web/server/)
    │
    │  REST API over Django sessions — no database
    │
    ▼
React frontend  (web/frontend/)
    │
    │  SPA served by Nginx; /api/ proxied to backend
    │
    ▼
Docker Compose  (docker-compose.yml)
    │
    │  backend container (Gunicorn :8001, internal)
    │  frontend container (Nginx :3000, public)
```

The `mastermind` package is installed as a wheel inside the backend container. The frontend container has no Python — it is a static Nginx build.

---

## Why FEEDBACK_TABLE

Computing black/white feedback naively requires scanning all 4 pegs twice per pair. With 1296 possible codes, an agent inside a training loop calls feedback millions of times. The `FEEDBACK_TABLE` (`1296 × 1296 × 2` int8 array) is built once at import time in `mastermind/engine/codes.py`. Every subsequent lookup is an O(1) NumPy index — no computation at training or inference time.

---

## Why Session-Based State

The game state (secret code, guess history, consistent set) is short-lived and user-specific. Using Django sessions stores this in the server's in-memory cache without needing a database, migrations, or authentication. Each browser tab gets its own session cookie, giving natural game isolation. The tradeoff is that sessions don't survive a server restart — acceptable for a stateless game.

---

## Why Nginx Reverse Proxy

The frontend is a single-page app (SPA) served as static files. Without a reverse proxy, the React app would need to make cross-origin requests to the backend, requiring CORS configuration and exposing the backend port to the browser. Nginx handles both concerns:

- Serves the SPA with a `try_files` fallback so client-side routing works.
- Proxies `/api/` requests to the backend container by hostname, keeping everything on one origin from the browser's perspective.
- Forwards session cookies, which is required for Django's session middleware to function.

---

## Why ConsistentAgent as Default AI

The trained RL model requires a specific board configuration (default: 6 colors, 4 pegs, 8 max steps). `ConsistentAgent` works with any configuration and needs no model file — it picks uniformly from the remaining consistent codes using the same `FEEDBACK_TABLE` the RL environment uses. It serves as a reliable fallback before a trained model is available and as a sanity check that the session and feedback pipeline are correct.

---

## Swapping ConsistentAgent for the RL Model

The AI is loaded in `web/server/game/agent.py`. To switch:

1. Place the trained model file (e.g. `model.zip`) somewhere accessible in the container.
2. In `agent.py`, replace the `ConsistentAgent` instantiation with a `MaskablePPO` load:

```python
from sb3_contrib import MaskablePPO
model = MaskablePPO.load("path/to/model.zip")
```

3. Update `get_ai_guess` to call `model.predict(obs, action_masks=masks)` instead of `agent.select_action(obs, masks)`.

The session structure and API contracts remain unchanged — the swap is confined to `agent.py`.
