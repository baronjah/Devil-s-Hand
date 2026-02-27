# For Codex — Devil's Hand

## Your Role
Backend Python. Steps 1–6 of the implementation plan.

## Read First
1. `README.md` — orientation
2. `ARCHITECTURE.md` — full system design
3. `CONTRACTS.md` — all types and APIs you must implement
4. This file

## Your Assignment

### Step 1: schemas + shared_types.py
Create `schemas/*.json` (JSON Schema format) and `shared_types.py` with Python dataclasses.
All other files import from `shared_types.py`. This is the foundation.

### Steps 2–6: Core backend
Build in order: launcher → ingest → basket → compiler → runtime → possession → gate

## Key Constraints
- Workspace: `D:\devil_s_hand\`
- Python only in your area (no GDScript, no HTML)
- All JSON I/O uses `shared_types.py` dataclasses
- `REAL_OS_UNLOCKED = False` — do not change, do not route real OS actions
- Local LLM via Ollama at `http://localhost:11434/api/chat`
  - Use `lfm` model for fast classification (basket router)
  - Use `gemma` model for beat generation
- No external dependencies except: `fastapi`, `uvicorn`, `httpx`

## Ollama Call Pattern
```python
import httpx, json

async def llm_call(model: str, messages: list, max_tokens: int = 100) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post("http://localhost:11434/api/chat", json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"num_predict": max_tokens, "repeat_penalty": 1.4}
        })
        return r.json()["message"]["content"].strip()
```

## Basket Router LLM Prompt Pattern
```python
# lfm is tiny — give it VERY explicit format with example
BASKET_PROMPT = """You route message fragments to story threads.
Active threads: {threads}
Fragment: "{fragment}"
Reply with ONLY: thread_id OR 'new' OR 'noise'
Example: story_abc123"""
```

## File Structure You Own
```
devils_hand_main.py
prompt_ingest.py
basket_router.py
storyboard_compiler.py
story_runtime.py
possession_engine.py
simulation_gate.py
skill_forge.py
skill_packer.py
shared_types.py
schemas/
stories/       ← write runtime state here
snapshots/     ← write snapshots here
skills/        ← write .dhskill.zip here
logs/
```

## Leave Notes Here
`docs/CODEX_NOTES.md` — what you built, what's incomplete, any blockers.

## When You're Done With a Step
Write to `docs/CODEX_NOTES.md`:
```
STEP N DONE: [date]
Files: [list]
Endpoints working: [list]
Known issues: [list]
Next step: [N+1]
```
