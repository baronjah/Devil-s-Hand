# Implementation Plan — Devil's Hand

Build in this order. Each step has a clear done condition. Do not skip steps.

---

## Step 1 — Bootstrap + Schema
**Build:** directory structure, schema JSON files, shared constants
**Done when:** `D:\devil_s_hand\schemas\*.json` exist and validate

Files:
- `schemas/basket_output.schema.json`
- `schemas/story_beat.schema.json`
- `schemas/possession_state.schema.json`
- `schemas/skill_manifest.schema.json`
- `shared_types.py` — dataclasses matching schemas, used everywhere

---

## Step 2 — Main Launcher
**Build:** `devils_hand_main.py`
**Done when:** running it prints subsystem status, `/ecosystem/status` returns JSON, kill/pause/resume work

Key logic:
```python
class Subsystem:
    name: str
    start_fn: callable
    health_fn: callable   # returns bool
    restart_count: int = 0
    MAX_RESTARTS = 3

# heartbeat loop: every 10s check all subsystems
# if health_fn() returns False: attempt restart
# after MAX_RESTARTS: mark as degraded, keep others running
```

---

## Step 3 — Prompt Ingest + Basket Router
**Build:** `prompt_ingest.py`, `basket_router.py`
**Done when:** messy text in → `basket_output.json` out with meaningful intents

Test input:
```
"fix the bug in story node, also i want new character, hmm that scene from yesterday..."
```
Expected: 3 intents, 1 story target each, noise discarded

Implementation notes:
- Split on comma first (user's writing style)
- Use `lfm` (fast local LLM) for classification
- Fallback: if confidence < 0.6, flag as noise, do NOT guess

---

## Step 4 — Storyboard Compiler + Story Runtime
**Build:** `storyboard_compiler.py`, `story_runtime.py`
**Done when:** basket_output → beats[] → story runs + snapshot saved

Key feature: multi-story concurrent loop
```python
class StoryScheduler:
    stories: dict[str, Story]   # all active instances

    def tick(self):
        for story in self.active_stories():
            story.advance_one_beat()
            story.write_snapshot()
        self.process_cross_story_events()
```

Snapshot lifecycle:
```
current → (after N beats) → cached → (after M beats) → chunked → archived
```

---

## Step 5 — Possession Engine
**Build:** `possession_engine.py`
**Done when:** token turns work, bonus logic applies, override interrupts AI turn

```python
def compute_turn_duration(owner: str, recent_history: list) -> int:
    base = BASE_TURN_MS
    if owner == "user":
        user_share = sum(1 for t in recent_history[-10:] if t == "user") / 10
        if user_share < INACTIVITY_THRESHOLD:
            bonus = base * BONUS_MULTIPLIER
            return min(bonus, MAX_BONUS_TURN_MS)
    return base
```

---

## Step 6 — Simulation Queue + Approval Workflow
**Build:** `simulation_gate.py`
**Done when:** all actions pass through gate, real OS blocked, simulation runs cleanly

All actions flow:
```
propose → queue → simulate → score → approve/reject → execute|block
```

---

## Step 7 — Skill Forge + Packer
**Build:** `skill_forge.py`, `skill_packer.py`
**Done when:** beats → `.dhskill.zip` with valid manifest + checksum

```python
import zipfile, hashlib, json

def pack_skill(manifest, actions, visual_profile, preview_img):
    path = f"skills/{manifest['skill_id']}.dhskill.zip"
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr("actions.json", json.dumps(actions))
        z.writestr("visual_profile/theme.json", json.dumps(visual_profile))
        if preview_img: z.write(preview_img, "visual_profile/preview.png")
        z.writestr("README.txt", manifest["name"])
    manifest["checksum"] = "sha256:" + _checksum(path)
    return path
```

---

## Step 8 — Browser Surfaces
**Build:** `dashboard.html`, `story_deck.html`
**Done when:** dashboard shows live ecosystem status via SSE, story deck shows current beat

`dashboard.html` panels:
- Ecosystem health (all subsystems green/red)
- Active stories list + state
- Possession state (who controls what, turn timer)
- Skill library (loaded .dhskill.zip files)
- Control queue (pending proposals)

`story_deck.html`:
- Full-screen beat viewer
- Scene text, actors, current action
- Timeline scrubber (branch/canon visible)
- Presentation mode (clean, no chrome)

---

## Step 9 — Godot Stage + Demon Hand
**Build:** GDScript files for Godot 4.x
**Done when:** stage shows current beat, demon hand animates on possession/action

Files:
- `story_player.gd` — polls `GET /storyboards`, updates scene text + actor positions
- `demon_hand_controller.gd` — 4 animations: `cue`, `possess`, `preview_path`, `strike`
- `theme_switcher.gd` — listens for string commands, hot-swaps theme resource

Demon hand trigger via HTTP or SSE `pulse` event.

---

## Step 10 — Multi-Story Scheduler + Event Bus
**Build:** cross-story event bus (already scaffolded in story_runtime.py)
**Done when:** two stories can exchange events, state updates deterministically in both

```python
class CrossStoryEventBus:
    def emit(self, from_story_id, event_type, payload):
        for story_id, story in scheduler.stories.items():
            if story_id != from_story_id:
                story.receive_event(event_type, payload)
```

---

## Step 11 — Archive + Recovery Workers
**Build:** snapshot rollover, archive worker, recovery on restart
**Done when:** killing a subsystem mid-story → restart → story continues from last snapshot

---

## Step 12 — Acceptance Suite (Phase Gate)
**Build:** `tests/acceptance.py`
**Done when:** all 10 test scenarios pass (see CONTRACTS.md or README)

**REAL OS CONTROL IS LOCKED UNTIL THIS PASSES.**

---

## Parallel Work Notes for Multiple AIs

Codex can work on: Steps 1-6 (Python backend)
Gemini can work on: Steps 8-9 (HTML surfaces + Godot GDScript)
Claude can do: architecture review, integration, basket router LLM logic

Shared files to never conflict on:
- `shared_types.py` — coordinate before touching
- `schemas/*.json` — locked after Step 1

Communication: leave notes in `docs/CODEX_NOTES.md` and `docs/GEMINI_NOTES.md`
