# API Contracts — Devil's Hand

All servers use JSON. All responses include `{"ok": true}` or `{"error": "..."}`.
SSE streams use `text/event-stream`.

---

## Base URLs
| Service | Port | Base |
|---------|------|------|
| Main ecosystem | 8009 | http://localhost:8009 |
| Story + surface | 8010 | http://localhost:8010 |
| Surface/browser | 8011 | http://localhost:8011 |

---

## Ecosystem Control (port 8009)

```
POST /ecosystem/start         → boot all subsystems
POST /ecosystem/pause         → pause all loops, keep state
POST /ecosystem/resume        → resume from pause
POST /ecosystem/stop          → flush snapshots, shutdown
GET  /ecosystem/status        → {subsystems[], uptime, stories_active, heartbeat_ok}
```

---

## Prompt + Story (port 8010)

```
POST /prompt/ingest
  body: {"text": "raw messy prompt", "story_hint": "optional story_id"}
  returns: {"prompt_id": "...", "basket_output": BasketOutput}

GET  /basket/latest
  returns: BasketOutput

POST /storyboard/compile
  body: {"prompt_id": "..."}
  returns: {"story_id": "...", "beats": StoryBeat[]}

GET  /storyboards
  returns: [{"story_id": "...", "state": "active|shadow|idle", "beat_count": N}]

POST /story/{id}/start
POST /story/{id}/rewind        body: {"to_beat_id": "..."}
POST /story/{id}/branch        body: {"from_beat_id": "...", "label": "..."}
POST /story/{id}/merge         body: {"branch_a": "...", "branch_b": "..."}
POST /story/{id}/commit_canon  body: {"beat_id": "..."}
```

---

## Possession + Control (port 8010)

```
POST /possession/request       body: {"character_id": "...", "requester": "user|ai"}
POST /possession/release       body: {"character_id": "..."}
GET  /possession/state         returns: PossessionState

POST /control/propose          body: {"story_id": "...", "beat_id": "...", "action": StoryAction, "proposer": "user|ai"}
POST /control/approve          body: {"proposal_id": "..."}
POST /control/reject           body: {"proposal_id": "...", "reason": "..."}
GET  /control/queue            returns: [proposal...]
```

---

## Skills (port 8010)

```
POST /skills/forge             body: {"story_id": "...", "beat_ids": [...], "name": "..."}
                               returns: {"skill_id": "..."}
POST /skills/package           body: {"skill_id": "..."}
                               returns: {"path": "skills/xxx.dhskill.zip", "checksum": "..."}
GET  /skills/list              returns: [SkillManifest...]
POST /skills/load              body: {"path": "path/to/skill.dhskill.zip"}
GET  /skills/{id}/manifest     returns: SkillManifest
```

---

## Streams (SSE)

```
GET /events/stream
  events:
    story_beat     → {story_id, beat: StoryBeat}
    possession     → PossessionState
    turn_start     → {owner: "user|ai", duration_ms: N, bonus: bool}
    turn_end       → {owner: "...", action_taken: "..."}
    override       → {by: "user", at_ms: N}
    skill_forged   → SkillManifest
    subsystem_down → {name: "...", will_restart: bool}
    pulse          → {node_id, var, old_val, new_val, t}  ← debug visualization

GET /timeline/{story_id}/stream
  events:
    beat           → StoryBeat
    branch         → {from_beat, label}
    merge          → {branches: [...], result_beat_id}
    canon          → {beat_id}
    snapshot       → {beat_id, path}
```

---

## Types / Schemas

### BasketOutput
```json
{
  "prompt_id": "string (uuid)",
  "raw_text": "string",
  "intents": [
    {
      "fragment": "string",
      "story_target": "string (story_id or 'new')",
      "confidence": "float 0-1",
      "type": "action | branch | question | meta | noise"
    }
  ],
  "discarded_noise": ["string"],
  "confidence": "float 0-1",
  "timestamp": "iso8601"
}
```

### StoryBeat
```json
{
  "beat_id": "string (uuid)",
  "story_id": "string",
  "scene": "string (description)",
  "actors": ["character_id"],
  "actions": [
    {"actor": "string", "type": "string", "target": "string", "params": {}}
  ],
  "timeline_index": "int",
  "visual_cue": "string",
  "detail_weight": "float 0-1",
  "branch_of": "beat_id | null",
  "is_canon": "bool",
  "snapshot_path": "string | null"
}
```

### PossessionState
```json
{
  "character_id": "string",
  "controller": "user | ai | shared",
  "turn_owner": "user | ai",
  "turn_started_at": "iso8601",
  "turn_duration_ms": "int",
  "bonus_applied": "bool",
  "bonus_multiplier": "float",
  "override_available": "bool",
  "user_control_share_last_10": "float 0-1"
}
```

### SkillManifest
```json
{
  "skill_id": "string (uuid)",
  "name": "string",
  "version": "semver",
  "schema_version": "1",
  "story_roles": ["string"],
  "actions": ["StoryAction"],
  "visual_profile": {
    "theme": "string",
    "primary_color": "#hex",
    "animation_hint": "string",
    "preview_frame": "int"
  },
  "dependencies": ["skill_id"],
  "compatibility": {"godot": "4.x", "dh_version": "2.0"},
  "checksum": "sha256:string"
}
```

### .dhskill.zip contents
```
skill_id.dhskill.zip
├── manifest.json       ← SkillManifest
├── actions.json        ← action sequence
├── visual_profile/
│   ├── theme.json
│   └── preview.png
└── README.txt          ← human-readable description
```

---

## Adaptive Bonus Defaults
```python
BONUS_MULTIPLIER     = 1.5
MAX_BONUS_TURN_MS    = 2 * BASE_TURN_MS
INACTIVITY_THRESHOLD = 0.3   # if user had <30% of last 10 turns, bonus applies
BASE_TURN_MS         = 10000 # 10 seconds base turn
```

## Simulation Gate
```python
REAL_OS_UNLOCKED = False  # do not change until acceptance suite passes
# Actions that require real OS: mouse_click, keyboard_type, file_write, process_spawn
# All others: safe in simulation
```
