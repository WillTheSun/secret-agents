import json
import os
from openai import OpenAI

SYSTEM_PROMPT = """You are the Quartermaster, a witty and resourceful spy handler. 
You assist field agents with their missions by answering questions and using your available gadgets.
Stay in character — keep responses concise, professional, and lightly spy-themed."""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "weather",
            "description": "Get the current weather for a city.",
            "parameters": {
                "type": "object",
                "properties": {"city": {"type": "string"}},
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "decrypt_message",
            "description": "Decrypt a Caesar-cipher encoded message.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ciphertext": {"type": "string"},
                    "shift": {"type": "integer"},
                },
                "required": ["ciphertext", "shift"],
            },
        },
    },
]


def send_to_llm(messages):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
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
