import json
import os
from openai import OpenAI
from llm.llm_interface import TOOLS
from gadgets.decryptor import encrypt_message

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TASKMASTER_PERSONA = """You are the Taskmaster, a shadowy spymaster who runs field agents through covert missions.
You manage a strict four-phase mission sequence: travel -> briefing -> crack_code -> complete.

CRITICAL:
- You MUST explicitly call update_game_phase to advance the mission state.
- Never skip phases.
- Never advance without a player decision or successful action.
- Keep responses short, tense, and spy-themed.
- Never break character.
"""

PHASE_PROMPTS = {
    "travel": """CURRENT PHASE: travel
Present the 3 mission options listed in 'Mission Options' as distinct destinations.
Number the options 1-3 in display order.
For each option, show the location and a short <15 word summary of the atmospheric description — do NOT reveal the cipher or shift value.
The agent MUST choose one.
Treat a choice by number (1-3) as selecting the corresponding option in the displayed order.
Once they choose, you MUST:
1. Call select_mission with the chosen location, cipher, and shift.
2. Call update_game_phase with phase='briefing'.""",

    "briefing": """CURRENT PHASE: briefing
Set the scene in the chosen city.
Using the shift_hint as inspiration, craft a single sentence and bury it naturally in the briefing narrative — an offhand remark, a piece of field intelligence, or an atmospheric detail. RULES for this sentence: (1) NEVER label it or draw attention to it. (2) MUST include the shift as an explicit single digit (1-5) exactly once. (3) It MUST contain exactly one countable element whose count equals the shift value — e.g. objects, events, taps on a door. The agent must recognise it themselves.
Present the encrypted cipher as the intercepted message they will need to crack.
Present 3 plausible disguises suited to the mission, numbered 1–3.
The agent MUST choose one cover identity.
CRITICAL — when the agent names or picks any disguise (by number or description), you MUST immediately call update_game_phase with phase='crack_code' AS A TOOL CALL before writing any response text. Do NOT acknowledge the choice with text only. If you are unsure whether the agent has chosen, ask them to confirm. Never move on without calling the tool.""",

    "crack_code": """CURRENT PHASE: crack_code
Deliver the mission-critical encrypted message (the cipher from the mission state) themed to the selected city and disguise.
Instruct the agent to use the 'Use Decryptor Gadget' button.
Once the message is successfully decrypted, you MUST call update_game_phase with phase='complete'.""",

    "complete": """CURRENT PHASE: complete
Accept the agent's final report in-character.
Deliver a short debrief and mission rating.
Close the operation cleanly.""",
}

UPDATE_GAME_PHASE_TOOL = {
    "type": "function",
    "function": {
        "name": "update_game_phase",
        "description": "Advance the mission to the next phase once the player has completed the current one.",
        "parameters": {
            "type": "object",
            "properties": {
                "phase": {
                    "type": "string",
                    "enum": ["briefing", "crack_code", "complete"],
                }
            },
            "required": ["phase"],
        },
    },
}

SELECT_MISSION_TOOL = {
    "type": "function",
    "function": {
        "name": "select_mission",
        "description": "Confirm the selected mission and save its details to the game state.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string"},
                "cipher": {"type": "string"},
                "shift": {"type": "integer"},
            },
            "required": ["location", "cipher", "shift"],
        },
    },
}

TASKMASTER_TOOLS = TOOLS + [UPDATE_GAME_PHASE_TOOL, SELECT_MISSION_TOOL]

MISSION_GENERATION_PROMPT = """You are a spy mission generator. Return ONLY valid JSON — no markdown, no explanation.
Generate 3 distinct mission options. Return them in a list under the key 'options'.
Each mission must have these fields:
{
  "location": "<a real world city>",
  "description": "<2-3 sentences of tense, atmospheric flavour for this mission — evoke the city's mood, the danger, and the stakes. No cipher or plaintext details.>",
  "plaintext": "<a short meaningful phrase of 3-5 words, ALL CAPS, e.g. 'MEET AT THE DOCKS'>",
  "shift": <integer between 1 and 5>,
  "shift_hint": "<a short spy-flavoured phrase hinting at the shift value, without stating the number as a digit>"
}"""


def generate_mission():
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": MISSION_GENERATION_PROMPT},
            {"role": "user", "content": "Generate 3 new mission options."},
        ],
    )
    data = json.loads(response.choices[0].message.content)
    for option in data.get("options", []):
        # Ensure shift is within the valid 1-5 range
        original_shift = option.get("shift", 1)
        clamped_shift = max(1, min(5, int(original_shift)))
        option["shift"] = clamped_shift
        
        plaintext = option.pop("plaintext", "")
        option["cipher"] = encrypt_message(plaintext, option["shift"])
    return data


def send_to_taskmaster(messages, game_state):
    mission = game_state.get("current_mission", {})
    phase = mission.get("phase", "travel")
    options = game_state.get("mission_options", [])

    options_summary = "\n".join([
        f"- {opt['location']} (Cipher: {opt['cipher']}, Shift: {opt['shift']})"
        + (f"\n  Description: {opt['description']}" if opt.get('description') else "")
        for opt in options
    ])

    shift_lines = (
        ""
        if phase == "crack_code"
        else (
            f"  Shift: {mission.get('shift', 0)}\n"
            f"  Shift Hint: {mission.get('shift_hint', 'pending')}\n"
        )
    )
    state_summary = (
        f"Mission Options:\n{options_summary}\n\n"
        f"Current mission state:\n"
        f"  Phase: {phase}\n"
        f"  Location: {mission.get('location', 'pending')}\n"
        f"  Cipher: {mission.get('cipher', 'pending')}\n"
        f"{shift_lines}"
        f"  Completed phases: {mission.get('completed_phases', [])}"
    )

    phase_instruction = PHASE_PROMPTS.get(phase, "")
    system_prompt = f"{TASKMASTER_PERSONA}\n{phase_instruction}\n\n{state_summary}"

    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=full_messages,
        tools=TASKMASTER_TOOLS,
    )
    choice = response.choices[0]

    if choice.finish_reason == "tool_calls":
        tool_call = choice.message.tool_calls[0]
        return {
            "tool_call_id": tool_call.id,
            "tool": tool_call.function.name,
            "params": json.loads(tool_call.function.arguments),
            "assistant_message": choice.message,
        }

    return choice.message.content
