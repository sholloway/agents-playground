print("Loading agents_playground.tasks.predefined.bootstrap")
import logging
from typing import cast

from agents_playground.fp import Something
from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.scene import Scene
from agents_playground.simulation.simulation_context_builder import (
    SimulationContextBuilder,
)
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.mesh import MeshData, MeshLike, MeshRegistry
from agents_playground.spatial.mesh.half_edge_mesh import (
    HalfEdgeMesh,
    MeshWindingDirection,
)
from agents_playground.spatial.mesh.packers.normal_packer import NormalPacker
from agents_playground.spatial.mesh.packers.simple_mesh_packer import SimpleMeshPacker
from agents_playground.spatial.mesh.tesselator import FanTesselator
from agents_playground.sys.logger import get_default_logger
from agents_playground.tasks.graph import TaskGraph
from agents_playground.tasks.register import task, task_input, task_output

logger: logging.Logger = get_default_logger()


@task_output(type=Scene, name="scene")
@task()
def load_scene(
    task_graph: TaskGraph,
    scene_path: str,
    sim_context_builder: SimulationContextBuilder,
) -> None:
    logger.info("Running load_scene task.")
    scene_loader = SceneLoader()
    sim_context_builder.scene = scene_loader.load(scene_path)


@task_input(type=Scene, name="scene")
@task_output(type=MeshData, name="landscape")
@task_output(type=MeshData, name="landscape_tri_mesh")
@task(require_before=["load_scene"])
def load_landscape_mesh(
    task_graph: TaskGraph, sim_context_builder: SimulationContextBuilder
) -> None:
    """Build a half-edge mesh of the landscape."""
    logger.info("Running load_landscape_mesh task.")
    scene: Scene = sim_context_builder.scene

    landscape: MeshData = cast(MeshData, task_graph.provision_resource("landscape"))

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

    landscape_tri_mesh_resource: MeshData = cast(
        MeshData, task_graph.provision_resource("landscape_tri_mesh")
    )
    landscape_tri_mesh_resource.lod = 1
    landscape_tri_mesh_resource.mesh_previous_lod_alias = Something("landscape")
    landscape_tri_mesh_resource.mesh = Something(landscape_tri_mesh)
    landscape_tri_mesh_resource.vertex_buffer = Something(
        SimpleMeshPacker().pack(landscape_tri_mesh)
    )
    landscape_tri_mesh_resource.normals_buffer = Something(
        NormalPacker().pack(landscape_tri_mesh)
    )

    landscape.next_lod_alias = Something("landscape_tri_mesh")


@task(require_before=["load_landscape_mesh"])
def initialize_graphics_pipeline(
    task_graph: TaskGraph,
    sim_context_builder: SimulationContextBuilder,
) -> None:
    logger.info("Running initialize_graphics_pipeline task.")
    # Before implementing this change TaskResource to be a wrapper.


@task(require_before=["initialize_graphics_pipeline"])
def prepare_landscape_renderer(
    task_graph: TaskGraph,
    sim_context_builder: SimulationContextBuilder,
) -> None:
    logger.info("Running prepare_landscape_renderer task.")
    # Before implementing this change TaskResource to be a wrapper.
