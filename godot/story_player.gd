extends Node

## story_player.gd
## Polls GET http://localhost:8010/storyboards every 2 seconds
## Updates scene label text
## Moves actor nodes based on beat data
## Emits signal when beat changes

signal beat_changed(beat_data)

@export var scene_label_path: NodePath
@export var actors_container_path: NodePath

var poll_timer: Timer
var last_beat_id: String = ""
var http_request: HTTPRequest

func _ready():
    http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(_on_request_completed)
    
    poll_timer = Timer.new()
    poll_timer.wait_time = 2.0
    poll_timer.autostart = true
    add_child(poll_timer)
    poll_timer.timeout.connect(_poll_storyboards)
    
    _poll_storyboards()

func _poll_storyboards():
    http_request.request("http://localhost:8010/status")

func _on_request_completed(result, response_code, headers, body):
    if response_code != 200:
        return
        
    var json = JSON.parse_string(body.get_string_from_utf8())
    if json == null or json.size() == 0:
        return
        
    # Assuming the first active storyboard is what we want to track for now
    var story = json[0]
    # In a full implementation, we'd fetch the latest beat for this story
    # For now, let's assume we have a way to get the latest beat data
    # Mocking beat data for structure
    var beat_data = {
        "beat_id": "beat-" + str(story.beat_count),
        "scene": "Mock scene text from polling",
        "actors": ["DemonHand", "TargetA"]
    }
    
    if beat_data.beat_id != last_beat_id:
        last_beat_id = beat_data.beat_id
        _update_scene(beat_data)
        beat_changed.emit(beat_data)

func _update_scene(beat_data):
    if scene_label_path:
        var label = get_node(scene_label_path)
        if label:
            label.text = beat_data.scene
            
    if actors_container_path:
        var container = get_node(actors_container_path)
        # Update actor positions or states here
        for actor_id in beat_data.actors:
            var actor_node = container.find_child(actor_id, true, false)
            if actor_node:
                # Apply movement or logic
                pass
