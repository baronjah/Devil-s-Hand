# Devil's Hand
**Story Skill Forge + Possession Ecosystem**

> One main file starts everything. Messy prompts go in, structured story comes out.
> AI and user co-control characters through token turns. Skills are packaged as `.dhskill.zip`.
> Visualized in Godot and browser simultaneously.

---

## Canonical Workspace
```
D:\devil_s_hand\
```

## Start Everything
```bash
python devils_hand_main.py
```
One entrypoint. Boots all subsystems in order. Keeps them alive. Exposes kill/pause/resume.

## Read Order for New AI (Codex / Gemini / Claude)
1. `README.md` — this file, orientation
2. `ARCHITECTURE.md` — all components, how they connect
3. `CONTRACTS.md` — all APIs, types, schemas
4. `IMPLEMENTATION_PLAN.md` — what to build in what order
5. `FOR_CODEX.md` or `FOR_GEMINI.md` — your specific assignment

## What This Is

A running ecosystem that:
- Accepts messy human prompts (fragmented, lowercase, no punctuation rules)
- Routes intent through a "basket" layer (like a professional receptionist)
- Compiles story beats into a timeline
- Runs multiple stories simultaneously with a shared event bus
- Lets AI and user fight over character control via token turns
- Packages story moments as reusable visual skills (`.dhskill.zip`)
- Shows everything in Godot (3D stage) and browser (dashboard + deck) simultaneously

## Philosophical Skills (Cursor AI Reconstructed)
- **✨ Miracle It Away (Healing):** Takes broken code or messy prompts and "miracles" them into a structured, perfect state via the LLM (Cleansing the Scriptura).
- **🛡️ Demonic Prevention (Prevention):** The Paranoia Agent scans for anomalies and strikes down "sinful" edits (breaking changes) before they can manifest in the story loop.

## Locked Decisions (Do Not Redesign)
| Decision | Value |
|----------|-------|
| Workspace | `D:\devil_s_hand` |
| Launch model | Single `devils_hand_main.py` |
| Skill format | `.dhskill.zip` hybrid ZIP |
| Control model | Token turns + adaptive bonus |
| Real OS control | Simulation-gate-first, always |
| Multi-story | Concurrent, v1 core feature |
| Surfaces | Godot + browser, both live |
| Data model | JSON-first, archive/chunk/cache lifecycle |

## Directory Layout
```
D:\devil_s_hand\
├── devils_hand_main.py       ← start here
├── prompt_ingest.py
├── basket_router.py
├── storyboard_compiler.py
├── story_runtime.py
├── possession_engine.py
├── skill_forge.py
├── skill_packer.py
├── dashboard.html
├── story_deck.html
├── schemas/
│   ├── basket_output.schema.json
│   ├── story_beat.schema.json
│   ├── possession_state.schema.json
│   └── skill_manifest.schema.json
├── docs/
│   ├── ARCHITECTURE.md
│   ├── CONTRACTS.md
│   └── IMPLEMENTATION_PLAN.md
├── godot/
│   ├── devils_hand_stage.tscn
│   ├── demon_hand_overlay.tscn
│   ├── story_player.gd
│   ├── demon_hand_controller.gd
│   └── theme_switcher.gd
├── stories/          ← runtime story state (JSON)
├── skills/           ← .dhskill.zip artifacts
├── snapshots/        ← checkpoint saves
└── logs/
```

## Project Custodians
- **Ecosystem:** Devil's Hand
- **Human Architect:** JSH

---
*Signed by JSH*
