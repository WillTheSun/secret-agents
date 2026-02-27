import json

GAME_STATE_FILE = "game_state.json"


def load_game_state():
    try:
        with open(GAME_STATE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"current_mission": {}}
    except json.JSONDecodeError:
        return {"current_mission": {}}


def save_game_state(state):
    with open(GAME_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)
