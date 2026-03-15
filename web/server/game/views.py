import random

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from game.agent import all_codes_for, filter_consistent_set, game_feedback, get_ai_guess
from game.serializers import FeedbackSerializer, GuessSerializer, StartSerializer
from game.session import clear_game_state, get_game_state, set_game_state


@api_view(["POST"])
def start(request):
    """Start a new game session.

    Body: ``{ mode, n_colors, n_pegs, max_steps }``

    In *codebreaker* mode a random secret code is stored in the session.
    In *codekeeper* mode the full consistent set is initialised and the AI
    makes its first guess, which is included in the response.
    """
    serializer = StartSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    data = serializer.validated_data
    mode = data["mode"]
    n_colors = data["n_colors"]
    n_pegs = data["n_pegs"]
    max_steps = data["max_steps"]
    n_codes = n_colors**n_pegs

    if mode == "codebreaker":
        secret_idx = random.randrange(n_codes)
        state = {
            "mode": mode,
            "secret_idx": secret_idx,
            "n_colors": n_colors,
            "n_pegs": n_pegs,
            "max_steps": max_steps,
            "step": 0,
            "terminated": False,
            "truncated": False,
            "history": [],
        }
        set_game_state(request, state)
        return Response(
            {
                "mode": mode,
                "n_colors": n_colors,
                "n_pegs": n_pegs,
                "max_steps": max_steps,
                "step": 0,
                "terminated": False,
                "truncated": False,
                "history": [],
            }
        )

    all_codes = all_codes_for(n_colors, n_pegs)
    consistent_set = list(range(n_codes))
    ai_guess_idx = get_ai_guess(consistent_set, n_colors, n_pegs)
    state = {
        "mode": mode,
        "consistent_set": consistent_set,
        "current_ai_guess_idx": ai_guess_idx,
        "n_colors": n_colors,
        "n_pegs": n_pegs,
        "max_steps": max_steps,
        "step": 0,
        "terminated": False,
        "truncated": False,
        "history": [],
    }
    set_game_state(request, state)
    return Response(
        {
            "mode": mode,
            "n_colors": n_colors,
            "n_pegs": n_pegs,
            "max_steps": max_steps,
            "step": 0,
            "terminated": False,
            "truncated": False,
            "history": [],
            "ai_guess_idx": ai_guess_idx,
            "ai_guess": list(all_codes[ai_guess_idx]),
            "consistent_set_size": len(consistent_set),
        }
    )


@api_view(["POST"])
def guess(request):
    """Submit a player guess in codebreaker mode.

    Body: ``{ guess_idx }`` — index into the code space for the current board size.

    Computes black/white feedback against the session secret, updates history,
    and returns ``terminated`` (correct guess) or ``truncated`` (limit reached).
    """
    state = get_game_state(request)
    if state is None:
        return Response(
            {"detail": "No active game. Call /start/ first."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if state["mode"] != "codebreaker":
        return Response(
            {"detail": "Endpoint only valid in codebreaker mode."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if state["terminated"] or state["truncated"]:
        return Response(
            {"detail": "Game is already over."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    n_colors = state["n_colors"]
    n_pegs = state["n_pegs"]
    n_codes = n_colors**n_pegs

    serializer = GuessSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    guess_idx = serializer.validated_data["guess_idx"]
    if guess_idx >= n_codes:
        return Response(
            {"detail": f"guess_idx must be in [0, {n_codes - 1}]."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    all_codes = all_codes_for(n_colors, n_pegs)
    blacks, whites = game_feedback(all_codes, guess_idx, state["secret_idx"], n_colors)

    state["history"].append([guess_idx, blacks, whites])
    state["step"] += 1
    state["terminated"] = blacks == n_pegs
    state["truncated"] = not state["terminated"] and state["step"] >= state["max_steps"]
    set_game_state(request, state)

    return Response(
        {
            "blacks": blacks,
            "whites": whites,
            "terminated": state["terminated"],
            "truncated": state["truncated"],
            "step": state["step"],
            "history": state["history"],
        }
    )


@api_view(["POST"])
def feedback(request):
    """Submit the player's feedback for the AI's last guess in codekeeper mode.

    Body: ``{ blacks, whites }`` — the correct feedback for the AI's most recent guess.

    Filters the consistent set, advances the step counter, and returns the AI's
    next guess (unless the game is over).
    """
    state = get_game_state(request)
    if state is None:
        return Response(
            {"detail": "No active game. Call /start/ first."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if state["mode"] != "codekeeper":
        return Response(
            {"detail": "Endpoint only valid in codekeeper mode."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if state["terminated"] or state["truncated"]:
        return Response(
            {"detail": "Game is already over."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    n_colors = state["n_colors"]
    n_pegs = state["n_pegs"]
    serializer = FeedbackSerializer(data=request.data, context={"n_pegs": n_pegs})
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    blacks = serializer.validated_data["blacks"]
    whites = serializer.validated_data["whites"]

    all_codes = all_codes_for(n_colors, n_pegs)
    current_ai_guess_idx = state["current_ai_guess_idx"]

    new_consistent_set = filter_consistent_set(
        all_codes,
        state["consistent_set"],
        current_ai_guess_idx,
        blacks,
        whites,
        n_colors,
    )

    state["history"].append([current_ai_guess_idx, blacks, whites])
    state["step"] += 1
    state["terminated"] = blacks == n_pegs
    state["truncated"] = not state["terminated"] and state["step"] >= state["max_steps"]
    state["consistent_set"] = new_consistent_set

    next_ai_guess_idx = None
    if not state["terminated"] and not state["truncated"]:
        next_ai_guess_idx = get_ai_guess(new_consistent_set, n_colors, n_pegs)
        state["current_ai_guess_idx"] = next_ai_guess_idx

    set_game_state(request, state)

    response: dict = {
        "terminated": state["terminated"],
        "truncated": state["truncated"],
        "step": state["step"],
        "consistent_set_size": len(new_consistent_set),
        "history": state["history"],
    }
    if next_ai_guess_idx is not None:
        response["ai_guess_idx"] = next_ai_guess_idx
        response["ai_guess"] = list(all_codes[next_ai_guess_idx])

    return Response(response)


@api_view(["GET"])
def game_state(request):
    """Return the current session state without exposing secret information.

    The ``secret_idx``, ``consistent_set``, and ``current_ai_guess_idx`` fields
    are excluded from the response.  In codekeeper mode, ``consistent_set_size``
    and the current ``ai_guess`` are added.
    """
    state = get_game_state(request)
    if state is None:
        return Response({"detail": "No active game."}, status=status.HTTP_404_NOT_FOUND)

    excluded = {"secret_idx", "consistent_set", "current_ai_guess_idx"}
    safe = {k: v for k, v in state.items() if k not in excluded}

    if state["mode"] == "codekeeper":
        safe["consistent_set_size"] = len(state.get("consistent_set", []))
        if not state["terminated"] and not state["truncated"]:
            ai_idx = state.get("current_ai_guess_idx")
            if ai_idx is not None:
                all_codes = all_codes_for(state["n_colors"], state["n_pegs"])
                safe["ai_guess_idx"] = ai_idx
                safe["ai_guess"] = list(all_codes[ai_idx])

    return Response(safe)


@api_view(["POST"])
def reset(request):
    """Clear the current game session state."""
    clear_game_state(request)
    return Response({"ok": True})
