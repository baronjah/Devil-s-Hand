# Claude Technical Logs — Session 2026-02-27

## Ollama Model Management
- **LFM (1.2B):** Loaded from `D:\llm_vlm`. Fast verification model.
- **Qwen2.5-VL (7B):** Vision model loaded. Tested with screenshots (640x360).
- **GPT-OSS (20B):** Base model. Fast but non-instructional.
- **Gemma 2.2B:** Instruction-tuned. Chosen for `phone_ai.py`.

## Python Environment
- Installed `pyautogui`, `pillow`, `httpx`, `fastapi`, `uvicorn`.
- Fixed Unicode/CP1252 issues on Windows by forcing UTF-8 in `sys.stdout`.

## Service Implementations (D:\AI_COORDINATION)
### 1. `chat_server.py` (Port 8080)
- Simple HTTP server for Ollama chat.

### 2. `phone_ai.py` (Port 8080)
- Decision-first interface.
- Automatic choice extraction (A/B/C/D) using `lfm` as an extractor.
- History management (last 4-8 messages).

### 3. `brain.py` (Port 8002)
- Graph engine.
- Nodes (context databases), Paths (connections), Crossroads (branches).
- Persistence to `graph_data/graph.json`.

### 4. `game.py` (Port 8003)
- SSE-based timer game.
- Dynamic timer (1s per 12 chars).
- 2-way push channel (POST `/push`).
- Fix: `ThreadingHTTPServer` to prevent SSE blocking other requests.

## Bootstrap of Devil's Hand (D:\devil_s_hand)
- Created project structure: `docs/`, `schemas/`, `godot/`, `human_place/`.
- Created foundational documents: `README.md`, `ARCHITECTURE.md`, `CONTRACTS.md`, `IMPLEMENTATION_PLAN.md`.
- Created agent role files: `FOR_CODEX.md`, `FOR_GEMINI.md`.
- Created schemas: `basket_output.schema.json`, `skill_manifest.schema.json`.
- Created stub: `devils_hand_main.py`.
