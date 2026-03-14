SESSION_KEY = "game_state"


def get_game_state(request) -> dict | None:
    return request.session.get(SESSION_KEY)


def set_game_state(request, state: dict) -> None:
    request.session[SESSION_KEY] = state
    request.session.modified = True


def clear_game_state(request) -> None:
    request.session.pop(SESSION_KEY, None)
    request.session.modified = True
