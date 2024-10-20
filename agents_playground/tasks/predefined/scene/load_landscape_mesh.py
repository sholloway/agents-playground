from agents_playground.fp import Something
from agents_playground.scene import Scene
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.mesh import MeshData, MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import (
    HalfEdgeMesh,
    MeshWindingDirection,
)
from agents_playground.spatial.mesh.packers.normal_packer import NormalPacker
from agents_playground.spatial.mesh.packers.simple_mesh_packer import SimpleMeshPacker
from agents_playground.spatial.mesh.tesselator import FanTesselator
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    SimulationPhase,
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=Scene, name="scene")
@task_output(type=MeshData, name="landscape", release_on=SimulationPhase.ON_SHUTDOWN)
@task_output(
    type=MeshData, name="landscape_tri_mesh", release_on=SimulationPhase.ON_SHUTDOWN
)
@task(require_before=["load_scene"])
def load_landscape_mesh(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Build a half-edge mesh of the landscape."""
    scene: Scene = inputs.scene
    landscape: MeshData = MeshData()

    landscape_lattice_mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
    for tile in scene.landscape.tiles.values():
        tile_vertices = cubic_tile_to_vertices(tile, scene.landscape.characteristics)
        landscape_lattice_mesh.add_polygon(tile_vertices)
    landscape.mesh = Something(landscape_lattice_mesh)

    # 2. Tesselate the landscape.
    landscape_tri_mesh: MeshLike = landscape_lattice_mesh.deep_copy()
    FanTesselator().tesselate(landscape_tri_mesh)

    # 4. Calculate the normals for the tessellated landscape mesh.
    landscape_tri_mesh.calculate_face_normals()
    landscape_tri_mesh.calculate_vertex_normals()

    landscape_tri_mesh_data: MeshData = MeshData()
    landscape_tri_mesh_data.lod = 1
    landscape_tri_mesh_data.mesh_previous_lod_alias = Something("landscape")
    landscape_tri_mesh_data.mesh = Something(landscape_tri_mesh)
    landscape_tri_mesh_data.vertex_buffer = Something(
        SimpleMeshPacker().pack(landscape_tri_mesh)
    )
    landscape_tri_mesh_data.normals_buffer = Something(
        NormalPacker().pack(landscape_tri_mesh)
    )

    landscape.next_lod_alias = Something("landscape_tri_mesh")

    outputs.landscape = landscape
    outputs.landscape_tri_mesh = landscape_tri_mesh_data
