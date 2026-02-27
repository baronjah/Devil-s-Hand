# Session Handoff — 2026-02-27 ~17:30
## Pick this up exactly here next session

---

## What Was Built This Session

| File | Port | Status | Purpose |
|------|------|--------|---------|
| `phone_ai.py` | 8080 | ✅ working | Text chat for phone, gemma model |
| `brain.py` | 8002 | ✅ working | Graph engine: nodes/paths/constructions/basket |
| `game.py` | 8003 | ⚠️ SSE issues | Timer decision game, push channel |
| `cast/surgeon.txt` | — | ✅ written | Dr. Veselin persona |

## What Still Needs Fixing

### 8003 game.py — SSE not reliable
**Symptom:** Auto-pick fires even when user clicked, push messages may not arrive
**Root cause suspects:**
1. `curl -X POST localhost:8003/push` was run as background bash task (wrong) — should be foreground
2. SSE heartbeat every 20s may drop on iOS Chrome (use 5s)
3. The `G.picked_scenes` set fix is correct in theory but needs testing

**To fix next session:**
```python
# In game.py — change heartbeat interval:
time.sleep(5)  # was 20s — iOS Chrome drops longer

# Test push manually:
import urllib.request, json
urllib.request.urlopen(urllib.request.Request(
    "http://localhost:8003/push",
    json.dumps({"message":"test","type":"note"}).encode(),
    {"Content-Type":"application/json"}
))
```

### Visual Debugging Idea (NEW — save this)
**Concept:** Every variable/data change creates a visual event
- Each node in brain.py has state that changes
- When value changes → emit a "pulse" event with: var_name, old_val, new_val, timestamp, node_id
- These pulses can be visualized as:
  - Flashes on Godot neuron nodes
  - Timeline bars (like Luminus Phase 5)
  - Color gradients on pathways (hot = recently changed)
- This IS the debugging — not a separate tool, the data IS the picture
- "places and reasons for something is like debugging more in one picture"

**Implementation sketch:**
```python
# In brain.py nodes, wrap every history.append() with:
def pulse(node_id, event_type, data):
    PULSES.append({
        "t": time.time(), "node": node_id,
        "type": event_type, "data": data
    })
    push_to_clients("pulse", {...})  # SSE to any viewer

# GET /pulses — returns timeline of all state changes
# Godot connects to this SSE stream and lights up nodes
```

---

## Architecture State

```
D:\AI_COORDINATION\
├── phone_ai.py       — chat server (port 8080)
├── brain.py          — graph engine (port 8002)
├── game.py           — timer game (port 8003)
├── chat_server.py    — old simple chat (deprecated)
├── backend_api.py    — existing FastAPI (port 8000, don't touch)
├── cast/
│   └── surgeon.txt   — Dr. Veselin persona
├── graph_data/
│   ├── graph.json    — node/path state (persists)
│   └── constructions.json
└── PROMPTS/
    ├── CLAUDE/PROMPT_AUTOMATION_ORCHESTRATOR_2026-02-27.md
    ├── parsed_vision_2026-02-27.md
    └── SESSION_HANDOFF_2026-02-27.md  ← this file
```

## Ollama Models
```
lfm       1.2GB  — fast routing/choices (0.4s)
gemma     2.2GB  — instruction-tuned chat (2-3s)  ← main model
qwen-vl   4.8GB  — vision, reads screenshots (13s)
oss       20B    — BASE model, ignores instructions, creative only
```
**Key:** gemma is the only reliably instruction-following local model.
`oss` is a base completion model — not usable for chat/instructions.

## Brain.py API (port 8002)
```
POST /message          — send message, routes to right node automatically
GET  /graph            — full graph JSON
GET  /status           — current node, active contexts
POST /node/add         — {"label":"X", "context":"system prompt", "note":"why"}
POST /path/add         — {"src":"node1", "dst":"node2", "label":"why"}
POST /node/{id}/go     — switch to node
POST /construction/save — {"name":"X", "nodes":["id1","id2"]}
POST /construction/use  — {"name":"X"}
GET  /cast             — all cast files
POST /cast/add         — {"name":"surgeon", "content":"..."}
```

## Phone Access
- PC IP: 172.20.10.3 (phone is the hotspot)
- Chat: http://172.20.10.3:8080
- Brain: http://172.20.10.3:8002/status
- Game: http://172.20.10.3:8003

## Next Session Prompt
"Read SESSION_HANDOFF_2026-02-27.md in D:\AI_COORDINATION\PROMPTS\
Fix the SSE reliability in game.py (iOS Chrome drops), test push messages,
then implement the visual debugging pulse system in brain.py."

---

## The Big Vision (not yet built)

### Scriptura IDE — Godot
- Plasmoids = neurons (MeshInstance3D spheres, glow shader)
- Pathways = Path3D + Curve3D bezier tubes between neurons
- Each neuron = a brain.py node (live connection via HTTP)
- When node receives message → neuron pulses (scale tween + color flash)
- When pathway is traversed → energy particle travels along Path3D
- Variable changes → color shift on neuron (hotter = more active)
- This is the visual debugger built into the IDE itself

### 12-Step System
User has written extensively about a "12-step system / step-turn system"
Need to find these notes — ask user where they are next session.

### Puppeteer Plasmoids
- Bootstrapping agents that use "strings" to move characters
- Metaphor for: lightweight coordinator agents that don't do work themselves
- Just pull the right string at the right time
- Could be the orchestration layer between brain.py nodes

### Interface Creation App
- Fully offline, phone-controlled
- Auto-generates simple HTML interfaces
- Each interface has a "note" explaining what it was for
- User said "we must leave notes on these sites"
- Basically: brain.py node → auto-generate a phone UI for that node's context



Worked for 23m 12s
I’ll inspect that handoff file directly and summarize what’s inside so we can plan from the current session state. I’m reading SESSION_HANDOFF_2026-02-27.md now.

Ran Set-Location 'D:/AI_COORDINATION/PROMPTS'; Get-Content 'SESSION_HANDOFF_2026-02-27.md'


I’ve read the handoff and extracted the active workstreams: game.py SSE reliability on port 8003, then visual pulse-debugging in brain.py on 8002. I’ll lock a decision-complete plan next based on which stream you want first.




Asked 1 question
Which plan should I produce first from this handoff?
SSE fix first (Recommended)
I’m now grounding the SSE plan in actual code by inspecting game.py and related logs, so the plan matches the current implementation instead of the handoff notes alone.

Ran Set-Location 'D:/godot_projects/Luminus_february_project'; if (Test-Path 'godot_console.txt') { Get-Content 'godot_console.txt' } else { 'MISSING: godot_console.txt' }


Ran Set-Location 'D:/AI_COORDINATION'; Get-Content 'game.py'


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "SSE|sse|event|push|picked|autopick|heartbeat|sleep|stream|choice|timeout" 'game.py'


I’ve confirmed game.py currently uses a 5s SSE heartbeat already, so the remaining reliability risk is likely race/connection handling and stale-choice behavior. I’m checking surrounding project files for any existing tests or integration patterns we should align with.

Ran Set-Location 'D:/AI_COORDINATION'; rg --files


Ran Set-Location 'D:/AI_COORDINATION'; if (Test-Path 'PROMPTS/CLAUDE/PROMPT_AUTOMATION_ORCHESTRATOR_2026-02-27.md') { Get-Content 'PROMPTS/CLAUDE/PROMPT_AUTOMATION_ORCHESTRATOR_2026-02-27.md' -TotalCount 220 } else { 'MISSING orchestrator prompt' }


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "game.py|/stream|EventSource|/push|/choice|auto_choice|picked_scenes" -g "*.md" -g "*.py"


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "8003|game.py|/start|/stream|/choice|/push|EventSource|SSE|decision engine" TESTS README.md QUICK_REFERENCE.md INDEX.md


I didn’t find existing tests/docs covering this game server, so I’m extracting exact line-level behavior now to base a concrete reliability test matrix on the current code paths.

Ran Set-Location 'D:/AI_COORDINATION'; $lines = Get-Content 'game.py'; for($i=250; $i -le 335; $i++){ if($i -le $lines.Length){ '{0}:{1}' -f $i, $lines[$i-1] } }


Ran Set-Location 'D:/AI_COORDINATION'; $lines = Get-Content 'game.py'; for($i=86; $i -le 130; $i++){ if($i -le $lines.Length){ '{0}:{1}' -f $i, $lines[$i-1] } }


Ran Set-Location 'D:/AI_COORDINATION'; $lines = Get-Content 'game.py'; for($i=410; $i -le 485; $i++){ if($i -le $lines.Length){ '{0}:{1}' -f $i, $lines[$i-1] } }


I found a likely core issue: game.py uses single-threaded HTTPServer while /stream holds a request open forever. I’m running a quick local, non-mutating repro to verify that this blocks /choice//push//status under active SSE.

Ran @' import subprocess, time, urllib.request, urllib.error, socket p = subprocess.Popen(["python", "D:/AI_COORDINATION/game.py"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) try: started = False t0 = time.time() while time.time() - t0 < 8: line = p.stdout.readline() if not line: time.sleep(0.1) continue if "Game server:" in line: started = True break if not started: print("START_FAIL") else: s = urllib.request.urlopen("http://127.0.0.1:8003/stream", timeout=2) print("STREAM_OPEN") try: r = urllib.request.urlopen("http://127.0.0.1:8003/status", timeout=2) body = r.read().decode("utf-8", errors="replace") print("STATUS_OK", body) except Exception as e: print("STATUS_ERR", type(e).__name__, str(e)) s.close() finally: p.kill() try: p.wait(timeout=2) except Exception: pass '@ | python -


Ran Get-NetTCPConnection -LocalPort 8003 -ErrorAction SilentlyContinue | Select-Object -First 5 -Property LocalAddress,LocalPort,State,OwningProcess


Ran @' import urllib.request, time try: s = urllib.request.urlopen('http://127.0.0.1:8003/stream', timeout=3) print('STREAM_OPEN') try: r = urllib.request.urlopen('http://127.0.0.1:8003/status', timeout=3) print('STATUS_OK', r.read().decode('utf-8', errors='replace')) except Exception as e: print('STATUS_ERR', type(e).__name__, e) s.close() except Exception as e: print('STREAM_ERR', type(e).__name__, e) '@ | python -


Ran @' import urllib.request, json s = urllib.request.urlopen('http://127.0.0.1:8003/stream', timeout=3) print('STREAM_OPEN') req = urllib.request.Request('http://127.0.0.1:8003/push', data=json.dumps({'message':'probe','type':'note'}).encode(), headers={'Content-Type':'application/json'}) try: r = urllib.request.urlopen(req, timeout=3) print('PUSH_OK', r.read().decode('utf-8', errors='replace')) except Exception as e: print('PUSH_ERR', type(e).__name__, e) s.close() '@ | python -


Ran @' import urllib.request, json req = urllib.request.Request('http://127.0.0.1:8003/push', data=json.dumps({'message':'probe2','type':'note'}).encode(), headers={'Content-Type':'application/json'}) r = urllib.request.urlopen(req, timeout=3) print(r.read().decode('utf-8', errors='replace')) '@ | python -


Ran $p = Get-CimInstance Win32_Process -Filter "ProcessId=20484"; if ($p) { $p | Select-Object ProcessId,Name,CommandLine | Format-List } else { 'MISSING' }


The repro is clear: once /stream is open, /status and /push time out, which confirms the single-threaded server is the main reliability blocker. I need one scope decision before I lock the implementation plan.





Asked 1 question
How far should the SSE reliability fix go in this pass?
i like this choices, that appeared after i described what i wanna, we can use any language for backend, we just need sequence of what opens what, maybe one script can make like combo of all programs opening, all working
Your note adds a broader requirement beyond SSE: a reliable startup sequence (possibly one launcher script) that brings all services up in the right order. I’m checking what startup scripts/docs already exist so we can plan this without duplicating work.

Ran Set-Location 'D:/AI_COORDINATION/KNOWLEDGE'; if (Test-Path 'START_BACKEND_API.md') { Get-Content 'START_BACKEND_API.md' -TotalCount 260 } else { 'MISSING START_BACKEND_API.md' }


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "ollama serve|python .*brain.py|python .*phone_ai.py|python .*game.py|startup|start.*server|launch|orchestrator|run all|combo|sequence|port 8002|port 8003|8080" -g "*.md" -g "*.py"


Ran Set-Location 'D:/AI_COORDINATION'; Get-Content 'README.md' -TotalCount 260


I can include that startup-combo requirement directly in the plan; to make it decision-complete I need two concrete choices.






Asked 2 questions
What should this plan include now?
SSE + launcher plan (Recommended)
If we include the startup combo, what format do you want?
Python supervisor (Recommended)
I’ll now inspect phone_ai.py and brain.py startup behavior and dependencies so the launcher sequence is concrete (order, readiness checks, failure handling).

Ran Set-Location 'D:/AI_COORDINATION'; Get-Content 'phone_ai.py'


Ran Set-Location 'D:/AI_COORDINATION'; Get-Content 'brain.py'


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "PORT|localhost:11434|ollama|HTTPServer|serve_forever|/status|/graph|/message|/cast|graph_data|load|save|MODEL|sys\.stdout|Run:" 'phone_ai.py' 'brain.py'


Ran Get-NetTCPConnection -LocalPort 8000,8002,8003,8080,11434 -ErrorAction SilentlyContinue | Select-Object LocalAddress,LocalPort,State,OwningProcess | Sort-Object LocalPort


Ran $p = Get-CimInstance Win32_Process -Filter "ProcessId=6712"; if ($p) { $p | Select-Object ProcessId,Name,CommandLine | Format-List } else { 'MISSING 6712' }


Ran $p = Get-CimInstance Win32_Process -Filter "ProcessId=25012"; if ($p) { $p | Select-Object ProcessId,Name,CommandLine | Format-List } else { 'MISSING 25012' }


Ran $p = Get-CimInstance Win32_Process -Filter "ProcessId=21876"; if ($p) { $p | Select-Object ProcessId,Name,CommandLine | Format-List } else { 'MISSING 21876' }


Ran $p = Get-CimInstance Win32_Process -Filter "ProcessId=27400"; if ($p) { $p | Select-Object ProcessId,Name,CommandLine | Format-List } else { 'MISSING 27400' }


I’ve confirmed all four processes are currently up (ollama, brain, game, phone_ai). I’m validating concrete health-check endpoints now so the launcher can reliably gate each startup step.

Ran @' import urllib.request, json checks = [ ('ollama_tags','http://127.0.0.1:11434/api/tags'), ('brain_status','http://127.0.0.1:8002/status'), ('game_status','http://127.0.0.1:8003/status'), ('phone_root','http://127.0.0.1:8080/'), ] for name, url in checks: try: r = urllib.request.urlopen(url, timeout=3) body = r.read(240).decode('utf-8', errors='replace') print(name, r.status, body[:160].replace('\n',' ')) except Exception as e: print(name, 'ERR', type(e).__name__, e) '@ | python -


Ran Set-Location 'D:/AI_COORDINATION'; rg --files -g "*.ps1" -g "*.bat" -g "*.cmd"




Asked 2 questions
Which processes should the combo launcher manage?
Ollama + 3 apps (Recommended)
If a target port is already in use at startup, what should launcher do?
for previous one we shall include something also? brain py? was it, i mashed button too fast, but i read you know, here i can add that we can translate what we made in godot to all that backedn for me to see it on phone and in godot, and choose here reuse, check if succesfull, if not, fully restart, an python script with delay of 10 seconds, that executes after time something, then it launches the same script copy but with different stuff later, to check it, again, and if not successful, we do something so i can help
I captured your policy as: try reuse, verify, then auto-restart if unhealthy, wait ~10s, recheck, and if still failing show actionable help prompts. I need two final behavior choices to lock the spec.





Asked 2 questions
For `game.py`, should we do minimal unblock or full reliability hardening?
Full hardening (Recommended)
How should the launcher interact with you while running?
the program shall know what device i am using, or what device i last used to interact, and shall look for me here, while doing everything anywhere too all the time kinda, well in bearable performance way, as it shall visualize me stuff in godot, and communicate with me in several apps at once i guess on several devices



Asked 1 question
For this pass, how deep should device-awareness/multi-app presence go?
multi app orchestration is important backend is needed to handle it all with task, schedule, queue, checking, rescheduling, waiting, delay, and much much more, with even list of all scripts to execute today, and make sure all of them run, and have a task scheduler to check on them each 10 minutes if all is alright, dashboards with info needed, interface creator is a way to talk with ai, with no words, just my touch
Ran if (Test-Path 'D:/AI_COORDINATION/orchestrator.py') { Get-Content 'D:/AI_COORDINATION/orchestrator.py' -TotalCount 260 } else { 'MISSING: D:/AI_COORDINATION/orchestrator.py' }


I confirmed orchestrator.py does not exist yet, so this would be net-new. I’m quickly checking backend_api.py capabilities to decide whether the plan should extend it or keep a separate supervisor/orchestrator process.

Ran Set-Location 'D:/AI_COORDINATION'; Get-Content 'backend_api.py' -TotalCount 320


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "interface creator|UI creator|no words|touch|dashboard|scheduler|queue" -g "*.md" SYSTEMS PROMPTS STATUS KNOWLEDGE


Ran Set-Location 'D:/AI_COORDINATION/STATUS'; Get-Content 'AGENT_DASHBOARD.md' -TotalCount 220





Asked 1 question
For the no-typing control interface in this pass, where should it live first?
Both now
You selected “Both now,” so the plan needs a web control surface plus a Godot panel wired to the same orchestration API. I’m mapping the current Godot project structure to choose exact integration files/scenes rather than leaving that ambiguous.

Ran Set-Location 'D:/godot_projects/Luminus_february_project'; rg -n "autoload|HTTP|HTTPRequest|dashboard|orchestrator|backend|port 800|localhost|panel|control" -g "*.gd" -g "*.tscn"


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'project.godot' -TotalCount 260


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; rg --files


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'autoload/http_server.gd'


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'scripts/ui/main_controller.gd'


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'scripts/ui/block_panel.gd'


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'scenes/main.tscn'


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'autoload/script_registry.gd'


I also found the Godot side has active compile errors in script_registry.gd/block_panel.gd, which affects any “both now” plan for an in-engine dashboard. I’m running a quick headless syntax check to anchor that risk in the plan.

Ran Set-Location 'D:/godot_projects/Luminus_february_project'; godot --headless --check-only


Ran where.exe Godot*


Ran where.exe godot4*



Asked 1 question
Ran Set-Location 'D:/godot_projects/Luminus_february_project'; if (Test-Path 'debugger_errors.txt') { Get-Content 'debugger_errors.txt' -TotalCount 260 } else { 'MISSING debugger_errors.txt' }


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; $lines = Get-Content 'autoload/script_registry.gd'; for($i=1; $i -le $lines.Length; $i++){ '{0}:{1}' -f $i, $lines[$i-1] }


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; $lines = Get-Content 'scripts/ui/block_panel.gd'; for($i=1; $i -le $lines.Length; $i++){ '{0}:{1}' -f $i, $lines[$i-1] }


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'autoload/twin_generator.gd'


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; rg -n "ScriptRegistry\.get_script\(|func get_script\(" -g "*.gd"


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'scenes/block_panel.tscn'





Asked 1 question
Should this plan also include the `brain.py` visual pulse-debugging system from the handoff, or keep it after SSE/orchestration?
Include pulses now
Including pulses now materially changes architecture, so I’m mapping the exact mutation points in brain.py where pulse events must be emitted and persisted.

Ran Set-Location 'D:/AI_COORDINATION'; rg -n "history\.append|GRAPH\[|save_graph|process_message|/message|/status|HTTPServer|do_GET|do_POST|paths\.append|active_nodes\.append" 'brain.py'







Asked 1 question
How much pulse visualization should be built in Godot during this pass?
Operational overlay (Recommended)




Asked 1 question
Where should “today’s scripts/tasks to execute” come from?
Dedicated JSON file (Recommended)





Asked 1 question
What execution scope should orchestrator allow for queued scripts?
Allowlist paths (Recommended)




Asked 1 question
Which channels should receive orchestrator health/task alerts in this pass?
Dashboard + game + Godot (Recommended)







Asked 1 question
Should orchestrator queue/schedule state survive restarts?
Persist to JSON (Recommended)
I have enough constraints locked to finalize a decision-complete build plan: full game.py hardening, orchestrator.py launcher/scheduler with 10-minute health checks, brain.py pulse system, and both web + Luminus Godot control surfaces. I’m now writing the concrete file-by-file implementation spec and test matrix.

Plan


Open

Unified Reliability + Orchestration Plan (SSE + Launcher + Pulses + Web/Godot Control)
Summary
Build one Python orchestration backbone that reliably starts/monitors ollama, brain.py, game.py, and phone_ai.py, while hardening SSE in game.py, adding pulse-debug streaming to brain.py, and exposing touch-first control in both a web dashboard and the Luminus Godot project.

Implementation Sequence (Decision-Complete)
Baseline and prerequisites
Confirm active service commands and ports: ollama 11434, brain.py 8002, game.py 8003, phone_ai.py 8080.
Keep backend_api.py untouched and outside launcher scope.
Add one preflight fix in Luminus so panel integration can compile: update block_panel.gd to stop calling missing ScriptRegistry.get_script(...) and use get_script_record(...).
Harden game.py SSE and choice correctness
File: game.py.
Replace HTTPServer with ThreadingHTTPServer.
Replace direct multi-thread wfile.write() fanout with per-client outbound queue and single-writer stream loop per connection.
Keep 5s heartbeat, add SSE retry: line, and deterministic client cleanup.
Add stale-choice/idempotency guard in /choice: accept only if scene_id == current_scene_id and not already picked; return 409 JSON for stale/duplicate picks.
Remove race-prone delayed handoff (time.sleep(0.2) path) and perform atomic state checks under lock before scene transition.
Frontend JS in same file: add EventSource error/open handlers, reconnect backoff, and duplicate-scene protection using scene.id.
Add pulse-debug system to brain.py
File: brain.py.
Replace HTTPServer with ThreadingHTTPServer and add global lock for graph + pulse mutation.
Add pulse ring buffer (PULSES) with monotonic pulse_id, bounded size (default 5000), and optional JSON persistence file (pulses.json).
Emit pulses on: node creation, path creation, active-node add/remove, current-node switch, incoming message routed, assistant reply stored, construction save/use, cast add.
Add endpoints:
GET /pulses?since_id=&limit=&node=&type= returning ordered pulse list.
GET /pulses/status returning counts/last_id/buffer_size.
GET /pulses/stream SSE feed with heartbeat and event payloads.
Keep all existing endpoints backward-compatible.
Build orchestrator backend (single “combo” script)
New file: orchestrator.py.
Stack: FastAPI + background scheduler loops.
Port: 8001.
Startup order hardcoded: ollama -> brain.py -> game.py -> phone_ai.py.
Port conflict policy: probe health; if healthy reuse; if unhealthy and process matches expected command restart; if unhealthy unknown process mark manual_intervention_required.
Recovery policy: on health failure retry restart up to 2 times with 10s delay; if still failing create high-priority alert and pause dependent tasks.
Add 10-minute full health audit scheduler plus immediate startup health checks.
Add allowlisted execution scope only: scripts/commands under D:/AI_COORDINATION and D:/godot_projects/Luminus_february_project.
Add queue/schedule/task execution layer
New config source: orchestrator_tasks.json.
New runtime state: orchestrator_state.json for persistence across restart.
Task engine features: queue, delayed execution, interval tasks, retries, reschedule, wait states, dependency on service health.
Include built-in recurring task: health_audit_every_10_min.
Expose task lifecycle states: queued, running, waiting, retrying, failed, done, paused.
Add orchestrator API surface
Control endpoints: POST /stop, POST /pause, POST /continue, POST /mode, GET /status.
Service endpoints: POST /services/start_all, POST /services/recover, GET /services/status.
Task endpoints: POST /task/add, GET /task/list, POST /task/skip, DELETE /task/clear, POST /task/reload_today.
Presence/alerts endpoints: GET /presence, POST /presence/ping, GET /alerts, POST /alerts/ack.
Pulse proxy/summary endpoints: GET /brain/pulses, GET /brain/pulses/status (proxying/aggregating from brain.py).
Dashboard endpoint: GET /dashboard (touch-first HTML UI).
Web dashboard (touch-first, no typing required for core flow)
Served by orchestrator.py.
Large controls: Start All, Pause Queue, Continue, Recover Failed, Stop All.
Panels: service health cards, queue timeline, retry/reschedule log, alerts, presence list, pulse counters.
Live updates via SSE from orchestrator (/events/stream).
Godot integration in Luminus (both-now requirement)
New scene: orchestrator_panel.tscn.
New script: orchestrator_panel.gd.
Update main scene: main.tscn to instance orchestrator panel alongside existing block UI.
Panel behavior: poll orchestrator status, display queue/services/alerts, show recent pulse stream summary, provide same control buttons as web dashboard.
Panel sends periodic presence/ping heartbeat to orchestrator.
Multi-app alert routing
Orchestrator broadcasts alerts to:
Web dashboard live stream.
game.py via POST http://localhost:8003/push (phone-visible when game UI connected).
Godot panel via polling/live event feed.
Alert delivery failures are logged and retried on next health cycle.
Public API / Interface / Type Changes
game.py:
/choice response contract adds stale/duplicate error responses (409) with reason fields.
SSE transport internals change to queued delivery; event names stay compatible.
brain.py:
New pulse APIs: /pulses, /pulses/status, /pulses/stream.
orchestrator.py (new):
New orchestration/task/presence/alerts/dashboard API on 8001.
Godot (Luminus):
New orchestrator control panel scene + script.
Minor compatibility fix in block panel script registry call.
Test Cases and Acceptance Scenarios
game.py concurrency regression
Open /stream, then call /status and /push repeatedly; no timeout.
Expected: both return promptly while SSE remains connected.
game.py stale choice race
Submit delayed choice for old scene_id after scene advanced.
Expected: 409 stale response, no extra next_scene call.
game.py click-vs-autopick correctness
Click near timeout boundary.
Expected: exactly one transition; no duplicate auto-pick when click already accepted.
brain.py pulse emission
Send POST /message, POST /node/add, POST /path/add.
Expected: corresponding pulse entries with increasing pulse_id.
brain.py pulse SSE reliability
Keep /pulses/stream connected while hitting /status and /message.
Expected: stream receives events/heartbeats; normal endpoints stay responsive.
Orchestrator startup sequence
Run python orchestrator.py with no services running.
Expected: services start in configured order and pass health checks.
Port-occupied policy
Start with occupied service port.
Expected: healthy process reused; unhealthy expected process restarted; unhealthy unknown process flagged for manual intervention.
Scheduler + retry behavior
Kill one managed service.
Expected: orchestrator detects failure, retries restart with 10s delay, emits alert if retries exhausted.
Task source and persistence
Load orchestrator_tasks.json, execute due tasks, restart orchestrator.
Expected: queue/state restored from orchestrator_state.json with correct statuses.
Cross-surface control parity
Trigger pause/continue/recover from web and Godot panel.
Expected: identical backend state transitions and reflected UI updates on both surfaces.
Assumptions and Defaults
Python is the backend language for all new orchestration work.
Scope includes game.py SSE hardening, brain.py pulses, and both web + Luminus control surfaces in one implementation cycle.
backend_api.py remains unchanged.
Scheduler health audit interval default is 10 minutes and configurable.
Restart retry policy default is 2 attempts with 10s spacing.
Execution allowlist is enforced to approved roots only.
Local-network deployment only; authentication is deferred.
Godot CLI is not assumed in PATH; Godot verification is done via in-editor run for this pass.
remember that you can use any and all programming languages, as long as we start somewhere, it can run and do something in background, layers upon layers of program, we can layer program and make shader over all these polygons 2d, and i do... want that neuron 3d interface with lines, i want shaders, movement, lightning, changes of sizes, physics, and you will create me these animations and show me this today and now! just! do! it! gambaree, and never give up, and one day we will translate all languages into godot, and from godot to any languages too, so i can program like you too




I understand the direction: start immediately with a visible 3D neuron world (lines, shaders, motion, pulses) and layer the system upward from there. I’m mapping existing Luminus/Godot assets first so the next plan is executable today, not conceptual.

Ran Set-Location 'D:/godot_projects/Luminus_february_project'; rg -n "neuron|node graph|shader|material|line|path|lightning|pulse|glow|physics|MeshInstance3D|ImmediateMesh|MultiMesh|GPUParticles|AnimationPlayer|Tween" -g "*.gd" -g "*.tscn" -g "*.md"


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'PHASE_5_DETAILED_DESIGN.md' -TotalCount 260


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'WORLD_DATABASE_DESIGN.md' -TotalCount 260


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content '_extracted_v2_backup/scripts/ui/main_controller.gd'


Ran Set-Location 'D:/AI_COORDINATION/PROMPTS'; Get-Content 'parsed_vision_2026-02-27.md' -TotalCount 260


I found enough local context to plan a real “today” visual slice, but one technical choice will decide whether we can ship it fast: true simulation physics vs shader-driven illusion with optional physics anchors.



Asked 2 questions
For the first same-day neuron demo, which rendering strategy should lead?
Shader-first hybrid (Recommended)
What counts as a successful result today?
Live playable scene (Recommended)
Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-ChildItem -Name


I can deliver the visual fastest either as a dedicated NeuronStage scene or embedded directly into current main.tscn; that choice changes implementation order and risk.



Asked 1 question
Where should the neuron 3D interface ship first today?
Both in same pass
Ran where.exe Godot_v4.7*


Ran Get-Process | Where-Object { $_.ProcessName -like '*godot*' } | Select-Object ProcessName,Id,Path


Plan


Open

Today-Now Neuron 3D Build Plan (Shader-First Hybrid + Background Layers)
Summary
Ship a same-day vertical slice that is immediately visible and interactive in Godot: 3D neuron spheres, animated connection lines, pulse/lightning shaders, size/motion changes, physics-like movement, and live backend-driven updates.
Keep architecture layered so any language can be swapped in later via stable JSON/SSE contracts.

Layered Architecture (Implementation Order)
Layer 1: service reliability and concurrency fixes (game.py, brain.py).
Layer 2: pulse event stream in brain.py (source of visual truth).
Layer 3: supervisor/orchestrator process for background run/restart/check loops.
Layer 4: Godot neuron visual system (dedicated scene + embedded in main.tscn).
Layer 5: control surfaces (web dashboard + Godot overlay) sharing the same orchestrator APIs.
File-Level Implementation Plan
A) Reliability + Event Source (Python)
Update game.py.
Switch HTTPServer to ThreadingHTTPServer.
Add thread-safe SSE client management so /stream cannot block /push, /status, /choice.
Add stale/duplicate choice rejection (scene_id must match current scene).
Keep 5s heartbeat and add robust frontend reconnect/error handlers in embedded JS.
Update brain.py.
Switch to ThreadingHTTPServer.
Add locked pulse buffer with monotonic IDs.
Emit pulse events on node/path/current/history/construction/cast mutations.
Add endpoints: GET /pulses, GET /pulses/status, GET /pulses/stream.
Create orchestrator.py.
FastAPI service on 8001.
Manages ollama, brain.py, game.py, phone_ai.py.
Startup policy: reuse healthy process on occupied port, restart unhealthy expected process, flag unknown unhealthy process.
Recovery policy: retry with 10s delay, then escalate alert.
10-minute health-audit loop.
Task queue/scheduler with allowlisted script execution roots only.
Create orchestrator_tasks.json.
Seed recurring tasks (health_audit_10m, optional daily script list).
Create orchestrator_state.json.
Persist queue/retry/last-status across orchestrator restart.
B) Godot Visual System (Dedicated Scene + Main Integration)
Fix compile blocker in block_panel.gd.
Replace invalid ScriptRegistry.get_script(...) call with existing get_script_record(...) usage pattern.
Create neuron_stage.tscn.
Self-contained 3D neuron stage for immediate run/demo.
Create neuron_graph_controller.gd.
Poll brain.py pulse endpoints.
Build node/edge visual instances from graph data.
Apply heat/pulse state to visuals.
Create neuron_motion_solver.gd.
Shader-first hybrid motion: spring + repulsion + damping (physics-like, stable for today).
Supports mass, drag, anchor stiffness, max velocity.
Create neuron_core.gdshader.
Glow, pulse ring, emissive modulation, scale-reactive intensity.
Create edge_energy.gdshader.
Animated traveling energy and lightning jitter along links.
Create screen_overlay.gdshader.
Global post-like layer over 2D UI/polygons for atmosphere (flicker, bloom tint, scan/noise drift).
Create orchestrator_overlay.gd and orchestrator_overlay.tscn.
Touch-friendly in-game controls: Start/Recover/Pause/Continue/Status.
Shows service health, alerts, and pulse counters.
Update main.tscn.
Instance both NeuronStage and OrchestratorOverlay.
Keep existing BlockPanel present.
Public APIs / Interfaces / Types
brain.py new event contract PulseEvent.
Fields: id, ts, node, type, payload, intensity, src, dst.
Types: node_created, path_created, node_switched, message_in, reply_out, state_change, construction_used, cast_changed.
game.py /choice adds explicit stale/duplicate rejection response.
Return 409 JSON with reason code for invalid scene choice timing.
orchestrator.py core interfaces.
ServiceStatus: name, port, state, pid, last_ok, restart_count, last_error.
TaskSpec: id, name, command, cwd, interval_sec, next_run_at, retries, state.
Endpoints: /status, /services/status, /services/recover, /task/*, /alerts, /events/stream.
Cross-language compatibility rule.
All runtime contracts remain JSON-over-HTTP/SSE so Python, Rust, or other service layers can replace internals without changing Godot client code.
Today Acceptance Criteria
Running the Godot main scene shows moving neuron nodes with animated lines, pulse glow, and size shifts.
Triggering activity in brain.py produces visible pulse reactions in under 300ms median.
game.py SSE no longer blocks /push//status while stream clients are connected.
Orchestrator can keep services up in background and auto-recover failed service with 10s retry delay.
Both control surfaces work: web dashboard and in-Godot overlay.
Test Cases
SSE concurrency test: hold /stream open, spam /push and /status, verify no timeouts.
Choice race test: send stale scene_id choice, verify 409 and no unwanted scene advance.
Pulse stream test: create/add/switch nodes in brain.py, verify ordered PulseEvent.id.
Visual reaction test: each pulse causes node emissive flash + temporary scale increase + path energy burst.
Motion stability test: 50-100 neurons run for 5 minutes without explosive drift.
Recovery test: kill brain.py process, verify orchestrator restarts and reports status/alert transitions.
Main integration test: main.tscn still runs existing UI while neuron stage/overlay are active.
Assumptions and Defaults
Immediate implementation language is Python + GDScript + Godot shaders; protocol stays language-agnostic for future Rust/other layers.
Visual priority is shader-first hybrid (not full rigidbody simulation) to deliver strong same-day output.
Delivery target is a live playable scene today, not just a design prototype.
Scope includes both dedicated neuron scene and direct integration into main.tscn in the same pass.
Authentication/security hardening is deferred; local/offline LAN workflow is the current operating mode.
make me clawdbot 2.0 a better than any other clawdbot, in all languages you know and name it "Devil's Hand", and make me see a demon hand controlling pc, with godot and polygon2d, i think  it shall be the same as the stories projects, where from one story txt, we describe story of an program unfolding, databases, visual presentations, treat godot and browser kinda as power point for me, our excel are json files, we work different


Worked for 10m 58s
I’ll ground this in your current files first and extract existing “story-driven” patterns, so the Devil's Hand plan fits what you already run instead of starting from scratch. I’m scanning for clawdbot, story text pipelines, and Godot/browser presentation patterns now.

Ran Set-Location 'D:/AI_COORDINATION'; rg -n "clawdbot|story|scenario|timeline|presentation|json|Devil|hand|orchestrator|power point|powerpoint" -g "*.md" -g "*.py"


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; rg -n "story|scenario|timeline|polygon2d|presentation|json|hand|demon|controller|overlay|browser" -g "*.gd" -g "*.md" -g "*.tscn"


Ran Set-Location 'D:/AI_COORDINATION'; rg --files -g "*.txt" -g "*.json" | Select-Object -First 200


I found strong existing building blocks for your direction (timeline, JSON-first state, scenario engine, Polygon2D design notes). I’ll now locate concrete story-file entry points so Devil’s Hand can be driven from one .txt as you described.

Ran Set-Location 'D:/AI_COORDINATION'; rg --files | rg -n "story|scenario|session_story|narrative|plot|cast|timeline"


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; rg --files | rg -n "story|scenario|world|timeline|json|cast|narrative"


Ran Set-Location 'D:/AI_COORDINATION'; rg -n "SESSION_STORY|story file|from one story|parse story|story txt|cast" -g "*.md" -g "*.py"


Ran Set-Location 'D:/AI_COORDINATION'; Get-ChildItem -Name 'SESSION_STORY_*.md'


There are no actual SESSION_STORY_*.md files yet, so we should define a new story format as part of this plan. I’m pulling the existing Polygon2D/world-system blueprint sections next so Devil’s Hand can reuse your own design language.

Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'WORLD_DATABASE_DESIGN.md' | Select-Object -Skip 620 -First 160


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'WORLD_SYSTEM_WEEK1_BUILD.md' | Select-Object -Skip 280 -First 260


Ran Set-Location 'D:/godot_projects/Luminus_february_project'; Get-Content 'WORLD_SYSTEM_WEEK1_BUILD.md' -TotalCount 280


Your request maps cleanly to a new product line: Clawdbot 2.0 codename Devil's Hand, driven by one story .txt, projecting to Godot + browser + JSON databases. I need to lock three high-impact decisions before I finalize the full build spec.



Asked 3 questions
How should `Devil's Hand` control the PC in v1?
Semi-auto with approval (Recommended)
How should we interpret “all languages” for the first implementation?
any programming language can be used
What should one story file look like?
simple prompts like i write, messy, too much data we should throw away, most about nothing, we done that already, its easier now, thats how the prompt first check shall go kinda, figuring out what it was about, to add it to basket, characters who do it need to be profesionalist, like "ancient screen writers" the ones whoi writes dreams for god, always around and nerby to help and amuse
I’ll treat that as: free-form messy prompt input, then a strong “basket/router” cleanup step by specialist personas before execution. I need two last product decisions to make the spec implementation-ready.





Asked 2 questions
How should the demon hand appear in Godot v1?
well instead of asking how, make sure we can switch it easily later, choose between several, like themes of entire project, could switch with just some string of words made from me or ai even, the "Devil's Hand" shall have prewritten stories inside, to check out, we will create "simulation" first, where we will create it in 3d world we made so far in godot, with actors and scenes and things and actions interactions time etc, then we create it with Devil's Hand, even physical stuff and things, become my factory
How should one messy prompt become executable flow?
Prompt->Basket->Storyboard (Recommended)
Clear direction: theme-switchable hand renderer, simulation-first in your current Godot world, then graduate to real PC control as factory mode. I’ll lock the phase gate and target location with one final decision.





Asked 2 questions
Should `Devil's Hand` enforce this rollout gate?
right now its a rule, that shall apply, when all previous systems are online and ready, as it is step by step plan, to create the Devil's Hand
Where should we anchor the first `Devil's Hand` build?
on github and on computer i will make folder "D:\devil_s_hand"
I’ll treat D:\devil_s_hand as the canonical workspace and keep Luminus/AI_COORDINATION as upstream dependencies. I’m doing one quick environment check so the plan includes exact bootstrap order and repository layout.

Ran if (Test-Path 'D:/devil_s_hand') { 'EXISTS' } else { 'MISSING' }


Ran if (Test-Path 'D:/devil_s_hand/.git') { 'GIT_REPO' } else { 'NO_GIT' }


Ran Get-NetTCPConnection -LocalPort 8001,8002,8003,8080,11434 -ErrorAction SilentlyContinue | Select-Object LocalPort,State,OwningProcess | Sort-Object LocalPort


Ran Set-Location 'D:/devil_s_hand'; Get-ChildItem -Force | Select-Object Name,Mode,Length


Plan


Open

Devil’s Hand (Clawdbot 2.0) - Simulation-First Polyglot Plan
Summary
Build Devil's Hand in D:\devil_s_hand as a story-driven orchestration system where messy user prompts become executable storyboards, then render in both Godot and browser as presentation surfaces.
Phase gate is strict: simulation mode first, real PC control only after validation of prior systems and scenario tests.
Core runtime is polyglot-ready: any language can participate through a worker adapter contract.

Repository Layout
D:/devil_s_hand/README.md
D:/devil_s_hand/devils_hand_orchestrator.py
D:/devil_s_hand/story_engine/prompt_ingest.py
D:/devil_s_hand/story_engine/basket_router.py
D:/devil_s_hand/story_engine/storyboard_compiler.py
D:/devil_s_hand/story_engine/story_runtime.py
D:/devil_s_hand/contracts/worker_contract.json
D:/devil_s_hand/contracts/storyboard.schema.json
D:/devil_s_hand/contracts/theme.schema.json
D:/devil_s_hand/data/inbox/prompts.ndjson
D:/devil_s_hand/data/storyboards/latest.json
D:/devil_s_hand/data/tables/scenes.json
D:/devil_s_hand/data/tables/actors.json
D:/devil_s_hand/data/tables/tasks.json
D:/devil_s_hand/data/state/runtime_state.json
D:/devil_s_hand/cast/ancient_screenwriters.txt
D:/devil_s_hand/cast/devils_hand_operator.txt
D:/devil_s_hand/stories/packs/devils_hand_intro.story.txt
D:/devil_s_hand/web/dashboard.html
D:/devil_s_hand/web/story_deck.html
D:/devil_s_hand/godot/DevilsHandSim/project.godot
D:/devil_s_hand/godot/DevilsHandSim/scenes/devils_hand_stage.tscn
D:/devil_s_hand/godot/DevilsHandSim/scenes/demon_hand_overlay.tscn
D:/devil_s_hand/godot/DevilsHandSim/scripts/story_player.gd
D:/devil_s_hand/godot/DevilsHandSim/scripts/demon_hand_controller.gd
D:/devil_s_hand/godot/DevilsHandSim/scripts/theme_switcher.gd
D:/devil_s_hand/godot/DevilsHandSim/shaders/hand_glow.gdshader
D:/devil_s_hand/godot/DevilsHandSim/shaders/lightning_trail.gdshader
Runtime Flow
POST /prompt/ingest accepts messy raw text exactly as written.
basket_router removes noise and splits into intents, threads, and action candidates.
ancient_screenwriters cast step turns intent bundle into scene beats and timing.
storyboard_compiler emits latest.json storyboard plus scene/task tables.
Simulation runtime pushes events to Godot and browser deck simultaneously.
Demon hand visual performs pointer path preview and action cue in simulation.
Real control path remains blocked until phase gate passes.
After gate pass, semi-auto mode requires explicit approve per action batch.
Public APIs and Contracts
Orchestrator API
POST /prompt/ingest
GET /basket/latest
POST /storyboard/compile
GET /storyboard/latest
POST /simulation/start
POST /simulation/stop
POST /theme/switch
GET /theme/current
GET /events/stream (SSE)
POST /control/propose
POST /control/approve
POST /control/reject
GET /control/queue
GET /health
Worker Adapter Contract
Worker registers capability list: parse, plan, render, automate, analyze.
Worker transport is JSON over HTTP.
Required fields: worker_id, language, capabilities, heartbeat_ts, status.
Any language is accepted if it implements this contract.
Storyboard Type
Root fields: story_id, title, theme_key, beats, actors, tasks, timeline.
beats[]: beat_id, intent, visual, duration_ms, target_surface.
tasks[]: task_id, action, requires_approval, phase.
timeline[]: ordered frame events for Godot and browser playback.
Godot Visual Spec (Devil’s Hand)
Default renderer is Polygon2D hand overlay with shader glow and lightning trails.
Stage also includes 3D simulation world with actors/scenes/actions driven by storyboard.
Hand mode is theme-switchable by phrase input mapped to theme_key.
Theme switch is runtime hot-reload, no scene restart.
Theme profiles include visual set, motion profile, sound cues, and palette.
Godot receives live storyboard events and queue state over SSE polling bridge.
Browser Spec (PowerPoint Mode)
story_deck.html renders storyboard beats as slide-like sequence.
dashboard.html shows queue, approvals, phase gate, and service health.
Browser and Godot always share the same latest.json and event stream.
JSON-First Data Model (“Excel as JSON”)
actors.json is character table.
scenes.json is visual/interaction table.
tasks.json is execution queue table.
runtime_state.json is current cursor, approvals, retries, and gating flags.
No spreadsheet dependency; JSON files are the source of truth.
Phase Gate Plan
Phase 1: Story parsing + basket + storyboard generation from messy prompts.
Phase 2: Godot simulation world with Devil’s Hand visuals and actor interactions.
Phase 3: Browser presentation/deck synced to same storyboard.
Phase 4: Semi-auto approval queue with simulated actions only.
Phase 5: Controlled real PC automation unlock after acceptance tests pass.
Acceptance Tests
Messy prompt ingestion produces valid storyboard JSON without manual cleanup.
Theme phrase switch updates hand look/motion in under 1 second.
Godot and browser show same beat index and actor state.
Simulation mode blocks real OS actions regardless of queue content.
Approval is mandatory in semi-auto mode for every executable action batch.
Recovery test: orchestrator restart preserves runtime_state.json.
Polyglot test: one non-Python worker registers and executes supported capability.
Assumptions and Defaults
Canonical workspace is D:\devil_s_hand and will be versioned to GitHub.
Existing services in D:\AI_COORDINATION (brain.py, game.py, Ollama) can be reused as optional upstream providers.
Initial implementation uses Python + GDScript + web JS, with adapters for additional languages.
Godot CLI may be unavailable in PATH; validation can run via editor until CLI path is configured.
Safety default is strict: simulation-first, real control locked behind explicit phase completion.
and we will craft skills visually with stories to tell and experience, that shall be skills for clawdbot 2.0 the Devil's hand Devil's Hand, we can even posses beings to controll them, and execute actions themselves, both ai and user shall be able to control that main character of any story, they compete, they complete, to finish it and make it perfect, with new details, as devil's within the detail.

I’m extending the architecture to include story-driven skill crafting, possession control, and AI-vs-user co-control loops. I’ll quickly check if any existing docs already define control arbitration so we don’t duplicate a model.

Ran Set-Location 'D:/AI_COORDINATION'; rg -n "possess|possession|co-control|dual control|ai vs u




Asked 3 questions
How should AI and user co-control a possessed main character during a story?
token turns plus, if i didnt control for a while i can control for longer now
What should a crafted story-skill become as a reusable artifact?
json sounds alright, hybrid too, maybe zip too?
How should AI-vs-user competition work while polishing stories?
it shall be 3d game, about 5d realm, the 5d chess, where we play with time, and as we time travel we discuss obesrve decide...

Worked for 1m 56s
I’ve locked one key rule: token turns with dynamic catch-up time when you’ve been idle. I need to pin down packaging and 5D-time gameplay mechanics so the spec is implementable without guesses.



Asked 2 questions
Choose the final skill artifact format for Devil's Hand v1.
Hybrid ZIP (Recommended)
How should the 5D time-play loop work per story beat?
all stories shall always play, from first to last we made so far, its a cycle and loop, maybe a process to turn on entire program too? to repair it, to maybe tinker with some stories, so it wont break?




Asked 1 question
Pick the runtime policy for “all stories always play in cycle.”
its complicated, as we could run later several stories at once, to communicate together from many places and times and even with ourselves from any time, any form, any place




Asked 1 question
For v1, should multi-story simultaneous runtime be built now or staged?
shall be there as its even core part of backend for anything to be turned on from main py file, that i run to turn on the ecosystem of Devil's Hand, its checking, requests, queues, task, it will always do something, like a train that rides in loop, then turns some lever and moves somewhere, but always can go back there, maybe even teleport and timetravel, saves, database, load, archive, chunk, cache, visible, invisible, online, offline, last seen and much more





Plan


Open

Devil’s Hand 2.0 - Story Skill Forge + Possession Ecosystem (V1)
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



