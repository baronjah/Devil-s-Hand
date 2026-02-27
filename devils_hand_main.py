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
        
        self.clients = []
        self.lock = threading.Lock()
        self.running = True
        self.status = "initializing"
        
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
    
    while E.running:
        # 1. Paranoia Check
        alerts = E.pa.check_integrity()
        for alert in alerts:
            push_event("paranoia_alert", alert)
            # If critical change, auto-track
            if "path" in alert:
                E.vt.track_file(alert["path"])
        
        # 2. Heartbeat
        push_event("pulse", {"node_id": "core", "t": time.time()})
        
        # 3. Simulate Story Progression (if no real intake)
        if time.time() % 30 < 5: # Every 30s, do a beat
            E.beat_count += 1
            push_event("story_beat", {
                "story_id": E.story_id,
                "beat": {
                    "beat_id": f"beat-{E.beat_count}",
                    "scene": f"Ecosystem loop cycle {E.beat_count}: Monitoring dimensions...",
                    "actors": ["DemonHand", "ParanoiaAgent"],
                    "timeline_index": E.beat_count,
                    "is_canon": True
                }
            })
            
        time.sleep(5)

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
        "beat_count": E.beat_count,
        "files_monitored": len(E.pa.signatures),
        "total_versions": sum(len(v["versions"]) for v in E.vt.version_index.values())
    })

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
        print(f"Ecosystem: Intent routed -> {structured.get('intent')}")

    threading.Thread(target=process, daemon=True).start()
    
    return json.dumps({"ok": True, "prompt_id": log["prompt_id"]})

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
