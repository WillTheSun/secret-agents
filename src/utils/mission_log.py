import json

MISSION_LOG_FILE = "mission_log.json"


def load_mission_log():
    try:
        with open(MISSION_LOG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"conversation": []}
    except json.JSONDecodeError:
        return {"conversation": []}


def save_mission_log(log):
    with open(MISSION_LOG_FILE, "w") as file:
        json.dump(log, file, indent=4)
