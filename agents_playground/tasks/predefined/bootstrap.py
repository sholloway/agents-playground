print("Loading agents_playground.tasks.predefined.bootstrap")
import logging
from typing import cast

from wgpu import GPUCanvasContext, GPUDevice
from wgpu import GPUDevice
from wgpu.gui.wx import WgpuWidget

from agents_playground.fp import Something
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.landscape_renderer_builder import (
    LandscapeRendererBuilder,
)
from agents_playground.gpu.renderer_builders.renderer_builder import (
    RenderingPipelineBuilder,
)
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.landscape_renderer import LandscapeRenderer
from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.scene import Scene
from agents_playground.simulation.simulation_context_builder import (
    SimulationContextBuilder,
)
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.mesh import MeshData, MeshLike
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
from agents_playground.tasks.types import TaskResource

logger: logging.Logger = get_default_logger()


@task_input(type=str, name="scene_file_path")
@task_output(type=Scene, name="scene")
@task()
def load_scene(task_graph: TaskGraph) -> None:
    """
    A task that is responsible for parsing the provided scene file.

    Effects:
    - The JSON scene file that is provided as an input is parsed.
    - The resulting Scene instance is allocated as an output.
    """
    logger.info("Running load_scene task.")
    # Get the inputs
    scene_file_path_resource: TaskResource = task_graph.resource_tracker[
        "scene_file_path"
    ]
    scene_path = scene_file_path_resource.resource.unwrap()

    sim_context_builder_resource: TaskResource = task_graph.resource_tracker[
        "sim_context_builder"
    ]
    sim_context_builder = sim_context_builder_resource.resource.unwrap()

    # Load the Scene.
    scene_loader = SceneLoader()
    scene: Scene = scene_loader.load(scene_path)

    # Allocate the task outputs.
    task_graph.provision_resource("scene", instance=scene)


@task_input(type=Scene, name="scene")
@task_output(type=MeshData, name="landscape")
@task_output(type=MeshData, name="landscape_tri_mesh")
@task(require_before=["load_scene"])
def load_landscape_mesh(task_graph: TaskGraph) -> None:
    """Build a half-edge mesh of the landscape."""
    logger.info("Running load_landscape_mesh task.")
    scene: Scene = task_graph.resource_tracker["scene"].resource.unwrap()

    landscape_resource: TaskResource = task_graph.provision_resource("landscape")
    landscape: MeshData = cast(MeshData, landscape_resource.resource.unwrap())

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

    landscape_tri_mesh_resource: TaskResource = task_graph.provision_resource(
        "landscape_tri_mesh"
    )
    landscape_tri_mesh_data: MeshData = cast(
        MeshData, landscape_tri_mesh_resource.resource.unwrap()
    )
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


@task_input(type=WgpuWidget, name="canvas")
@task_output(type=GPUDevice, name="gpu_device")
@task_output(type=str, name="render_texture_format")
@task(require_before=["load_landscape_mesh"])
def initialize_graphics_pipeline(task_graph: TaskGraph) -> None:
    """
    A task responsible for initializing the graphics pipeline.
    """
    logger.info("Running initialize_graphics_pipeline task.")
    # Initialize the graphics pipeline via WebGPU.
    canvas: WgpuWidget = task_graph.resource_tracker["canvas"].resource.unwrap()

    # Create a high performance GPUAdapter for a Canvas.
    adapter: wgpu.GPUAdapter = wgpu.gpu.request_adapter(  # type: ignore
        canvas=canvas, power_preference="high-performance"
    )

    # Get an instance of the GPUDevice that is associated with a provided GPUAdapter.
    device = adapter.request_device(
        label="only-gpu-device",
        required_features=[],
        required_limits={},
        default_queue={},
    )

    canvas_context: GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format: str = canvas_context.get_preferred_format(device.adapter)

    canvas_context.configure(
        device=device,
        usage=wgpu.flags.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
        format=render_texture_format,
        view_formats=[],
        color_space="bgra8unorm-srgb",
        alpha_mode="opaque",
    )

    task_graph.provision_resource("gpu_device", instance=device)
    task_graph.provision_resource(
        "render_texture_format", instance=render_texture_format
    )


@task_output(type=GPURenderer, name="landscape_renderer")
@task(require_before=["initialize_graphics_pipeline"])
def prepare_landscape_renderer(task_graph: TaskGraph) -> None:
    """
    A task that is responsible for building the renderer specific to the landscape.
    """
    logger.info("Running prepare_landscape_renderer task.")
    pc = PipelineConfiguration()
    builder: RenderingPipelineBuilder = LandscapeRendererBuilder()
    render_pipeline = builder.build(sim_context_builder, pc)
    renderer: GPURenderer = LandscapeRenderer(render_pipeline)
    task_graph.provision_resource("landscape_renderer", instance=renderer)


"""
Next Steps
- Decide what I want to do about the SimulationContextBuilder and the RenderingPipelineBuilders.
"""
