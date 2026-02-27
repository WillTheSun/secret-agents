---
title: Secret Agents
emoji: 🕵️
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
---

# Secret Agents

A web-based spy mission text game demonstrating **multi-agent orchestration** and **LLM tool-calling** with [Chainlit](https://chainlit.io).

A Taskmaster agent manages mission state and drives the narrative, dynamically invoking tools mid-conversation — real-time weather lookups and Caesar cipher decryption — before formulating its next response. A second general-purpose agent handles out-of-mission dialogue. Game state is maintained per-user in session memory, making the app stateless and container-ready.

## Agentic Patterns Demonstrated

| Pattern | Implementation |
| --- | --- |
| **Tool-calling / function-calling** | Taskmaster invokes `weather` and `decrypt_message` tools mid-loop via OpenAI function calling |
| **Agentic tool loop** | App reruns the LLM after each tool result until no further tool calls are made |
| **Multi-agent routing** | Active missions route to the Taskmaster; idle sessions route to a general LLM interface |
| **Session-scoped state** | Mission state tracked in `cl.user_session` — no file I/O, safe for multi-user deployments |

## Gameplay

Players receive a covert mission briefing and work through four phases:

| Phase | Objective |
| --- | --- |
| **Travel** | Receive your destination from the Taskmaster |
| **Disguise** | Check local weather and choose your cover |
| **Crack the Code** | Decrypt an intercepted Caesar cipher using the Decryptor gadget |
| **Complete** | Debrief with the Taskmaster to close the mission |

## Architecture

```
User message
    │
    ▼
Agent Router (app.py)
    ├── Mission active?  ──► Taskmaster Agent
    │                            │
    │                     Tool-calling loop
    │                       ├── weather(city)
    │                       ├── decrypt_message(ciphertext, shift)
    │                       └── update_game_phase(phase)
    │
    └── No mission  ──► LLM Interface Agent
```

**Agents:**
- **Taskmaster** — drives mission phases, calls tools, manages game state transitions
- **LLM Interface** — handles general conversation with a system prompt and full message history

**Tool gadgets:**
- **Weather** — live conditions via OpenWeather API, used to inform the player's disguise choice
- **Decryptor** — solves Caesar ciphers; the player must guess the correct shift key

## Running Locally

### Prerequisites

- Python 3.11+
- OpenAI API key
- OpenWeather API key

### Setup

```bash
cd src
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example src/.env   # or place .env one level up at secret_agents/.env
```

### Run

```bash
cd src
chainlit run app.py
```

## Environment Variables

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | OpenAI API key for LLM calls |
| `OPENWEATHER_API_KEY` | OpenWeather API key for the Weather gadget |
