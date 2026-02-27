## i might have made it first here

## Devil’s Hand 2.0 - Story Skill Forge + Possession Ecosystem (V1)
Devil's Hand - Story Skill Forge + Possession Ecosystem Alpha
Summary
Build Devil’s Hand in D:\devil_s_hand as an always-running ecosystem launched from one main Python entrypoint.
It ingests messy prompts, routes intent through a professional “basket” layer, compiles storyboards, runs multi-story loops, and visualizes everything in Godot and browser as presentation surfaces.
Core gameplay includes possession and AI-vs-user co-control with token turns, adaptive bonus control time, rewind/merge timeline competition, and reusable visual skills packaged as hybrid ZIP artifacts.

Core Product Decisions (Locked)
Canonical workspace: D:\devil_s_hand.
Runtime launch model: one main file starts full ecosystem.
Skill artifact format: hybrid ZIP (.dhskill.zip).
Control model: token turns with dynamic bonus time for user inactivity.
Real-world OS control: simulation-first gate remains mandatory.
Multi-story behavior: v1 includes simultaneous story runtime as a core backend feature.
Surfaces: Godot + browser both treated as live presentation decks.
Data model: JSON-first (“Excel as JSON”), with archive/chunk/cache lifecycle.
System Architecture
1) Main Ecosystem Launcher
File: devils_hand_main.py
Responsibilities:
Boot dependency checks.
Start subsystems in deterministic order.
Maintain heartbeat loop (“train loop”).
Restart failed workers by policy.
Expose global status and kill/pause/resume endpoints.
2) Story Intake and Basket Routing
Files:
prompt_ingest.py
basket_router.py
Behavior:
Accept free-form, messy prompt text.
Extract intent from noise.
Map fragments to active story threads.
Produce structured basket_output.json.
3) Storyboard Compiler + Runtime
Files:
storyboard_compiler.py
story_runtime.py
Behavior:
Compile basket output into beat-by-beat storyboard.
Support timeline rewind, branch, merge, canon commit.
Keep multi-story instances active with cross-story event bus.
4) Possession and Co-Control Engine
File: possession_engine.py
Behavior:
Token turn scheduler for AI and user.
- and as i could not controll main character i would spawn myself some other form to use currently and while!
Adaptive bonus logic: if user has low recent control share, user turn duration increases by configured multiplier.
Emergency override: user can interrupt AI turn.
Action queue routes through simulation gate.
5) Skill Forge (Visual + Story Skill Creation)
Files:
skill_forge.py
skill_packer.py
Behavior:
Convert story beats into reusable skills.
Attach visual profile for Godot rendering.
Pack to .dhskill.zip with manifest, schema version, preview metadata.
6) Presentation Surfaces
Browser:
dashboard.html
story_deck.html
Godot:
devils_hand_stage.tscn
demon_hand_overlay.tscn
story_player.gd
demon_hand_controller.gd
theme_switcher.gd
Visual contract:
Demon hand drives cueing, possession target highlighting, action preview path, and click-strike animation.
Theme switch via plain phrase/string command mapped to theme registry.
Public APIs / Contracts
Ecosystem Control API
POST /ecosystem/start
POST /ecosystem/pause
POST /ecosystem/resume
POST /ecosystem/stop
GET /ecosystem/status
Prompt and Story API
POST /prompt/ingest
GET /basket/latest
POST /storyboard/compile
GET /storyboards
POST /story/{id}/start
POST /story/{id}/rewind
POST /story/{id}/branch
POST /story/{id}/merge
POST /story/{id}/commit_canon
Possession API
POST /possession/request
POST /possession/release
GET /possession/state
POST /control/propose
POST /control/approve
POST /control/reject
GET /control/queue
Skill API
POST /skills/forge
POST /skills/package
GET /skills/list
POST /skills/load
GET /skills/{id}/manifest
Stream API
GET /events/stream (SSE)
GET /timeline/{story_id}/stream
Key Types (Schema Additions)
BasketOutput
prompt_id
raw_text
intents[]
story_targets[]
discarded_noise[]
confidence
StoryBeat
beat_id
story_id
scene
actors[]
actions[]
timeline_index
visual_cue
detail_weight
PossessionState
character_id
controller (user|ai|shared)
turn_owner
turn_started_at
turn_duration_ms
bonus_applied
override_available
SkillManifest (inside .dhskill.zip)
skill_id
name
version
schema_version
story_roles[]
actions[]
visual_profile
dependencies[]
compatibility
checksum
Multi-Story Loop Model (V1)
Stories run as concurrent instances with states: active, shadow, idle.
Active stories can exchange timeline messages through event bus.
Every story writes snapshots with save/load/archive/chunk/cache lifecycle.
Canon selection is per story, plus optional global “meta-canon” for synchronized arcs.
Loop scheduler revisits all active stories continuously and supports teleport jumps (direct state load to any checkpoint).
Competition and Perfection Loop
AI and user both submit move proposals per beat.
Runtime replays both branches in simulation.
Scoring function computes:
coherence score
detail richness score
continuity score
safety/constraint score
Best elements are merged into canonical branch.
“Devil’s in the detail” pass runs as final beat refinement stage before commit.
Implementation Sequence
Bootstrap repository and schema contracts.
Implement devils_hand_main.py launcher and health loop.
Implement prompt ingest + basket router.
Implement storyboard compiler and timeline storage.
Implement possession engine with token + adaptive bonus logic.
Implement simulation queue and approval workflow.
Implement skill forge + .dhskill.zip packer.
Implement browser dashboard/deck.
Implement Godot stage + demon hand overlay + theme switch.
Integrate multi-story concurrent scheduler and cross-story event bus.
Add archive/chunk/cache workers and recovery flows.
Run acceptance suite and lock phase gate before any real OS control.
Test Cases and Scenarios
Messy prompt parsing:
Input noisy multi-topic text.
Expect basket output with meaningful intents and explicit discarded noise.
Token fairness:
User idle for N turns.
Expect increased next user turn duration by configured bonus factor.
Emergency override:
AI currently controlling.
User override request should preempt within max latency target.
Multi-story cross-talk:
Two active stories exchange event payload.
Expect deterministic state update in both timelines.
Branch-merge quality:
AI and user submit divergent beat actions.
Expect replay, scoring, and deterministic merged canon.
Skill packaging:
Forge a skill from storyboard.
Expect valid .dhskill.zip with manifest and checksum.
Surface sync:
Same beat index visible in browser deck and Godot stage.
Simulation gate safety:
Real control actions queued before gate pass.
Expect blocked execution with explicit reason.
Recovery:
Kill one subsystem process.
Expect launcher restart and resumed loop without story corruption.
Archive lifecycle:
Snapshot rollover produces visible states: current, cached, chunked, archived.
Assumptions and Defaults
“Any language” is implemented via worker adapter contract; v1 core uses Python + GDScript + JS, with pluggable workers later.
Since you requested core multi-story behavior now, v1 includes concurrent stories despite higher complexity.
Adaptive bonus default:
bonus_multiplier = 1.5
max_bonus_turn_ms = 2x base turn
Canon merge default is automatic with user override option.
Godot is simulation/presentation first; real OS automation unlocks only after phase-gate tests pass.
Theme switching is phrase-driven and runtime hot-reloadable.

## didnt read after just title, it is clawdbot 2.0 named Devil's Hand, and we will be creative about story telling, mysteries