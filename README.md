# JARVIS — Local, Privacy‑First OS Assistant

Identity: a local, privacy‑first operating system assistant. It runs on your machine, keeps your data on‑device, and focuses on real automation of everyday desktop workflows.

Key differentiators
- Multi‑step natural language execution: understands chained instructions and carries them out across apps.
- Strong reasoning + memory: combines short‑term conversation context with long‑term personal memory to adapt to you.
- On‑device privacy: personal data and memories are stored locally; internet calls are optional and user‑controlled.
- Practical desktop automation: launch/close apps, open sites, media control (planned), basic file operations, and simple coding tasks (planned).

Privacy‑first principles
- All memories, preferences, states, and embeddings are stored on device under `memory/`.
- Online LLM usage is opt‑in only: it’s used only when `OPENAI_API_KEY` is set. Otherwise the system uses an offline/hybrid mode with web search fallback.
- No personal data leaves your device unless you explicitly enable online features.

Features
- Desktop automation
  - Apps: open, close, reopen last (persistent across restarts)
  - Web: open sites, reopen last
  - Files (basic): create folder/file, rename/move, list a directory, delete with safeguard
  - Media: play/pause/next (planned; depends on OS capabilities)
  - Simple coding tasks (planned): generate/edit files from templates and run small scripts
- Natural multi‑step tasks
  - Understands chained commands and executes them sequentially with shared context
  - Example: “Create a notes folder, open notepad, and save a todo list”
- Memory and adaptation
  - Short‑term window keeps recent turns for continuity
  - Long‑term memory stores facts, habits, and preferences with retrieval
  - Affect‑aware tone: concise under urgency, empathetic under frustration
- Hybrid intelligence
  - Stronger reasoning with LLM when enabled
  - Offline/hybrid fallback with DuckDuckGo search
- Voice‑first
  - Voice input and TTS output for hands‑free workflows

Quick start
1. Python 3.10+
2. Install dependencies (PowerShell on Windows):
   - `python -m pip install --upgrade pip`
   - `pip install scikit-learn SpeechRecognition pyttsx3 duckduckgo-search openai`
   - `pip install pipwin`
   - `pipwin install pyaudio`
   - If `ddgs` import fails: `pip install ddgs`
3. Optional: set your OpenAI key to enable LLM fallback
   - `setx OPENAI_API_KEY "your_api_key_here"`
4. Run
   - `python main.py`

Examples
- “open notepad”
- “open youtube”
- “close notepad”
- “open again”
- “what time is it”
- “create a folder named notes on the desktop, then create a file todo.txt inside it”

Architecture
- `core/`
  - `router.py`: routes intents/commands
  - `actions.py`: app/web actions
  - `context_manager.py`: builds context from short/long‑term memory and affect
  - `answer_generator.py`, `search_engine.py`, etc.
- `llm/`
  - `chat.py`: LLM client that accepts memory context
- `memory/`
  - `short_term.py`: rolling dialogue window
  - `long_term.py`: JSONL store + lightweight embeddings
  - `affect.py`: urgency/frustration detection
  - `state.py`: persistent app/website state
- `voice/`
  - `listen.py`, `speak.py`
- `ml/`
  - `predict.py` with trained model

Security & offline mode
- By default, the system runs locally and uses only on‑device memory.
- If you don’t set `OPENAI_API_KEY`, LLM is not used. Answers will rely on offline/hybrid modes.

Roadmap
- Media controls via OS‑appropriate APIs
- Simple coding tasks: boilerplate generation and execution helpers
- Richer multi‑step planning with rollback
