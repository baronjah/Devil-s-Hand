# Architecture — Devil's Hand

## System Map

```
[User / Phone]
     │ messy prompt
     ▼
┌─────────────────────────────────────────────────────────┐
│                 devils_hand_main.py                      │
│   heartbeat loop │ subsystem watchdog │ global kill/pause│
└────┬──────┬──────┬──────┬──────┬──────┬────────────────┘
     │      │      │      │      │      │
     ▼      ▼      ▼      ▼      ▼      ▼
  ingest  basket  story  possess  skill  surface
  .py     .py     .py    .py      .py    servers
     │      │      │
     └──────┴──────┴──→ basket_output.json
                              │
                    storyboard_compiler.py
                              │
                    story_runtime.py  ←──── multi-story event bus
                              │
                    possession_engine.py
                              │
                    ┌─────────┴─────────┐
                simulation_gate.py   skill_forge.py
                    │                       │
                 [blocked]          skill_packer.py
                 until tests              │
                 pass                .dhskill.zip
                              │
               ┌──────────────┼──────────────┐
           browser         Godot          SSE stream
        dashboard.html   stage.tscn      /events/stream
        story_deck.html  overlay.tscn    /timeline/{id}/stream
```

---

## Components

### 1. devils_hand_main.py — Ecosystem Launcher
The train. Everything else is a car on the train.

Responsibilities:
- Boot dependency checks (Ollama? ports free? schema files present?)
- Start subsystems in this order: ingest → basket → story → possession → skill → surfaces
- Heartbeat loop: ping each subsystem every N seconds
- Restart policy: if subsystem dies, attempt restart up to 3 times, then flag + continue
- Global endpoints: `/ecosystem/start|pause|resume|stop|status`
- Clean shutdown: flush all story snapshots before exit

```python
SUBSYSTEMS = [
    {"name": "ingest",    "module": "prompt_ingest",       "port": None},
    {"name": "basket",    "module": "basket_router",       "port": None},
    {"name": "story",     "module": "story_runtime",       "port": 8010},
    {"name": "possession","module": "possession_engine",   "port": None},
    {"name": "skill",     "module": "skill_forge",         "port": None},
    {"name": "surface",   "module": "surface_server",      "port": 8011},
]
```

---

### 2. prompt_ingest.py + basket_router.py — Intake Layer

**prompt_ingest.py:**
- Accepts any text: fragmented, lowercase, multi-topic, stream-of-consciousness
- Normalizes without losing meaning
- Splits by comma as primary separator (user writing style)
- Passes phrase list to basket_router

**basket_router.py:**
- Given N phrase fragments + list of active story threads
- Routes each fragment to the most likely story thread
- Handles "new context" (creates new thread node)
- Handles "going back" (detects reference to previous thread)
- Outputs `basket_output.json`
- Uses local LLM (lfm for speed) for classification

```json
// basket_output.json
{
  "prompt_id": "uuid",
  "raw_text": "original messy input",
  "intents": [
    {"fragment": "...", "story_target": "story_id", "confidence": 0.9, "type": "action|branch|question|meta"}
  ],
  "discarded_noise": ["..."],
  "confidence": 0.85,
  "timestamp": "iso8601"
}
```

---

### 3. storyboard_compiler.py + story_runtime.py — Story Engine

**storyboard_compiler.py:**
- Takes `basket_output.json`
- Compiles intent list into ordered `StoryBeat[]`
- Each beat: scene, actors, actions, timeline_index, visual_cue, detail_weight
- Writes to `stories/{story_id}/beats.json`

**story_runtime.py:**
- Manages all active story instances
- States per story: `active | shadow | idle`
- Cross-story event bus: story A can emit event, story B receives
- Loop scheduler: visits all active stories continuously
- Teleport: load any snapshot directly (skip linear replay)
- Operations: `start | rewind | branch | merge | commit_canon`
- Snapshots written to `snapshots/{story_id}/{beat_id}.json`
- Archive lifecycle: current → cached → chunked → archived

```
Timeline model:
  beat_0 ──→ beat_1 ──→ beat_2 ──→ beat_3  [canon]
                  └──→ branch_A ──→ branch_B  [shadow]
                              ↑ merge possible
```

---

### 4. possession_engine.py — Co-Control

Token turn model:
```
AI_TURN → USER_TURN → AI_TURN → ...
```

Adaptive bonus:
```python
if user_control_share_last_N_turns < THRESHOLD:
    user_turn_ms *= BONUS_MULTIPLIER  # default 1.5x
    user_turn_ms = min(user_turn_ms, MAX_BONUS_MS)  # cap at 2x base
```

Emergency override: user can interrupt AI turn at any time.
Action queue: all actions (AI or user) go through simulation gate before execution.

```json
// PossessionState
{
  "character_id": "...",
  "controller": "user|ai|shared",
  "turn_owner": "user|ai",
  "turn_started_at": "iso8601",
  "turn_duration_ms": 5000,
  "bonus_applied": true,
  "override_available": true
}
```

---

### 5. skill_forge.py + skill_packer.py — Skill Creation

**skill_forge.py:**
- Takes a story beat (or sequence of beats)
- Extracts reusable pattern
- Attaches visual profile (for Godot rendering)
- Creates `SkillManifest`

**skill_packer.py:**
- Packages skill into `.dhskill.zip`
- ZIP contains: `manifest.json`, `actions.json`, `visual_profile/`, `preview.png`
- Computes checksum
- Writes to `skills/{skill_id}.dhskill.zip`

```json
// SkillManifest (inside .dhskill.zip)
{
  "skill_id": "uuid",
  "name": "...",
  "version": "1.0.0",
  "schema_version": "1",
  "story_roles": ["protagonist", "antagonist"],
  "actions": [...],
  "visual_profile": {"theme": "...", "color": "...", "animation": "..."},
  "dependencies": [],
  "compatibility": {"godot": "4.x", "dh_version": "2.0"},
  "checksum": "sha256:..."
}
```

---

### 6. Presentation Surfaces

**Browser (port 8011):**
- `dashboard.html` — ecosystem status, story list, possession state, skill library
- `story_deck.html` — beat-by-beat story viewer, SSE-driven, presentation mode

**Godot:**
- `devils_hand_stage.tscn` — main 3D stage, receives beat data via HTTP
- `demon_hand_overlay.tscn` — demon hand that cues actions, highlights possession targets
- `story_player.gd` — polls `/storyboards`, renders current beat
- `demon_hand_controller.gd` — animates hand for: cueing, possession, strike, preview path
- `theme_switcher.gd` — phrase-driven hot-reload: `"switch theme dark"` → applies instantly

**Demon hand visual contract:**
- Cueing: point at next action target
- Possession highlight: glow ring around target character
- Action preview path: dashed arc showing proposed move
- Click-strike: fast snap animation on confirmed action

---

### 7. Competition + Perfection Loop

Per beat, both AI and user submit proposals:
1. `POST /control/propose` (from AI)
2. `POST /control/propose` (from user, within turn window)
3. Runtime replays both in simulation
4. Scoring: coherence + detail richness + continuity + safety
5. Best elements merged into canonical branch
6. "Devil's in the detail" pass: final refinement before commit
7. `POST /story/{id}/commit_canon`

---

### 8. Simulation Gate (Safety)

All real OS actions blocked until phase-gate tests pass:
```python
class SimulationGate:
    REAL_OS_UNLOCKED = False  # stays False until acceptance suite passes

    def execute(self, action):
        if action.requires_real_os and not self.REAL_OS_UNLOCKED:
            return {"blocked": True, "reason": "simulation gate active"}
        return self._run(action)
```

---

## Data Flow Summary

```
user_prompt
  → prompt_ingest (normalize, split by comma)
  → basket_router (classify fragments → story threads)
  → basket_output.json
  → storyboard_compiler (compile beats)
  → story_runtime (execute, branch, merge, snapshot)
  → possession_engine (who controls what, token turns)
  → simulation_gate (safety check)
  → [action executes OR is blocked]
  → skill_forge (if beat is good → package as skill)
  → surface_server (push to browser + Godot via SSE)
```
