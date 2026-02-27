extends Node3D

## demon_hand_controller.gd
## 4 animation states: cue, possess, preview_path, strike
## Triggered by: HTTP poll OR SSE pulse event
## Theme-aware: reads from ThemeRegistry resource

@export var theme_registry: Resource # Assuming a ThemeRegistry resource type exists

enum State { IDLE, CUE, POSSESS, PREVIEW, STRIKE, HEAL }
enum Mode { DEMON, GOD }

var current_state = State.IDLE
var current_mode = Mode.DEMON
var _time: float = 0.0

func _ready():
    _update_visuals()

func _process(delta: float):
    _time += delta
    if current_state == State.IDLE:
        _animate_idle_math(delta)

func _animate_idle_math(delta: float):
    # Lissajous Curve Idle (Math-driven life)
    # x = A sin(at + delta), y = B sin(bt)
    var a = 1.0
    var b = 2.0
    var x = sin(a * _time) * 0.2
    var y = sin(b * _time) * 0.1
    var z = cos(a * _time) * 0.1
    
    global_position += Vector3(x, y, z) * delta
    
    # Fibonacci Pulse (1.0 -> 1.618)
    var pulse = 1.0 + (abs(sin(_time * 0.5)) * 0.618)
    scale = Vector3(pulse, pulse, pulse)

func set_mode(mode: Mode):
    current_mode = mode
    _update_visuals()

func play_animation(state: State, target_pos: Vector3 = Vector3.ZERO):
    current_state = state
    match current_state:
        State.CUE:
            _animate_cue(target_pos)
        State.POSSESS:
            _animate_possess(target_pos)
        State.PREVIEW:
            _animate_preview(target_pos)
        State.STRIKE:
            _animate_strike(target_pos)
        State.HEAL:
            _animate_heal(target_pos)

func _animate_cue(target: Vector3):
    # Point at next action target
    var tween = create_tween()
    tween.tween_property(self, "quaternion", Quaternion(Vector3.FORWARD, (target - global_position).normalized()), 0.5)

func _animate_possess(target: Vector3):
    # Glow ring appears around target
    print("Possessing target at ", target)
    _update_visuals()

func _animate_preview(target: Vector3):
    # Dashed arc shows proposed move
    pass

func _animate_strike(target: Vector3):
    # Fast snap on confirmed action
    # Strike animation: scale 1.0 → 1.3 → 0.9 → 1.0, 8 frames, ease-out
    var tween = create_tween()
    tween.set_ease(Tween.EASE_OUT)
    tween.tween_property(self, "global_position", target, 0.1)
    tween.tween_property(self, "scale", Vector3(1.3, 1.3, 1.3), 0.05)
    tween.tween_property(self, "scale", Vector3(0.9, 0.9, 0.9), 0.05)
    tween.tween_property(self, "scale", Vector3(1.0, 1.0, 1.0), 0.05)

func _animate_heal(target: Vector3):
    # Golden glow and gentle pulse
    var tween = create_tween()
    tween.set_loops(2)
    tween.tween_property(self, "scale", Vector3(1.2, 1.2, 1.2), 0.3)
    tween.tween_property(self, "scale", Vector3(1.0, 1.0, 1.0), 0.3)
    _set_hand_color(Color(1.0, 0.84, 0.0)) # Gold

func _update_visuals():
    if current_mode == Mode.DEMON:
        _set_hand_color(Color(0.6, 0.0, 1.0)) # Purple AI / Demon
    else:
        _set_hand_color(Color(1.0, 0.84, 0.0)) # Gold / God

func _set_hand_color(color: Color):
    # Logic to update material color
    # Assuming there's a MeshInstance3D as a child
    var mesh = find_child("*MeshInstance3D*", true, false)
    if mesh and mesh.get_surface_override_material(0):
        mesh.get_surface_override_material(0).set_shader_parameter("albedo", color)

func _on_sse_pulse(data):
    # React to SSE pulse
    if data.has("var") and data["var"] == "possession":
        play_animation(State.POSSESS)
