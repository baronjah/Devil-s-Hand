# Devil's Hand 2.0

Story Skill Forge + Possession Ecosystem (V1).

## Run

```powershell
cd D:\devil_s_hand
python devils_hand_main.py
```

Server defaults to `http://127.0.0.1:8010`.

## Surfaces

- Dashboard: `/dashboard`
- Story deck: `/deck`
- SSE events: `/events/stream`

## Core APIs

- `POST /ecosystem/start|pause|resume|stop`
- `GET /ecosystem/status`
- `POST /prompt/ingest`
- `GET /basket/latest`
- `POST /storyboard/compile`
- `GET /storyboards`
- `POST /story/{id}/start|rewind|branch|merge|commit_canon`
- `POST /possession/request|release`
- `GET /possession/state`
- `POST /control/propose|approve|reject`
- `GET /control/queue`
- `POST /skills/forge|package|load`
- `GET /skills/list`
- `GET /skills/{id}/manifest`
- `POST /theme/switch`
- `GET /theme/current`

## Data Model

JSON-first tables and state live under `data/`.

- `data/inbox/prompts.ndjson`
- `data/state/basket_output.json`
- `data/state/runtime_state.json`
- `data/storyboards/*.json`
- `data/tables/*.json`

## Safety

Simulation-first gate is enabled by default.
Real control remains blocked until `phase_gate_passed` is true and simulation mode is disabled.

---
Signature: JSH

