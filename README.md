---
title: Secret Agents
emoji: 🕵️
colorFrom: gray
colorTo: blue
sdk: docker
app_port: 7860
---

# Secret Agents

A web-based spy mission text game powered by a multi-agent LLM system, built with [Chainlit](https://chainlit.io).

## Gameplay

Players receive a covert mission briefing and work through four phases:

| Phase | Objective |
| --- | --- |
| **Travel** | Receive your destination from the Taskmaster |
| **Disguise** | Check local weather and choose your cover |
| **Crack the Code** | Decrypt an intercepted Caesar cipher using the Decryptor gadget |
| **Complete** | Debrief with the Taskmaster to close the mission |

## Architecture

Two LLM agents collaborate to run the game:

- **Taskmaster** — manages game state and drives the mission narrative
- **LLM Interface** — handles general conversation outside of active missions

Tool gadgets available to the agents:
- **Weather** — real-time weather data via OpenWeather API
- **Decryptor** — Caesar cipher solver

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
