extends Control

## dimensional_hud.gd
## Visualizes the mathematical ratios and screen divisions for 'Dimensions'.
## Uses Golden Ratio (0.618) and Power-of-Two splits.

@export var line_color: Color = Color(0.48, 0.41, 0.97, 0.3) # Accent purple
@export var text_color: Color = Color(0.88, 0.88, 1.0, 0.8)

func _draw():
    var size = get_viewport_rect().size
    var phi = 0.61803398875
    
    # 1. Draw Golden Ratio Vertical Split (The Archive vs The Action)
    var v_split = size.x * phi
    draw_line(Vector2(v_split, 0), Vector2(v_split, size.y), line_color, 1.0)
    draw_string(ThemeDB.fallback_font, Vector2(v_split + 10, 30), "Ratio: 0.618 (The Golden Section)", HORIZONTAL_ALIGNMENT_LEFT, -1, 14, text_color)
    
    # 2. Draw Horizontal Zones (5D Timelines)
    var h_unit = size.y / 5
    for i in range(1, 5):
        var y = h_unit * i
        draw_line(Vector2(0, y), Vector2(size.x, y), line_color * 0.5, 1.0)
        draw_string(ThemeDB.fallback_font, Vector2(10, y - 5), "Timeline Layer " + str(i), HORIZONTAL_ALIGNMENT_LEFT, -1, 10, line_color)

    # 3. Corner Coordinates (Raw Math)
    draw_string(ThemeDB.fallback_font, Vector2(10, size.y - 10), "SCREEN_DIVIDE: " + str(size), HORIZONTAL_ALIGNMENT_LEFT, -1, 12, text_color)

func _process(_delta):
    queue_redraw() # Keep it updated if screen resizes
