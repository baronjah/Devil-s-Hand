import os
import time
import json
import threading
from flask import Flask, Response, stream_with_context, request
from flask_cors import CORS

from story_engine.version_tracker import VersionTracker
from story_engine.paranoia_agent import ParanoiaAgent
from prompt_ingest import PromptIngest
from basket_router import BasketRouter
from save_system import SaveSystem
from mode_manager import ModeManager
from skill_forge import SkillForge
from dimension_explorer import DimensionExplorer
from schemas.swiss_knife_schema import SwissKnifeSchema

app = Flask(__name__)
CORS(app)

# ─── Ecosystem State ──────────────────────────────────────────────────────────
class Ecosystem:
    def __init__(self):
        self.base_dir = "D:/devil_s_hand"
        self.vt = VersionTracker(self.base_dir, os.path.join(self.base_dir, "history"))
        self.pa = ParanoiaAgent([self.base_dir, "D:/godot_projects/fab"])
        self.ingestor = PromptIngest(self.base_dir)
        self.router = BasketRouter()
        self.save_system = SaveSystem(self.base_dir)
        self.mode_manager = ModeManager(initial_mode="sandbox")
        self.skill_forge = SkillForge(self)
        self.explorer = DimensionExplorer(self)
        
        # Initialize structured state from Swiss Knife Schema
        self.state = self.save_system.create_empty_state("JSH")
        
        self.clients = []
        self.lock = threading.Lock()
        self.running = True
        self.status = "initializing"
        
        # Mode specific states
        self.turn_committed = False
        self.force_beat = False
        self.resources = {"energy": 100}
        
        # Possession State
        self.controller = "j_s_hand" # "j_s_hand" (User) or "devil_s_hand" (AI)
        self.last_controller_switch = time.time()
        
        self.story_id = "demon-hand-init"
        self.beat_count = 0

E = Ecosystem()

# ─── SSE Helper ───────────────────────────────────────────────────────────────
def push_event(event_type, data):
    msg = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    with E.lock:
        dead = []
        for client in E.clients:
            try:
                client.put(msg)
            except:
                dead.append(client)
        for d in dead:
            E.clients.remove(d)

class ClientQueue:
    def __init__(self):
        self.queue = []
        self.event = threading.Event()
    def put(self, msg):
        self.queue.append(msg)
        self.event.set()
    def get(self):
        self.event.wait()
        msg = self.queue.pop(0)
        if not self.queue: self.event.clear()
        return msg

# ─── The Train Loop ──────────────────────────────────────────────────────────
def ecosystem_loop():
    print("Ecosystem: 🚂 Train loop started.")
    E.status = "running"
    
    # Auto-save timer
    last_save = time.time()
    
    while E.running:
        # Tick Rate determined by Mode
        time.sleep(E.mode_manager.tick_rate)
        
        # 1. Paranoia Check
        alerts = E.pa.check_integrity()
        for alert in alerts:
            push_event("paranoia_alert", alert)
            # If critical change, auto-track
            if "path" in alert:
                E.vt.track_file(alert["path"])
        
        # 2. Heartbeat
        push_event("pulse", {"node_id": "core", "t": time.time(), "mode": E.mode_manager.current_mode})
        
        # 3. Apply Mode Rules (might halt further execution this tick)
        if not E.mode_manager.process_loop_rules(E):
            continue
            
        # 4. Simulate Story Progression (if auto-advance is on or forced)
        if E.mode_manager.auto_advance_beats or E.force_beat:
            E.beat_count += 1
            push_event("story_beat", {
                "story_id": E.story_id,
                "beat": {
                    "beat_id": f"beat-{E.beat_count}",
                    "scene": f"Ecosystem loop cycle {E.beat_count}: Running in {E.mode_manager.current_mode.upper()} mode.",
                    "actors": ["DemonHand"],
                    "timeline_index": E.beat_count,
                    "is_canon": True
                }
            })
            E.force_beat = False
            
        # 5. Auto-Save every 60 seconds
        if time.time() - last_save > 60:
            state_dict = {
                "beat_count": E.beat_count,
                "controller": E.controller,
                "mode": E.mode_manager.current_mode,
                "resources": E.resources
            }
            E.save_system.save_state(state_dict, save_name="train_auto")
            last_save = time.time()

# ─── API Endpoints ────────────────────────────────────────────────────────────
@app.route('/events/stream')
def stream():
    q = ClientQueue()
    with E.lock:
        E.clients.append(q)
    
    def generator():
        try:
            while True:
                yield q.get()
        except GeneratorExit:
            with E.lock:
                if q in E.clients: E.clients.remove(q)
                
    return Response(stream_with_context(generator()), mimetype="text/event-stream")

@app.route('/status')
def get_status():
    return json.dumps({
        "status": E.status,
        "controller": E.controller,
        "mode": E.mode_manager.current_mode,
        "beat_count": E.beat_count,
        "files_monitored": len(E.pa.signatures),
        "total_versions": sum(len(v["versions"]) for v in E.vt.version_index.values())
    })

@app.route('/mode/set', methods=['POST'])
def set_mode():
    data = request.json
    new_mode = data.get("mode")
    if E.mode_manager.set_mode(new_mode):
        push_event("mode_changed", {"mode": new_mode})
        return json.dumps({"ok": True, "mode": new_mode})
    return json.dumps({"ok": False, "error": "Invalid mode"}), 400

@app.route('/turn/commit', methods=['POST'])
def commit_turn():
    E.turn_committed = True
    E.force_beat = True # Force a beat generation
    return json.dumps({"ok": True})

@app.route('/state/save', methods=['POST'])
def save_state():
    data = request.json
    name = data.get("name", "manual_save")
    state_dict = {
        "beat_count": E.beat_count,
        "controller": E.controller,
        "mode": E.mode_manager.current_mode,
        "resources": E.resources
    }
    filepath = E.save_system.save_state(state_dict, save_name=name, tag="manual")
    if filepath:
        return json.dumps({"ok": True, "file": filepath})
    return json.dumps({"ok": False}), 500

@app.route('/state/load', methods=['POST'])
def load_state():
    data = request.json
    name = data.get("name", "manual_save")
    state = E.save_system.load_latest(save_name=name)
    if state:
        E.beat_count = state.get("beat_count", 0)
        E.controller = state.get("controller", "j_s_hand")
        E.mode_manager.set_mode(state.get("mode", "sandbox"))
        E.resources = state.get("resources", {"energy": 100})
        push_event("state_loaded", state)
        return json.dumps({"ok": True, "state": state})
    return json.dumps({"ok": False, "error": "Save not found"}), 404

@app.route('/prompt/ingest', methods=['POST'])
def ingest_prompt():
    data = request.json
    raw_text = data.get("prompt", "")
    source = data.get("source", "web_interface")
    
    # 1. Physical Ingest
    log = E.ingestor.ingest(raw_text, source)
    
    # 2. Basket Routing (AI extraction)
    # We do this in a thread to not block the UI if Ollama is slow
    def process():
        structured = E.router.route_prompt(raw_text)
        push_event("basket_routed", {
            "prompt_id": log["prompt_id"],
            "structured": structured
        })
        
        # Log to timeline
        event = SwissKnifeSchema.create_timeline_event("JSH", "INGEST_PROMPT", log["prompt_id"])
        event["after"] = structured
        E.state["timeline"].append(event)
        
        print(f"Ecosystem: Intent routed -> {structured.get('intent')}")

    threading.Thread(target=process, daemon=True).start()
    
    return json.dumps({"ok": True, "prompt_id": log["prompt_id"]})

@app.route('/branch/create', methods=['POST'])
def create_branch():
    data = request.json
    label = data.get("label", "New Branch")
    b_type = data.get("type", "LOGIC_BLOCK")
    
    node = SwissKnifeSchema.create_branch_node(label, b_type)
    E.state["branches"][node["branch_id"]] = node
    
    push_event("branch_created", node)
    return json.dumps({"ok": True, "branch": node})

@app.route('/skill/miracle', methods=['POST'])
def execute_miracle():
    data = request.json
    target = data.get("target_id")
    raw = data.get("raw_input", "")
    
    result = E.skill_forge.miracle_it_away(target, raw)
    push_event("skill_executed", result)
    return json.dumps({"ok": True, "result": result})

@app.route('/skill/prevent', methods=['POST'])
def execute_prevention():
    data = request.json
    target = data.get("target_path")
    
    result = E.skill_forge.demonic_prevention(target)
    push_event("skill_executed", result)
    return json.dumps({"ok": True, "result": result})

@app.route('/dimension/roam', methods=['POST'])
def roam_dimension():
    data = request.json
    path = data.get("path", "D:/")
    if E.explorer.roam(path):
        push_event("dimension_roamed", {"path": path})
        return json.dumps({"ok": True, "path": path})
    return json.dumps({"ok": False, "error": "Path not found"}), 404

@app.route('/dimension/expect', methods=['POST'])
def expect_dimension():
    data = request.json
    text = data.get("expectation", "something useful")
    exp = E.explorer.declare_expectation(text)
    E.explorer.check_reality()
    push_event("expectation_declared", exp)
    return json.dumps({"ok": True, "expectation": exp})

@app.route('/dimension/status', methods=['GET'])
def dimension_status():
    E.explorer.check_reality()
    return json.dumps({
        "current_path": E.explorer.current_path,
        "reality": E.explorer.reality,
        "expectations": E.explorer.expectations
    })

@app.route('/dimension/reconstruct', methods=['POST'])
def reconstruct_dimension():
    data = request.json
    exp_id = data.get("id")
    if E.explorer.reconstruct(exp_id):
        push_event("dimension_reconstructed", {"id": exp_id})
        return json.dumps({"ok": True})
    return json.dumps({"ok": False}), 500

@app.route('/judgement/execute', methods=['POST'])
def execute_judgement():
    data = request.json
    decision = data.get("decision")
    file_path = data.get("file_path")
    
    # Record the decision in version tracker
    E.vt.set_author("Judge")
    E.vt._record_version(file_path, "", f"Judgement: {decision}")
    
    push_event("judgement_result", {"decision": decision, "file_path": file_path})
    return json.dumps({"ok": True})

@app.route('/history/<path:file_path>')
def get_file_history(file_path):
    # Fix for path encoding
    file_path = file_path.replace("\\", "/")
    return json.dumps(E.vt.get_history(file_path))

if __name__ == "__main__":
    # Start loop in background
    threading.Thread(target=ecosystem_loop, daemon=True).start()
    
    # Start Flask
    print("Ecosystem: 🌐 API running on port 8010")
    app.run(host='0.0.0.0', port=8010, debug=False, threaded=True)
