import numpy as np
import pytest

from mastermind.engine.codes import CODE_TO_IDX, N_CODES, N_COLORS, N_PEGS
from mastermind.env.obs_encoder import ObservationEncoder

# Encoder defaults used across all tests
N_MAX_STEPS = 10
DIMS_PER_STEP = N_PEGS * N_COLORS + 2  # 24 one-hot + 2 scalars = 26
OBS_DIM = N_MAX_STEPS * DIMS_PER_STEP + 2  # 260 + 2 = 262


@pytest.fixture
def encoder() -> ObservationEncoder:
    return ObservationEncoder(n_colors=N_COLORS, n_pegs=N_PEGS, max_steps=N_MAX_STEPS)


# Shape and dtype


def test_output_shape_and_dtype(encoder: ObservationEncoder) -> None:
    obs = encoder.encode(history=[], remaining_valid=N_CODES, current_step=0)
    assert obs.shape == (OBS_DIM,)
    assert obs.dtype == np.float32


# Zero padding


def test_zero_padding_on_empty_history(encoder: ObservationEncoder) -> None:
    obs = encoder.encode(history=[], remaining_valid=N_CODES, current_step=0)
    history_block = obs[: N_MAX_STEPS * DIMS_PER_STEP]
    assert np.all(history_block == 0.0)
    assert obs[-2] == pytest.approx(1.0)  # remaining_valid / N_CODES = 1296/1296
    assert obs[-1] == pytest.approx(0.0)  # current_step / max_steps = 0/10


# One-hot correctness


def test_one_hot_encoding_correctness(encoder: ObservationEncoder) -> None:
    code = (0, 1, 2, 3)
    guess_idx = CODE_TO_IDX[code]
    blacks, whites = 2, 1
    obs = encoder.encode(
        history=[(guess_idx, (blacks, whites))],
        remaining_valid=N_CODES,
        current_step=1,
    )
    # Step 0 occupies dims [0 : DIMS_PER_STEP]
    step = obs[:DIMS_PER_STEP]
    # Each peg i occupies dims [i*N_COLORS : (i+1)*N_COLORS]
    for peg_i, color in enumerate(code):
        peg_slice = step[peg_i * N_COLORS : (peg_i + 1) * N_COLORS]
        expected = np.zeros(N_COLORS, dtype=np.float32)
        expected[color] = 1.0
        np.testing.assert_array_equal(peg_slice, expected)
    # Feedback scalars follow the peg block
    assert step[N_PEGS * N_COLORS] == pytest.approx(blacks / N_PEGS)  # 0.5
    assert step[N_PEGS * N_COLORS + 1] == pytest.approx(whites / N_PEGS)  # 0.25


# Constraint signal


def test_constraint_signal_updates(encoder: ObservationEncoder) -> None:
    remaining = 100
    step_idx = 2
    obs = encoder.encode(history=[], remaining_valid=remaining, current_step=step_idx)
    assert obs[-2] == pytest.approx(remaining / N_CODES)  # 100 / 1296
    assert obs[-1] == pytest.approx(step_idx / N_MAX_STEPS)  # 2 / 10


# Full history


def test_full_history_no_padding(encoder: ObservationEncoder) -> None:
    guess_idx = CODE_TO_IDX[(0, 0, 0, 0)]
    history = [(guess_idx, (0, 0))] * N_MAX_STEPS
    obs = encoder.encode(
        history=history,
        remaining_valid=1,
        current_step=N_MAX_STEPS,
    )
    assert obs.shape == (OBS_DIM,)
    # Every step slot should be filled — peg 0 of every step encodes color 0
    for step_i in range(N_MAX_STEPS):
        offset = step_i * DIMS_PER_STEP
        assert obs[offset] == pytest.approx(1.0)  # color 0 hot in peg 0
