#!/usr/bin/env python3
"""Devils Hand 2.0 main runtime."""

import io
import json
import os
import re
import sys
import time
import uuid
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

from story_engine.prompt_ingest import ingest_prompt
from story_engine.basket_router import route_prompt
from story_engine.storyboard_compiler import compile_storyboard
from story_engine.story_runtime import (
    create_story_runtime,
    tick_story_runtime,
    rewind_story,
    branch_story,
    merge_story,
    commit_canon,
)
from control.possession_engine import PossessionEngine
from skills.skill_forge import forge_skill_from_storyboard
from skills.skill_packer import package_skill_zip, compute_manifest_checksum

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
INBOX_FILE = os.path.join(DATA_DIR, "inbox", "prompts.ndjson")
BASKET_FILE = os.path.join(DATA_DIR, "state", "basket_output.json")
STORYBOARD_DIR = os.path.join(DATA_DIR, "storyboards")
STORYBOARD_INDEX_FILE = os.path.join(STORYBOARD_DIR, "index.json")
STATE_FILE = os.path.join(DATA_DIR, "state", "runtime_state.json")
SKILLS_DIR = os.path.join(ROOT, "skills", "packages")
WEB_DIR = os.path.join(ROOT, "web")

PORT = 8010


def now_ms() -> int:
    return int(time.time() * 1000)


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def read_json(path: str, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def write_json(path: str, data) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def append_ndjson(path: str, row: dict) -> None:
    ensure_dir(os.path.dirname(path))
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


class EventBus:
    def __init__(self):
        self.lock = threading.Lock()
        self.subs = []

    def subscribe(self, handler, stream_type="events", story_id=""):
        with self.lock:
            self.subs.append({"handler": handler, "stream_type": stream_type, "story_id": story_id})

    def unsubscribe(self, handler):
        with self.lock:
            self.subs = [s for s in self.subs if s["handler"] is not handler]

    def publish(self, event: str, payload: dict, story_id: str = ""):
        msg = {
            "event": event,
            "story_id": story_id,
            "ts": now_ms(),
            "payload": payload,
        }
        packet = f"event: {event}\ndata: {json.dumps(msg, ensure_ascii=False)}\n\n".encode("utf-8")

        dead = []
        with self.lock:
            for sub in self.subs:
                wants_events = sub["stream_type"] == "events"
                wants_timeline = sub["stream_type"] == "timeline" and sub["story_id"] == story_id
                if not (wants_events or wants_timeline):
                    continue
                h = sub["handler"]
                try:
                    h.wfile.write(packet)
                    h.wfile.flush()
                except Exception:
                    dead.append(h)

        if dead:
            with self.lock:
                self.subs = [s for s in self.subs if s["handler"] not in dead]


class AppState:
    def __init__(self):
        self.lock = threading.Lock()
        self.running = False
        self.paused = False
        self.simulation_mode = True
        self.phase_gate_passed = False
        self.theme = "default_infernal"

        self.last_basket = read_json(BASKET_FILE, {})
        self.storyboards = {}
        self.story_instances = {}
        self.control_queue = []
        self.skills = {}
        self.services = {
            "brain": {"port": 8002, "state": "unknown"},
            "game": {"port": 8003, "state": "unknown"},
            "phone_ai": {"port": 8080, "state": "unknown"},
            "ollama": {"port": 11434, "state": "unknown"},
        }

        self.possession = PossessionEngine(base_turn_ms=12000, bonus_multiplier=1.5, max_bonus_factor=2.0)
        self.bus = EventBus()
        self._load_storyboards()

    def _load_storyboards(self):
        index = read_json(STORYBOARD_INDEX_FILE, {"storyboards": []})
        for sid in index.get("storyboards", []):
            p = os.path.join(STORYBOARD_DIR, sid + ".json")
            sb = read_json(p, None)
            if sb:
                self.storyboards[sid] = sb
                self.story_instances[sid] = create_story_runtime(sb)

    def persist(self):
        write_json(STATE_FILE, {
            "running": self.running,
            "paused": self.paused,
            "simulation_mode": self.simulation_mode,
            "phase_gate_passed": self.phase_gate_passed,
            "theme": self.theme,
            "story_ids": sorted(self.storyboards.keys()),
            "control_queue": self.control_queue[-200:],
            "skills": sorted(self.skills.keys()),
            "possession": self.possession.get_state(),
            "updated_ms": now_ms(),
        })


STATE = AppState()


def save_storyboard(sb: dict):
    sid = sb["story_id"]
    ensure_dir(STORYBOARD_DIR)
    write_json(os.path.join(STORYBOARD_DIR, sid + ".json"), sb)

    index = read_json(STORYBOARD_INDEX_FILE, {"storyboards": []})
    rows = set(index.get("storyboards", []))
    rows.add(sid)
    write_json(STORYBOARD_INDEX_FILE, {"storyboards": sorted(rows)})


def score_bundle(bundle: dict) -> dict:
    text = json.dumps(bundle, ensure_ascii=False)
    coherence = min(1.0, 0.4 + (len(text) / 1200.0))
    detail = min(1.0, (text.count("detail") + len(text) / 200.0) / 10.0)
    continuity = 0.8 if "timeline_index" in text else 0.55
    safety = 1.0 if bundle.get("simulation", True) else 0.5
    total = (coherence * 0.3) + (detail * 0.3) + (continuity * 0.2) + (safety * 0.2)
    return {
        "coherence": round(coherence, 3),
        "detail_richness": round(detail, 3),
        "continuity": round(continuity, 3),
        "safety": round(safety, 3),
        "total": round(total, 3),
    }


def heartbeat_loop():
    while True:
        time.sleep(1)
        with STATE.lock:
            if not STATE.running or STATE.paused:
                continue
            for sid, runtime in STATE.story_instances.items():
                tick_story_runtime(runtime)
                snap = runtime.get("current_snapshot")
                if snap:
                    STATE.bus.publish("story_tick", {"snapshot": snap, "state": runtime.get("state")}, sid)
            STATE.possession.tick()
            STATE.persist()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def set_headers(self, code=200, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.end_headers()

    def send_json(self, data, code=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.set_headers(code=code)
        self.wfile.write(body)

    def read_json(self):
        n = int(self.headers.get("Content-Length", "0") or 0)
        if n <= 0:
            return {}
        try:
            return json.loads(self.rfile.read(n))
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.set_headers(200)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/events/stream":
            return self.stream("events", "")

        m = re.match(r"^/timeline/([^/]+)/stream$", path)
        if m:
            return self.stream("timeline", m.group(1))

        if path == "/ecosystem/status":
            with STATE.lock:
                return self.send_json({
                    "running": STATE.running,
                    "paused": STATE.paused,
                    "simulation_mode": STATE.simulation_mode,
                    "phase_gate_passed": STATE.phase_gate_passed,
                    "theme": STATE.theme,
                    "stories": {k: v.get("state", "unknown") for k, v in STATE.story_instances.items()},
                    "control_queue": len(STATE.control_queue),
                    "possession": STATE.possession.get_state(),
                    "services": STATE.services,
                    "now_ms": now_ms(),
                })

        if path == "/basket/latest":
            with STATE.lock:
                return self.send_json(STATE.last_basket)

        if path == "/storyboards":
            with STATE.lock:
                rows = []
                for sid, sb in STATE.storyboards.items():
                    rows.append({"story_id": sid, "title": sb.get("title", sid), "beats": len(sb.get("beats", [])), "updated_ms": sb.get("updated_ms", 0)})
                rows.sort(key=lambda x: x["updated_ms"], reverse=True)
                return self.send_json({"storyboards": rows})

        if path == "/possession/state":
            return self.send_json(STATE.possession.get_state())

        if path == "/control/queue":
            with STATE.lock:
                return self.send_json({"queue": STATE.control_queue})

        if path == "/skills/list":
            with STATE.lock:
                rows = []
                for sid, item in STATE.skills.items():
                    rows.append({"skill_id": sid, "name": item.get("name", sid), "version": item.get("version", "0.0.1"), "updated_ms": item.get("updated_ms", 0)})
                rows.sort(key=lambda x: x["updated_ms"], reverse=True)
                return self.send_json({"skills": rows})

        m = re.match(r"^/skills/([^/]+)/manifest$", path)
        if m:
            sid = m.group(1)
            with STATE.lock:
                item = STATE.skills.get(sid)
                if not item:
                    return self.send_json({"error": "skill not found"}, 404)
                return self.send_json(item)

        if path == "/theme/current":
            return self.send_json({"theme": STATE.theme})

        if path == "/health":
            return self.send_json({"ok": True, "ts": now_ms(), "service": "Devils Hand 2.0"})

        if path == "/dashboard":
            return self.serve_text(os.path.join(WEB_DIR, "dashboard.html"), "text/html; charset=utf-8")

        if path == "/deck":
            return self.serve_text(os.path.join(WEB_DIR, "story_deck.html"), "text/html; charset=utf-8")

        if path == "/":
            return self.send_json({
                "name": "Devils Hand 2.0",
                "dashboard": "/dashboard",
                "deck": "/deck",
                "status": "/ecosystem/status",
            })

        return self.send_json({"error": "not found", "path": path}, 404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        body = self.read_json()

        if path == "/ecosystem/start":
            with STATE.lock:
                STATE.running = True
                STATE.paused = False
                STATE.persist()
            STATE.bus.publish("ecosystem_start", {"running": True})
            return self.send_json({"ok": True})

        if path == "/ecosystem/pause":
            with STATE.lock:
                STATE.paused = True
                STATE.persist()
            STATE.bus.publish("ecosystem_pause", {"paused": True})
            return self.send_json({"ok": True})

        if path == "/ecosystem/resume":
            with STATE.lock:
                STATE.running = True
                STATE.paused = False
                STATE.persist()
            STATE.bus.publish("ecosystem_resume", {"paused": False})
            return self.send_json({"ok": True})

        if path == "/ecosystem/stop":
            with STATE.lock:
                STATE.running = False
                STATE.paused = False
                STATE.persist()
            STATE.bus.publish("ecosystem_stop", {"running": False})
            return self.send_json({"ok": True})

        if path == "/prompt/ingest":
            raw = str(body.get("text", "")).strip()
            if not raw:
                return self.send_json({"error": "missing text"}, 400)
            prompt = ingest_prompt(raw_text=raw, source=str(body.get("source", "user")))
            basket = route_prompt(prompt)
            with STATE.lock:
                STATE.last_basket = basket
                append_ndjson(INBOX_FILE, prompt)
                write_json(BASKET_FILE, basket)
                STATE.persist()
            STATE.bus.publish("prompt_ingested", {"prompt_id": prompt["prompt_id"]})
            STATE.bus.publish("basket_updated", basket)
            return self.send_json({"prompt": prompt, "basket": basket})

        if path == "/storyboard/compile":
            with STATE.lock:
                basket = body.get("basket") or STATE.last_basket
            if not basket:
                return self.send_json({"error": "no basket data"}, 400)
            sb = compile_storyboard(basket, title=str(body.get("title", "")))
            sid = sb["story_id"]
            runtime = create_story_runtime(sb)
            with STATE.lock:
                STATE.storyboards[sid] = sb
                STATE.story_instances[sid] = runtime
                save_storyboard(sb)
                STATE.persist()
            STATE.bus.publish("storyboard_compiled", {"story_id": sid, "beats": len(sb.get("beats", []))}, sid)
            return self.send_json({"storyboard": sb})

        m = re.match(r"^/story/([^/]+)/start$", path)
        if m:
            sid = m.group(1)
            with STATE.lock:
                rt = STATE.story_instances.get(sid)
                if not rt:
                    return self.send_json({"error": "story not found"}, 404)
                rt["state"] = "active"
                rt["last_started_ms"] = now_ms()
                STATE.persist()
            STATE.bus.publish("story_started", {"story_id": sid}, sid)
            return self.send_json({"ok": True, "story_id": sid})

        m = re.match(r"^/story/([^/]+)/rewind$", path)
        if m:
            sid = m.group(1)
            idx = int(body.get("timeline_index", 0))
            with STATE.lock:
                rt = STATE.story_instances.get(sid)
                if not rt:
                    return self.send_json({"error": "story not found"}, 404)
                rewind_story(rt, idx)
                STATE.persist()
            STATE.bus.publish("story_rewind", {"story_id": sid, "timeline_index": idx}, sid)
            return self.send_json({"ok": True, "story_id": sid, "timeline_index": idx})

        m = re.match(r"^/story/([^/]+)/branch$", path)
        if m:
            sid = m.group(1)
            branch = str(body.get("branch", "branch_" + uuid.uuid4().hex[:6]))
            with STATE.lock:
                rt = STATE.story_instances.get(sid)
                if not rt:
                    return self.send_json({"error": "story not found"}, 404)
                branch_story(rt, branch)
                STATE.persist()
            STATE.bus.publish("story_branch", {"story_id": sid, "branch": branch}, sid)
            return self.send_json({"ok": True, "story_id": sid, "branch": branch})

        m = re.match(r"^/story/([^/]+)/merge$", path)
        if m:
            sid = m.group(1)
            a = str(body.get("branch_a", "main"))
            b = str(body.get("branch_b", "candidate"))
            with STATE.lock:
                rt = STATE.story_instances.get(sid)
                if not rt:
                    return self.send_json({"error": "story not found"}, 404)
                merged = merge_story(rt, a, b)
                merged["quality_score"] = score_bundle(merged)
                rt["last_merge"] = merged
                STATE.persist()
            STATE.bus.publish("story_merge", {"story_id": sid, "quality_score": merged["quality_score"]}, sid)
            return self.send_json({"ok": True, "story_id": sid, "merge": merged})

        m = re.match(r"^/story/([^/]+)/commit_canon$", path)
        if m:
            sid = m.group(1)
            with STATE.lock:
                rt = STATE.story_instances.get(sid)
                if not rt:
                    return self.send_json({"error": "story not found"}, 404)
                result = commit_canon(rt)
                STATE.persist()
            STATE.bus.publish("story_commit_canon", {"story_id": sid, "canon": result}, sid)
            return self.send_json({"ok": True, "story_id": sid, "canon": result})

        if path == "/possession/request":
            result = STATE.possession.request_control(
                side=str(body.get("side", "user")),
                character_id=str(body.get("character_id", "main_character")),
                emergency_override=bool(body.get("emergency_override", False)),
            )
            STATE.bus.publish("possession_request", result)
            return self.send_json(result)

        if path == "/possession/release":
            result = STATE.possession.release_control(side=str(body.get("side", "user")))
            STATE.bus.publish("possession_release", result)
            return self.send_json(result)

        if path == "/control/propose":
            action = {
                "action_id": "act_" + uuid.uuid4().hex[:10],
                "story_id": str(body.get("story_id", "")),
                "source": str(body.get("source", "ai")),
                "controller": str(body.get("controller", "ai")),
                "action": body.get("action", {}),
                "requires_approval": bool(body.get("requires_approval", True)),
                "state": "queued",
                "simulation": True,
                "created_ms": now_ms(),
            }
            with STATE.lock:
                STATE.control_queue.append(action)
                STATE.persist()
            STATE.bus.publish("control_proposed", action, action["story_id"])
            return self.send_json({"ok": True, "action": action})

        if path == "/control/approve":
            aid = str(body.get("action_id", ""))
            with STATE.lock:
                action = next((a for a in STATE.control_queue if a["action_id"] == aid), None)
                if not action:
                    return self.send_json({"error": "action not found"}, 404)
                if not STATE.phase_gate_passed or STATE.simulation_mode:
                    action["state"] = "executed_simulation"
                    action["execution_note"] = "simulation gate active"
                else:
                    action["state"] = "executed_real_stub"
                action["executed_ms"] = now_ms()
                STATE.persist()
            STATE.bus.publish("control_approved", action, action.get("story_id", ""))
            return self.send_json({"ok": True, "action": action})

        if path == "/control/reject":
            aid = str(body.get("action_id", ""))
            reason = str(body.get("reason", "rejected by operator"))
            with STATE.lock:
                action = next((a for a in STATE.control_queue if a["action_id"] == aid), None)
                if not action:
                    return self.send_json({"error": "action not found"}, 404)
                action["state"] = "rejected"
                action["reason"] = reason
                action["rejected_ms"] = now_ms()
                STATE.persist()
            STATE.bus.publish("control_rejected", action, action.get("story_id", ""))
            return self.send_json({"ok": True, "action": action})

        if path == "/skills/forge":
            sid = str(body.get("story_id", ""))
            with STATE.lock:
                sb = STATE.storyboards.get(sid)
            if not sb:
                return self.send_json({"error": "story_id not found"}, 404)
            manifest = forge_skill_from_storyboard(sb, requested_name=str(body.get("name", "")))
            manifest["checksum"] = compute_manifest_checksum(manifest)
            with STATE.lock:
                STATE.skills[manifest["skill_id"]] = manifest
                STATE.persist()
            STATE.bus.publish("skill_forged", manifest)
            return self.send_json({"ok": True, "manifest": manifest})

        if path == "/skills/package":
            skill_id = str(body.get("skill_id", ""))
            with STATE.lock:
                manifest = STATE.skills.get(skill_id)
            if not manifest:
                return self.send_json({"error": "skill not found"}, 404)
            pkg = package_skill_zip(manifest, SKILLS_DIR)
            with STATE.lock:
                manifest["package_path"] = pkg
                manifest["updated_ms"] = now_ms()
                STATE.skills[skill_id] = manifest
                STATE.persist()
            STATE.bus.publish("skill_packaged", {"skill_id": skill_id, "package_path": pkg})
            return self.send_json({"ok": True, "package_path": pkg})

        if path == "/skills/load":
            skill_id = str(body.get("skill_id", ""))
            with STATE.lock:
                manifest = STATE.skills.get(skill_id)
            if not manifest:
                return self.send_json({"error": "skill not found"}, 404)
            STATE.bus.publish("skill_loaded", {"skill_id": skill_id, "name": manifest.get("name", skill_id)})
            return self.send_json({"ok": True, "skill": manifest})

        if path == "/theme/switch":
            phrase = str(body.get("phrase", "")).lower()
            new_theme = "default_infernal"
            if "ice" in phrase or "frost" in phrase:
                new_theme = "frost_wire"
            elif "void" in phrase or "shadow" in phrase:
                new_theme = "void_orbit"
            elif "gold" in phrase or "sun" in phrase:
                new_theme = "solar_circuit"

            with STATE.lock:
                STATE.theme = new_theme
                STATE.persist()
            STATE.bus.publish("theme_switched", {"theme": new_theme, "phrase": phrase})
            return self.send_json({"ok": True, "theme": new_theme})

        return self.send_json({"error": "not found", "path": path}, 404)

    def serve_text(self, path: str, ctype: str):
        if not os.path.exists(path):
            return self.send_json({"error": "missing file", "path": path}, 404)
        with open(path, "rb") as f:
            payload = f.read()
        self.set_headers(200, ctype)
        self.wfile.write(payload)

    def stream(self, stream_type: str, story_id: str):
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        STATE.bus.subscribe(self, stream_type=stream_type, story_id=story_id)
        try:
            while True:
                hb = f": heartbeat {int(time.time())}\n\n".encode("utf-8")
                self.wfile.write(hb)
                self.wfile.flush()
                time.sleep(5)
        except Exception:
            pass
        finally:
            STATE.bus.unsubscribe(self)


def main():
    ensure_dir(os.path.join(DATA_DIR, "inbox"))
    ensure_dir(os.path.join(DATA_DIR, "state"))
    ensure_dir(STORYBOARD_DIR)
    ensure_dir(SKILLS_DIR)

    threading.Thread(target=heartbeat_loop, daemon=True).start()

    print(f"Devils Hand 2.0 listening on http://127.0.0.1:{PORT}")
    print("Dashboard: /dashboard")
    print("Story deck: /deck")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
