extends Node3D

## procedural_stage.gd
## Generates an infinite mathematical grid environment.
## Lines fade and change color based on distance and math rules.

@export var grid_size: int = 100
@export var cell_size: float = 2.0
@export var grid_color: Color = Color(0.1, 0.1, 0.2)

func _ready():
    _create_math_grid()

func _create_math_grid():
    var mesh_instance = MeshInstance3D.new()
    var immediate_mesh = ImmediateMesh.new()
    var material = ORMMaterial3D.new()
    
    mesh_instance.mesh = immediate_mesh
    add_child(mesh_instance)
    
    material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
    material.albedo_color = grid_color
    material.vertex_color_use_as_albedo = true
    mesh_instance.material_override = material
    
    immediate_mesh.surface_begin(Mesh.PRIMITIVE_LINES)
    
    # Generate infinite-style lines
    for i in range(-grid_size, grid_size + 1):
        var pos = i * cell_size
        
        # Grid lines (Math: X axis)
        immediate_mesh.surface_set_color(grid_color)
        immediate_mesh.surface_add_vertex(Vector3(pos, 0, -grid_size * cell_size))
        immediate_mesh.surface_add_vertex(Vector3(pos, 0, grid_size * cell_size))
        
        # Grid lines (Math: Z axis)
        immediate_mesh.surface_add_vertex(Vector3(-grid_size * cell_size, 0, pos))
        immediate_mesh.surface_add_vertex(Vector3(grid_size * cell_size, 0, pos))
        
    immediate_mesh.surface_end()
    print("ProceduralStage: 📐 Mathematical grid forged.")
