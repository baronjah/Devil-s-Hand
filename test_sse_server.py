import time
import json
import random
from flask import Flask, Response, stream_with_context, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_events():
    story_id = "test-story-001"
    beat_id = 1
    
    while True:
        # Emit a pulse event
        yield f"event: pulse\ndata: {json.dumps({'node_id': 'core', 'var': 'heartbeat', 'old_val': 0, 'new_val': 1, 't': time.time()})}\n\n"
        
        # Randomly emit other events
        r = random.random()
        if r < 0.2:
            beat_id += 1
            beat = {
                "story_id": story_id,
                "beat": {
                    "beat_id": f"beat-{beat_id}",
                    "story_id": story_id,
                    "scene": f"Mock scene description for beat {beat_id}",
                    "actors": ["DemonHand", "UserTarget"],
                    "actions": [{"actor": "DemonHand", "type": "move", "target": "UserTarget", "params": {}}],
                    "timeline_index": beat_id,
                    "visual_cue": "pulse",
                    "detail_weight": 0.5,
                    "branch_of": None,
                    "is_canon": True,
                    "snapshot_path": None
                }
            }
            yield f"event: story_beat\ndata: {json.dumps(beat)}\n\n"
        
        elif r < 0.4:
            possession = {
                "character_id": "TargetA",
                "controller": random.choice(["user", "ai", "shared"]),
                "turn_owner": random.choice(["user", "ai"]),
                "turn_started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "turn_duration_ms": 10000,
                "bonus_applied": False,
                "bonus_multiplier": 1.0,
                "override_available": True,
                "user_control_share_last_10": 0.5
            }
            yield f"event: possession\ndata: {json.dumps(possession)}\n\n"
            
            turn_start = {
                "owner": possession["turn_owner"],
                "duration_ms": 10000,
                "bonus": False
            }
            yield f"event: turn_start\ndata: {json.dumps(turn_start)}\n\n"

        elif r < 0.5:
            yield f"event: subsystem_down\ndata: {json.dumps({'name': 'VisionNode', 'will_restart': True})}\n\n"

        elif r < 0.7:
            # Simulate a confession
            confession = {
                "file_path": "D:/godot_projects/fab/scripts/NeuralHandshake.gd",
                "confession": "Forgive me, Judge, for I have sinned. I contain hardcoded paths to 'D:/' and 'C:/', which is a sin of rigidity. I have no error handling for missing scenes, a sin of pride. But I have also done good deeds: I bridge worlds and allow the AI to roam freely across dimensions. I seek redemption."
            }
            yield f"event: confession\ndata: {json.dumps(confession)}\n\n"

        time.sleep(3)

@app.route('/events/stream')
def stream():
    return Response(stream_with_context(generate_events()), mimetype="text/event-stream")

@app.route('/storyboards')
def storyboards():
    return json.dumps([{"story_id": "test-story-001", "state": "active", "beat_count": 5}])

@app.route('/judgement/execute', methods=['POST'])
def execute_judgement():
    data = json.loads(request.data)
    print(f"Executing judgement: {data['decision']}")
    return json.dumps({"ok": True, "decision": data['decision']})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8010, debug=True)
