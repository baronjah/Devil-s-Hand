extends Node

## theme_switcher.gd
## Listens for string commands from any source
## Maps phrase → theme resource
## Commands: "switch theme dark" / "switch theme fire" / "switch theme void"
## Hot-reloads without scene restart

@export var themes: Dictionary = {
    "dark": preload("res://themes/dark.tres"),
    "fire": preload("res://themes/fire.tres"),
    "void": preload("res://themes/void.tres")
}

func _ready():
    # Register with a global command bus or listener
    pass

func handle_command(command: String):
    if command.begins_with("switch theme "):
        var theme_name = command.replace("switch theme ", "").strip_edges()
        apply_theme(theme_name)

func apply_theme(theme_name: String):
    if themes.has(theme_name):
        var theme_res = themes[theme_name]
        # Logic to apply theme globally or to specific nodes
        print("Switching theme to: ", theme_name)
        # ProjectSettings.set_setting("gui/theme/custom", theme_res) # Example
    else:
        print("Theme not found: ", theme_name)
