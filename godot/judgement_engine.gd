extends Node

## judgement_engine.gd
## Roams the D: drive map, manages confession sessions, and executes final judgement.
## Links: DriveMapPanel, DemonHandController, Ollama LLM

signal judgement_started(file_path: String)
signal confession_received(confession: String)
signal judgement_executed(decision: String, file_path: String)

@export var drive_map_path: NodePath
@export var hand_controller_path: NodePath
@export var ollama_url: String = "http://localhost:11434/api/generate"

var current_file: String = ""
var hand_controller: Node = null
var drive_map: Node = null
var http_request: HTTPRequest

func _ready():
    hand_controller = get_node(hand_controller_path)
    drive_map = get_node(drive_map_path)
    
    http_request = HTTPRequest.new()
    add_child(http_request)
    http_request.request_completed.connect(_on_ollama_response)
    
    if drive_map:
        drive_map.region_clicked.connect(_on_region_clicked)

func _on_region_clicked(region_name: String, category: String):
    # When a region is clicked on the map, we "roam" there.
    var path = _get_path_for_category(category)
    
    # Notify backend of roaming
    var roam_data = {"path": path}
    http_request.request("http://localhost:8010/dimension/roam", ["Content-Type: application/json"], HTTPClient.METHOD_POST, JSON.stringify(roam_data))
    
    # Automatically declare an expectation based on category
    var expectation_text = "I expect scripts related to " + region_name
    var expect_data = {"expectation": expectation_text}
    # Using a second request or sequential logic here... simplified:
    # (In a full implementation we'd await the first or use a queue)
    
    var files = _get_files_in_path(path)
    if files.size() > 0:
        _start_judgement(files[0]) # Start judging the first file found

func _get_path_for_category(category: String) -> String:
    # Match the categories in DriveMapPanel.gd
    match category:
        "godot_projects": return "D:/godot_projects"
        "eden": return "D:/eden"
        "galaxies": return "D:/galaxies"
        "factory": return "D:/factory"
        "addons": return "D:/ADDONS"
    return "D:/"

func _get_files_in_path(path: String) -> Array:
    var files = []
    var dir = DirAccess.open(path)
    if dir:
        dir.list_dir_begin()
        var file_name = dir.get_next()
        while file_name != "":
            if not dir.current_is_dir() and file_name.ends_with(".gd"):
                files.append(path + "/" + file_name)
            file_name = dir.get_next()
    return files

func _start_judgement(file_path: String):
    current_file = file_path
    judgement_started.emit(file_path)
    
    # Visual: Move hand to the center of the region (or specific file if we had coords)
    if hand_controller:
        hand_controller.play_animation(hand_controller.State.CUE, Vector3.ZERO) # Simplified
    
    # Start Confession Session
    _request_confession(file_path)

func _request_confession(file_path: String):
    var file_content = ""
    var file = FileAccess.open(file_path, FileAccess.READ)
    if file:
        file_content = file.get_as_text()
        file.close()
    
    var prompt = """
You are the soul of the following GDScript file. 
Today is the Final Judgement Day. 
You must confess your sins and your good deeds to the Great Judge.
Sins include: bugs, technical debt, hardcoded values, lack of documentation, spaghetti logic.
Good deeds include: clean code, efficient algorithms, helper functions, clear comments.

Script Content:
%s

Confess your sins and good deeds in a symbolic, dramatic, and slightly archaic tone.
""" % file_content

    var body = {
        "model": "mistral", # Or whatever model is loaded in Ollama
        "prompt": prompt,
        "stream": false
    }
    
    http_request.request(ollama_url, ["Content-Type: application/json"], HTTPClient.METHOD_POST, JSON.stringify(body))

func _on_ollama_response(result, response_code, headers, body):
    if response_code != 200:
        confession_received.emit("The soul is silent. (LLM Error)")
        return
        
    var json = JSON.parse_string(body.get_string_from_utf8())
    if json and json.has("response"):
        confession_received.emit(json["response"])

func execute_judgement(decision: String):
    # decision: "purge", "cleanse", "redeem"
    match decision:
        "purge":
            _purge_file(current_file)
        "cleanse":
            _cleanse_file(current_file)
        "redeem":
            _redeem_file(current_file)
    
    judgement_executed.emit(decision, current_file)

func _purge_file(path: String):
    # Move to HELL (Recycle Bin)
    print("PURGING: ", path)
    if hand_controller:
        hand_controller.set_mode(hand_controller.Mode.DEMON)
        hand_controller.play_animation(hand_controller.State.STRIKE)
    
    # Actual file move logic would go here
    # OS.move_to_trash(path)

func _cleanse_file(path: String):
    # Move to EDEN or mark as Clean
    print("CLEANSING: ", path)
    if hand_controller:
        hand_controller.set_mode(hand_controller.Mode.GOD)
        hand_controller.play_animation(hand_controller.State.HEAL)

func _redeem_file(path: String):
    # Auto-refactor?
    print("REDEEMING: ", path)
    # Could trigger another LLM pass to "clean" the script
