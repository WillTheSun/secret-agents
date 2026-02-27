from gadgets.decryptor import decrypt_message
from gadgets.weather import get_weather

PHASE_ORDER = ["travel", "briefing", "crack_code", "complete"]


def execute_tool(tool_name, parameters, game_state=None):
    if game_state is None:
        game_state = {"current_mission": {}}

    print(f"DEBUG: Executing tool '{tool_name}' with parameters: {parameters}")

    if tool_name == "weather":
        city = parameters.get("city")
        result = get_weather(city)

    elif tool_name == "decrypt_message":
        ciphertext = parameters.get("ciphertext")
        shift = parameters.get("shift")
        result = decrypt_message(ciphertext, shift)

    elif tool_name == "select_mission":
        location = parameters.get("location")
        cipher = parameters.get("cipher")
        shift = parameters.get("shift")
        shift_hint = next(
            (opt.get("shift_hint", "") for opt in game_state.get("mission_options", []) if opt.get("location") == location),
            ""
        )
        mission = game_state.get("current_mission", {})
        mission.update({
            "location": location,
            "cipher": cipher,
            "shift": shift,
            "shift_hint": shift_hint,
        })
        game_state["current_mission"] = mission
        result = f"Mission confirmed for {location}."

    elif tool_name == "update_game_phase":
        new_phase = parameters.get("phase")
        mission = game_state.get("current_mission", {})
        current_phase = mission.get("phase", "travel")
        completed = mission.get("completed_phases", [])
        if current_phase not in completed:
            completed.append(current_phase)
        mission["completed_phases"] = completed
        mission["phase"] = new_phase
        if new_phase == "complete":
            mission["active"] = False
        game_state["current_mission"] = mission
        result = f"Phase advanced to: {new_phase}"

    else:
        result = "Unknown tool requested."

    print(f"DEBUG: Tool '{tool_name}' returned: {result}")
    return result, game_state
