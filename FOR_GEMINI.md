# For Gemini — Devil's Hand

## Your Role
Frontend surfaces: browser HTML/JS (Steps 8) + Godot GDScript (Step 9).

## Read First
1. `README.md` — orientation
2. `ARCHITECTURE.md` — section 6 "Presentation Surfaces"
3. `CONTRACTS.md` — SSE stream events you must consume
4. This file

## Your Assignment

### Step 8: Browser Surfaces
Two HTML files. Both consume SSE from `GET /events/stream` (port 8010).

**dashboard.html**
- Dark theme (bg #080810, accent #7c6af7)
- Panels: ecosystem health, active stories, possession state, skill library, control queue
- All data via SSE — no page refresh ever
- Mobile-friendly (user reads this on iPhone 14 Pro Max, Chrome)
- Each subsystem: colored dot (green=ok, yellow=degraded, red=down)
- Turn timer: visual countdown bar, shows whose turn (user=blue, ai=purple)

**story_deck.html**
- Full-screen presentation mode
- Large scene text (center, readable from distance)
- Current actors listed
- Timeline bar at bottom: canon=solid, branch=dashed, current position marked
- Beat navigation: prev/next buttons (large, thumb-friendly)
- Keyboard: arrow keys also work

SSE events to handle:
```javascript
// From GET /events/stream
'story_beat'     → update current beat display
'possession'     → update turn indicator
'turn_start'     → start countdown timer
'turn_end'       → stop timer
'override'       → flash "USER OVERRIDE" banner
'skill_forged'   → add to skill library panel
'subsystem_down' → update health dot
'pulse'          → optional: flash debug indicator
```

### Step 9: Godot Stage
Godot 4.x. Target Godot project: create `godot/` folder with these files.

**story_player.gd**
```gdscript
# Polls GET http://localhost:8010/storyboards every 2 seconds
# Updates scene label text
# Moves actor nodes based on beat data
# Emits signal when beat changes (for demon hand to react)
```

**demon_hand_controller.gd**
```gdscript
# 4 animation states:
# - cue: point at next action target
# - possess: glow ring appears around target
# - preview_path: dashed arc shows proposed move
# - strike: fast snap on confirmed action

# Triggered by: HTTP poll OR SSE pulse event
# Theme-aware: reads from ThemeRegistry resource
```

**theme_switcher.gd**
```gdscript
# Listens for string commands from any source
# Maps phrase → theme resource
# Commands: "switch theme dark" / "switch theme fire" / "switch theme void"
# Hot-reloads without scene restart
```

## Visual Contract (DO NOT change these)
- Demon hand ALWAYS visible when story is active
- Hand color matches current controller: blue=user, purple=ai
- Possession target has animated glow ring (not a static highlight)
- Action preview path uses dashed arc with arrowhead
- Strike animation: scale 1.0 → 1.3 → 0.9 → 1.0, 8 frames, ease-out

## SSE Connection Pattern (browser)
```javascript
const es = new EventSource('http://localhost:8010/events/stream');
es.addEventListener('story_beat', e => {
    const beat = JSON.parse(e.data);
    updateScene(beat);
});
// heartbeat every 5s keeps connection alive on iOS Chrome
```

## File Structure You Own
```
dashboard.html
story_deck.html
godot/
  devils_hand_stage.tscn
  demon_hand_overlay.tscn
  story_player.gd
  demon_hand_controller.gd
  theme_switcher.gd
```

## Coordination with Codex
- You consume Codex's SSE stream — don't implement the server, just consume it
- If Codex's stream isn't ready: stub with `test_sse_server.py` that emits fake events every 3s
- Use `docs/GEMINI_NOTES.md` to log what you built and any blockers

## Leave Notes Here
`docs/GEMINI_NOTES.md`
```
STEP N DONE: [date]
Files: [list]
SSE events working: [list]
Known issues: [list]
```
