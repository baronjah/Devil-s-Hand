# Pathways

Pathways describe where Devil's Hand routes flow, and what each place is for.

## Core Pathways

1. `prompt -> basket -> storyboard`
- Source: messy human/AI text.
- Destination: structured story beats and tasks.

2. `storyboard -> runtime loop`
- Source: compiled beats/timeline.
- Destination: active, shadow, and idle story instances.

3. `runtime -> surfaces`
- Source: timeline ticks and control events.
- Destinations:
- Godot scene (`godot/DevilsHandSim`) for simulation visuals.
- Browser deck/dashboard (`web/`) for presentation and operations.

4. `control queue -> approval gate`
- Source: AI/user proposed actions.
- Destination: simulation execution by default, real execution only after gate unlock.

5. `story skill forge -> package`
- Source: finalized story details.
- Destination: `.dhskill.zip` artifacts in `skills/packages`.

## Place Explanations

- `data/inbox`: raw prompt intake history.
- `data/state`: live ecosystem state and current basket output.
- `data/storyboards`: canonical and branch-ready story JSON.
- `data/tables`: actor/scene/task tables (JSON-first "excel").
- `cast`: operator personas and routing roles.
- `stories/packs`: prewritten story packs for testing and iteration.

## Guiding Rule

Devil's Hand always keeps a return path: rewind, branch, merge, commit.
