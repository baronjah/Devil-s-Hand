# AI Plans — Devil's Hand

## Codex's Plan (from 17:30 Handoff)
### Goals
1. **Fix SSE in `game.py`:** Use 5s heartbeats for iOS stability.
2. **Visual Debugging (Pulses):**
   - Every variable change emits a "pulse" event (SSE).
   - Visualize as flashes in Godot or timeline bars.
3. **Brain.py Expansion:** Persistent graph state and construction sequences.

### Unified Reliability + Orchestration Plan
- **Orchestrator.py:** Supervisor to start/monitor all services (Ollama, brain, game, phone).
- **Hardened Game.py:** Use per-client outbound queues.
- **Godot Integration:** `orchestrator_panel.gd` and `neuron_graph_controller.gd`.

---

## Claude's Plan (The "Devil's Hand" Vision)
### The "Train Loop"
- `devils_hand_main.py` is the always-running ecosystem.
- Messy prompts go into the "Basket".
- Professional "Ancient Screenwriters" turn intents into storyboards.

### Possession and Co-Control
- Token-based turns between AI and User.
- Adaptive bonus time for user inactivity.
- "Skill Forge" creates reusable `.dhskill.zip` artifacts.

### 5D Time-Play
- Simultaneous story runtimes.
- Rewind, branch, and merge timelines.
- Competition/Perfection loop: AI and User propose moves, best elements merge.

### Presentation
- Godot as the 3D Simulation/Presentation stage.
- Browser as the Story Deck (PowerPoint-style).
- Shared JSON-first data model.
