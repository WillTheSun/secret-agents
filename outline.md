Project Spec: Secret Agents
"Secret Agents" is a web-based text game where players solve spy missions and puzzles through a chat interface. An LLM (served online via API or locally via tools like Ollama) manages all user inputs, invokes relevant tools, and formats the output. The LLM acts as the central controller, orchestrating actions based on user commands and providing context-aware responses.

This project is divided into two phases, each focused on building an agent in the app:

The Quartermaster: a tool-using agent
The Taskmaster: a game-manager agent
Phase 1: Tool-Using Agent Overview
We're going to begin implementing our agent-based application with a single agent that is capable of function-calling / tool usage. This is just one portion of the complete game but emphasizes the most common pattern in agentic systems and a core upgrade to RAG.

This part of the application manages an LLM-centric interaction flow that invokes tools before responding to prompts:

Flow
User Input: Message sent via chat interface.
LLM Processing: LLM determines required actions and tool(s).
Tool Invocation: Flask executes tools as requested.
Tool Result Handling: Results are sent back to the LLM.
LLM Response: Final response is generated and returned to the user.
Tool Examples:

Weather Gadget: Retrieves real-time weather data.
Decryption Gadget: Solves puzzles like Caesar ciphers.
Additional Gadgets: Time zone converter, translator.
Application Architecture
Frontend / UI:

HTML/CSS: Provides the web-based chat interface.
JavaScript: Uses Socket.IO for real-time communication between the frontend and Flask backend.
Backend (Flask application):

Flask: Handles routing, WebSocket communication, and integration with the LLM and gadgets.
LLM Integration: User messages are sent to the LLM, which processes the input, determines tool usage, and returns instructions to Flask.
Tool Execution: Tools are executed based on LLM requests, with results returned for response generation.
Directory Structure:

src/
├── app.py              # Main Flask application
├── mission_log.json    # Log of interactions
├── requirements.txt    # Dependencies
├── templates/          # HTML templates (chat interface)
├── gadgets/            # Functions that call APIs or perform non-LLM tasks
├── utils/              # Utility functions 
└── llm/                # LLM interaction logic
Core Components:

LLM Interface
Purpose: Manages communication with the LLM, including sending user messages and receiving instructions.
Implementation: Uses HTTP requests for communication, with a structured protocol for tool requests.
Tool Executor
Purpose: Executes tools as instructed by the LLM.
Implementation: Maps tool names to functions and handles invocation.
Flask App
Implementation: Receives user messages, forwards them to the LLM, executes tools if needed, and delivers responses to the user.

Developer Notes
LLM Configuration: Ensure LLM understands the structured response format.
Error Handling: Manage malformed responses or failed tool executions.
Security: Validate inputs to prevent unauthorized actions.
Testing: Test LLM and Flask interactions with representative inputs.

Phase 1 Extra Credit
Expand Gadget Library: Add tools like translators or additional puzzles.
LLM Fine-Tuning: Improve decision-making and response quality.
User Feedback: Add rating capability to the UI (e.g. a thumbs-up / thumbs-down button after every LLM response. Store an interaction log and update a rating field based on the user input.

Phase 2: Game Manager Overview
This phase focuses on managing the game flow and context using an LLM that tracks player progress and mission status.

When a player starts a new session (using a "new game" button in the UI), the application creates a mission for the player to complete. The mission involves actions that involve using the tools in the game:

Traveling to a Location: The LLM selects a destination for the player.
Packing a Disguise: Based on the weather at the chosen location, the player must pack an appropriate disguise.
Cracking a Code: The LLM generates a Caesar cipher that the player must decode to steal an important object.
Mission Completion: The player reports back to mark the mission as complete, at which point the game session ends.
Flow
User Interaction: Player interacts with the game through the chat interface, starting with a new mission.
LLM State Management: LLM uses stored game state to track the player's progress through each mission phase.
Response Generation: LLM formulates responses based on the current mission context, providing briefings, hints, and feedback for each task.
Context Update: LLM updates mission progress and player interactions in the database or JSON files.
Core Components
Game State Manager (utils/game_state.py)
Purpose: Tracks player progress and game state.
Implementation: Stores and retrieves mission data, ensuring continuity in player experience.
Developer Notes
LLM Configuration: Ensure the LLM can track and recall game state.
Error Handling: Account for incomplete or inconsistent game states.
Security: Validate all player inputs and sanitize data before updating game state.
Testing: Test game scenarios to ensure smooth progression and context tracking.
