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
from agents_playground.gpu.camera_configuration.camera_configuration_builder import (
    CameraConfigurationBuilder,
)
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import (
    TriangleListMeshConfigurationBuilder,
)
from agents_playground.gpu.shader_configuration.default_shader_configuration_builder import (
    DefaultShaderConfigurationBuilder,
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

    # Create the configuration objects
    pc = PipelineConfiguration()
    camera_config = CameraConfigurationBuilder()
    shader_config = DefaultShaderConfigurationBuilder()
    mesh_config = TriangleListMeshConfigurationBuilder("Landscape")

    # Load Shaders

    # Build the Pipeline Configuration

    # Load the Mesh

    # Setup the Camera

    # Setup the model transform

    # Setup the uniform bind groups

    # Create the rendering pipeline.

    # Create Bind Groups

    # Load Uniform Buffers

    # Construct the LandscapeRender

    # builder: RenderingPipelineBuilder = LandscapeRendererBuilder()
    # render_pipeline = builder.build(sim_context_builder, pc)
    # renderer: GPURenderer = LandscapeRenderer(render_pipeline)

    # Set the outputs.
    task_graph.provision_resource("landscape_renderer", instance=renderer)


"""
Next Steps
- Decide what I want to do about the SimulationContextBuilder and the RenderingPipelineBuilders.

The renderer builders does the steps.
self._load_shaders(sim_context_builder, pc)
self._build_pipeline_configuration(sim_context_builder, pc)
self._load_mesh(sim_context_builder, pc)
self._setup_camera(sim_context_builder, pc)
self._setup_model_transforms(sim_context_builder, pc)
self._setup_uniform_bind_groups(sim_context_builder, pc)
self._rendering_pipeline = self._setup_renderer_pipeline(sim_context_builder, pc)
self._create_bind_groups(sim_context_builder, pc)
self._load_uniform_buffers(sim_context_builder, pc)
return self._rendering_pipeline

Perhaps flattening this out into a big task will help align to the TaskGraph.
Probably needs to be a few smaller tasks (that could be run in parallel.)
"""
