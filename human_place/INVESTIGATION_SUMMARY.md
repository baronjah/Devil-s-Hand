# Backend Investigation Summary — Devil's Hand
**Date:** 2026-02-27
**Status:** Multi-service ecosystem active but fragmented.

## 1. What was built today so far:
### D:\AI_COORDINATION (Active Services)
- **`phone_ai.py` (Port 8080):** A decision-first mobile interface using the `gemma` model for structured choices (A/B/C/D).
- **`brain.py` (Port 8002):** A graph engine managing nodes, paths, and "constructions". Supports "possession" logic and memory.
- **`game.py` (Port 8003):** An SSE-based timer game for "push" notifications and decision-making.
- **`chat_server.py` (Port 8080):** A legacy simple chat interface (replaced by `phone_ai.py`).
- **`backend_api.py` (Port 8000):** Existing FastAPI service.

### D:\devil_s_hand (New Ecosystem)
- **Godot Frontend:** `story_player.gd`, `demon_hand_controller.gd` (with Demon/God modes), and `judgement_engine.gd` (the "Final Judgement" session).
- **Web Dashboard:** `dashboard.html` and `story_deck.html` consuming SSE.
- **Test Stub:** `test_sse_server.py` simulating the "Devil's Hand" events.

## 2. Model Status (Ollama):
- `lfm` (1.2B): Fast routing/choices (~0.4s).
- `gemma` (2.2B): Main instruction-following chat model (~2s).
- `qwen-vl` (7B): Vision model, reads screenshots (~13s).
- `oss` (20B): Base model, creative but ignores instructions.

## 3. Key Findings:
- **SSE Reliability:** `game.py` had issues with single-threading blocking the stream. This needs `ThreadingHTTPServer`.
- **User Preference:** Shift from "chatting" to "touch/choice" interface.
- **Visual Goal:** "Neuron 3D" interface in Godot where data pulses are visible.
- **Ecosystem Goal:** A "train loop" that always runs, checks health, and executes a cycle of stories.

## 4. Next Steps:
- Combine the fragmented services under one `orchestrator.py`.
- Finalize the "Final Judgement Day" logic where scripts confess their technical debt.
- Implement the "God Hand" cleansing animation in Godot.
