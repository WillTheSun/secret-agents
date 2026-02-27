---
title: Secret Agents
emoji: 🕵️
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
---

# 🔗 Demo: **[Open on Hugging Face →](https://huggingface.co/spaces/willthesun/SecretAgent)**

# Secret Agents (Agentic LLM Game)

Secret Agents is a web-based spy mission text game built with **Chainlit** and an **LLM tool-calling runtime**. The core learning outcome is **engineering an agentic system**: routing between agents, running a **tool loop** (LLM → tools → LLM), and enforcing a **finite-state mission workflow** while the model generates narrative and decisions.

## Agentic Concepts Demonstrated

### 1) Tool Calling (Structured Actions)
The model can emit structured tool calls (name + JSON parameters). The app executes tools (e.g., weather lookup, cipher decrypt) and returns tool results back to the model as tool messages.

### 2) Agentic Tool Loop (LLM ↔ Tools Until Done)
Instead of a single response, the system repeatedly alternates **LLM → tool execution → LLM** until the model stops requesting tools, enabling multi-step behavior with environment feedback.

### 3) Multi-Agent Routing (Specialist vs Generalist)
Requests are routed between a constrained mission manager (specialist) and a general conversational agent (generalist), keeping prompts simpler and behavior more controllable.

### 4) Controlled Workflow (Prompt-as-Policy + FSM)
Prompts encode “policy” (required steps, phase-specific rules), while a finite sequence of phases structures mission progression. Creativity stays in the model; correctness stays in the workflow constraints.

### 5) Context + Hybrid Software Design (Reliability)
The app carefully selects what context to feed the model (summaries over dumps) and combines deterministic code (validation/updates) with probabilistic generation (narrative), improving reliability and debuggability.

---

## Gameplay

Players receive a covert mission briefing and work through four phases:

| Phase              | Objective                                                       |
| ------------------ | --------------------------------------------------------------- |
| **Travel**         | Receive your destination from the Taskmaster                    |
| **Disguise**       | Check local weather and choose your cover                       |
| **Crack the Code** | Decrypt an intercepted Caesar cipher using the Decryptor gadget |
| **Complete**       | Debrief with the Taskmaster to close the mission                |

---

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

| Variable              | Description                                |
| --------------------- | ------------------------------------------ |
| `OPENAI_API_KEY`      | OpenAI API key for LLM calls               |
| `OPENWEATHER_API_KEY` | OpenWeather API key for the Weather gadget |
