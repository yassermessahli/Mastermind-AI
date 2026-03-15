# web/server — Django Backend

Django REST Framework backend for the Mastermind web app. Manages game state in server-side sessions and delegates all game logic to the `mastermind` package.

---

## Running Locally

```bash
cp .env.example .env
make backend-serve      # starts on http://localhost:8001
```

Or manually:

```bash
cd web/server
uv run python manage.py runserver 8001
```

Requires the root `uv` environment with the `backend` dependency group installed (`make install`).

---

## API Endpoints

| Method | Path                  | Description                                        | Mode        |
|--------|-----------------------|----------------------------------------------------|-------------|
| POST   | `/api/game/start/`    | Start a new game session                           | both        |
| POST   | `/api/game/guess/`    | Submit a player guess (by code index)              | codebreaker |
| POST   | `/api/game/feedback/` | Submit feedback for the AI's guess (blacks/whites) | codekeeper  |
| GET    | `/api/game/state/`    | Retrieve current session state                     | both        |
| POST   | `/api/game/reset/`    | Clear session state                                | both        |

### Request bodies

**`/start/`**
```json
{ "mode": "codebreaker", "n_colors": 6, "n_pegs": 4, "max_steps": 8 }
```

**`/guess/`**
```json
{ "guess_idx": 42 }
```

**`/feedback/`**
```json
{ "blacks": 1, "whites": 2 }
```

---

## Tests

```bash
make backend-test
```
