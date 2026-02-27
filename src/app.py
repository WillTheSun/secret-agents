from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

import asyncio
import json
import chainlit as cl
from llm.llm_interface import send_to_llm, SYSTEM_PROMPT
from llm.taskmaster import generate_mission, send_to_taskmaster
from utils.tool_executor import execute_tool
from utils.mission_log import load_mission_log, save_mission_log
from utils.game_state import load_game_state, save_game_state


async def run_tool_loop(send_fn, messages, **send_kwargs):
    """Run the tool-calling loop for any LLM sender and return the final text."""
    result = await asyncio.to_thread(send_fn, messages, **send_kwargs)

    while isinstance(result, dict):
        assistant_msg = result["assistant_message"]
        messages.append(assistant_msg)
        for tc in assistant_msg.tool_calls:
            tool_result = execute_tool(tc.function.name, json.loads(tc.function.arguments))
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": tool_result,
            })
        if "game_state" in send_kwargs:
            send_kwargs["game_state"] = load_game_state()
        result = await asyncio.to_thread(send_fn, messages, **send_kwargs)

    return result


@cl.on_chat_start
async def on_chat_start():
    cl.user_session.set("messages", [])
    actions = [cl.Action(name="new_game", value="new_game", label="New Game", payload={})]
    await cl.Message(
        content="Welcome, Agent. Your mission awaits. Click **New Game** to receive your briefing.",
        actions=actions,
    ).send()


@cl.action_callback("new_game")
async def on_new_game(action: cl.Action):
    mission_options = await asyncio.to_thread(generate_mission)
    game_state = {
        "mission_options": mission_options.get("options", []),
        "current_mission": {
            "active": True,
            "phase": "travel",
            "location": "pending",
            "cipher": "pending",
            "shift": 0,
            "completed_phases": [],
        }
    }
    save_game_state(game_state)

    briefing_messages = [
        {"role": "user", "content": "Start the mission. Present the available mission options."}
    ]
    cl.user_session.set("messages", briefing_messages)
    briefing = await run_tool_loop(send_to_taskmaster, briefing_messages, game_state=game_state)

    # Reload game state to get the updated phase if it changed during the tool loop
    game_state = load_game_state()
    phase = game_state.get("current_mission", {}).get("phase", "unknown")
    
    actions = []
    if phase == "briefing":
        actions.append(cl.Action(name="get_weather", value="get_weather", label="Get Weather", payload={}))
    elif phase == "crack_code":
        actions.append(cl.Action(name="use_decryptor", value="use_decryptor", label="🔓 Use Decryptor Gadget", payload={}))

    await cl.Message(content=f"**[PHASE: {phase}]**\n\n{briefing}", actions=actions).send()


@cl.action_callback("get_weather")
async def on_get_weather(action: cl.Action):
    game_state = load_game_state()
    location = game_state.get("current_mission", {}).get("location", "London")
    
    # Directly call the tool executor
    weather_report = execute_tool("weather", {"city": location})
    
    await cl.Message(content=f"📡 **Weather Intelligence for {location}:**\n{weather_report}").send()


@cl.action_callback("use_decryptor")
async def on_use_decryptor(action: cl.Action):
    res = await cl.AskActionMessage(
        content="🔐 **Decryptor Armed.**\n\nBefore you proceed — re-read your briefing carefully. The Taskmaster never wastes words. Something in that message holds the key.\n\nSelect the shift:",
        actions=[cl.Action(name=f"shift_{i}", value=str(i), label=str(i), payload={}) for i in range(1, 6)],
    ).send()

    if not res:
        return

    value = res.get("value") or res.get("name", "").rsplit("_", 1)[-1]
    user_shift = int(value)
    game_state = load_game_state()
    mission = game_state.get("current_mission", {})
    cipher = mission.get("cipher")
    actual_shift = mission.get("shift")

    if user_shift == actual_shift:
        decrypted = execute_tool("decrypt_message", {"ciphertext": cipher, "shift": user_shift})
        await cl.Message(content=f"✅ **DECRYPTION SUCCESSFUL:**\n\n> {decrypted}").send()

        execute_tool("update_game_phase", {"phase": "complete"})
        game_state = load_game_state()

        messages = cl.user_session.get("messages", [])
        messages.append({"role": "user", "content": f"The message has been decrypted: {decrypted}. Mission complete."})
        debrief = await run_tool_loop(send_to_taskmaster, messages, game_state=game_state)
        cl.user_session.set("messages", messages)

        await cl.Message(content=f"**[PHASE: complete]**\n\n{debrief}").send()
    else:
        retry_action = cl.Action(name="use_decryptor", value="use_decryptor", label="🔓 Use Decryptor Gadget", payload={})
        await cl.Message(
            content="❌ **DECRYPTION FAILED:** Incorrect shift. The signal remains scrambled. Try again.",
            actions=[retry_action],
        ).send()


@cl.on_message
async def handle_message(message: cl.Message):
    game_state = load_game_state()
    mission = game_state.get("current_mission", {})
    messages = cl.user_session.get("messages", [])
    messages.append({"role": "user", "content": message.content})

    if mission.get("active"):
        result = await run_tool_loop(send_to_taskmaster, messages, game_state=game_state)
    else:
        # For non-mission interactions, we might want to inject the system prompt
        # but keep the history. For now, let's just ensure history is used.
        if not any(m.get("role") == "system" for m in messages):
            messages.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
        result = await run_tool_loop(send_to_llm, messages)

    cl.user_session.set("messages", messages)

    # Reload game state to get the updated phase
    game_state = load_game_state()
    phase = game_state.get("current_mission", {}).get("phase", "none") if game_state.get("current_mission", {}).get("active") else "inactive"

    actions = []
    if phase == "briefing":
        actions.append(cl.Action(name="get_weather", value="get_weather", label="Get Weather", payload={}))
    elif phase == "crack_code":
        actions.append(cl.Action(name="use_decryptor", value="use_decryptor", label="🔓 Use Decryptor Gadget", payload={}))

    log = load_mission_log()
    log["conversation"].append({"user": message.content, "agent": result})
    save_mission_log(log)

    await cl.Message(content=f"**[PHASE: {phase}]**\n\n{result}", actions=actions).send()
