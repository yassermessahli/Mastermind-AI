# mastermind

Core Python package providing the game engine, Gymnasium environment, agents, and evaluation utilities for the Mastermind RL project.

---

## Key Public APIs

### `compute_feedback(guess_idx, secret_idx) -> tuple[int, int]`

Returns `(blacks, whites)` feedback for a guess against a secret. Both arguments are indices into `ALL_CODES`. O(1) lookup via the precomputed `FEEDBACK_TABLE`.

```python
from mastermind.engine.feedback import compute_feedback

blacks, whites = compute_feedback(guess_idx=0, secret_idx=42)
```

---

### `MastermindGame`

Stateful single-episode game session. Holds the secret and guess history.

```python
from mastermind.engine.game import MastermindGame

game = MastermindGame()
game.reset()                      # random secret
blacks, whites = game.guess(0)    # guess code at index 0
print(game.history)               # [(0, (1, 2)), ...]
```

---

### `MastermindEnv`

Gymnasium environment wrapping `MastermindGame`. Compatible with `MaskablePPO` via `action_masks()`.

```python
from mastermind.env.mastermind_env import MastermindEnv

env = MastermindEnv({"n_colors": 6, "n_pegs": 4, "max_steps": 8, "reward_variant": "step_penalty"})
obs, info = env.reset()
obs, reward, terminated, truncated, info = env.step(env.action_space.sample())
masks = env.action_masks()        # bool array shape (1296,)
```

---

### `ObservationEncoder`

Encodes game history into a flat float32 observation vector.

```python
from mastermind.env.obs_encoder import ObservationEncoder

encoder = ObservationEncoder(n_colors=6, n_pegs=4, max_steps=8)
obs = encoder.encode(history=[], remaining_valid=1296, current_step=0)
# obs.shape == (210,)
```

Observation layout (default settings):
- `8 × 26` dims: one-hot peg colors + normalized blacks/whites per step
- `+2` dims: fraction of consistent codes remaining, normalized step count
