from fractions import Fraction
from functools import partial
from math import floor,radians
from multiprocessing.connection import Connection
import os
from pprint import pp
import statistics
import traceback

import wx
import wgpu
from wgpu import GPUBuffer
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.cameras.camera import Camera
from agents_playground.core.constants import FRAME_SAMPLING_SERIES_LENGTH
from agents_playground.core.duration_metrics_collector import sample_duration
from agents_playground.core.observe import Observable
from agents_playground.core.performance_monitor import PerformanceMetrics, PerformanceMonitor
from agents_playground.core.privileged import require_root
from agents_playground.core.samples import SamplesDistribution
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.webgpu_sim_loop import WGPU_SIM_LOOP_EVENT, WGPUSimLoop, WGPUSimLoopEvent, WGPUSimLoopEventMsg
from agents_playground.fp import Maybe, Nothing, Something
# from agents_playground.gpu.overlays import Overlay, OverlayBufferNames

from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.landscape_renderer_builder import (
    LandscapeRendererBuilder,
    assemble_camera_data,
)
# from agents_playground.gpu.renderers.agent_renderer import AgentRenderer
from agents_playground.gpu.renderer_builders.normals_renderer_builder import NormalsRendererBuilder
from agents_playground.gpu.renderer_builders.renderer_builder import RenderingPipelineBuilder
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.normals_renderer import NormalsRenderer
from agents_playground.gpu.renderers.landscape_renderer import LandscapeRenderer
from agents_playground.loaders import find_valid_path, search_directories
from agents_playground.loaders.obj_loader import ObjLoader
from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.scene import Scene, SceneLoadingError
from agents_playground.simulation.context import SimulationContext, UniformRegistry
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.simulation.simulation_context_builder import SimulationContextBuilder
from agents_playground.spatial.landscape import cubic_tile_to_vertices
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.mesh import MeshData, MeshLike, MeshRegistry
from agents_playground.spatial.mesh.half_edge_mesh import (
    HalfEdgeMesh,
    MeshWindingDirection,
    obj_to_mesh,
    requires_triangulation,
)
from agents_playground.spatial.mesh.packers.normal_packer import NormalPacker
from agents_playground.spatial.mesh.packers.simple_mesh_packer import SimpleMeshPacker
from agents_playground.spatial.mesh.tesselator import FanTesselator
from agents_playground.spatial.vector.vector import Vector
from agents_playground.sys.logger import get_default_logger, log_call, log_table

logger = get_default_logger()

def print_camera(camera: Camera) -> None:
    # Write a table of the Camera's location and focus.
    table_format = "{:<20} {:<20} {:<20} {:<20}"
    header = table_format.format("", "X", "Y", "Z")
    loc_row = table_format.format(
        "Camera Location", camera.position.i, camera.position.j, camera.position.k
    )

    facing: Vector = camera.facing.unwrap()
    right: Vector = camera.right.unwrap()
    up: Vector = camera.up.unwrap()

    facing_row = table_format.format("Facing", facing.i, facing.j, facing.k)  # type: ignore
    right_row = table_format.format("Right", right.i, right.j, right.k)  # type: ignore
    up_row = table_format.format("Up", up.i, up.j, up.k)  # type: ignore
    target_row = table_format.format("Target", camera.target.i, camera.target.j, camera.target.k)  # type: ignore

    print("Camera Information")
    print(header)
    print(target_row)
    print(loc_row)
    print(facing_row)
    print(right_row)
    print(up_row)

@sample_duration(sample_name="draw_frame", count=FRAME_SAMPLING_SERIES_LENGTH)
def draw_frame(
    context: SimulationContext,
    renderers: dict[str, GPURenderer]
):
    """
    The main render function. This is responsible for populating the queues of the
    various rendering pipelines for all geometry that needs to be rendered per frame.

    It is bound to the canvas.
    """
    # 1. Calculate the current aspect ratio.
    canvas_width, canvas_height = context.canvas.GetSize()
    aspect_ratio = Fraction(canvas_width, canvas_height)

    canvas_context: wgpu.GPUCanvasContext = context.canvas.get_context()
    current_texture: wgpu.GPUTexture = canvas_context.get_current_texture()

    # 2. Calculate the projection matrix.
    context.scene.camera.projection_matrix = Something(
        Matrix4x4.perspective(
            aspect_ratio=aspect_ratio, v_fov=radians(72.0), near=0.1, far=100.0
        )
    )
    camera_data = assemble_camera_data(context.scene.camera)
    camera_buffer: GPUBuffer = context.uniforms['camera'].buffer.unwrap_or_throw('The camera buffer was not set on the uniform.')
    context.device.queue.write_buffer(camera_buffer, 0, camera_data)

    # 3. Build a render pass color attachment.
    # struct.RenderPassColorAttachment
    color_attachment = {
        "view": current_texture.create_view(),
        "resolve_target": None,
        "clear_value": (0.9, 0.5, 0.5, 1.0),  # Clear to pink.
        "load_op": wgpu.LoadOp.clear,  # type: ignore
        "store_op": wgpu.StoreOp.store,  # type: ignore
    }

    # 4. Create a depth texture for the Z-Buffer.
    depth_texture: wgpu.GPUTexture = context.device.create_texture(
        label="Z Buffer Texture",
        size=current_texture.size,
        usage=wgpu.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
        format=wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
    )
    depth_texture_view = depth_texture.create_view()

    # 5. Create a depth stencil attachment.
    depth_attachment = {
        "view": depth_texture_view,
        "depth_clear_value": 1.0,
        "depth_load_op": wgpu.LoadOp.clear,  # type: ignore
        "depth_store_op": wgpu.StoreOp.store,  # type: ignore
        "depth_read_only": False,
        # I'm not sure about these values.
        "stencil_clear_value": 0,
        "stencil_load_op": wgpu.LoadOp.load,  # type: ignore
        "stencil_store_op": wgpu.StoreOp.store,  # type: ignore
        "stencil_read_only": False,
    }

    # 6. Create a GPU command encoder.
    command_encoder: wgpu.GPUCommandEncoder = context.device.create_command_encoder()

    # 7. Encode the drawing instructions.
    # The first command to encode is the instruction to do a rendering pass.
    frame_pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
        label="Draw Frame Render Pass",
        color_attachments=[color_attachment],
        depth_stencil_attachment=depth_attachment,
        occlusion_query_set=None,  # type: ignore
        timestamp_writes=None,
        max_draw_count=50_000_000,  # Default
    )

    # Set the landscape rendering pipe line as the active one.
    # Encode the landscape drawing instructions.
    landscape_renderer: GPURenderer = renderers['landscape_renderer']
    frame_pass_encoder.set_pipeline(landscape_renderer.render_pipeline)
    landscape_renderer.render(
        frame_pass_encoder, context.mesh_registry["landscape_tri_mesh"]
    )

    # # Set the normals rendering pipe line as the active one.
    # # Encode the normals drawing instructions.
    normals_renderer: GPURenderer = renderers['normals_renderer']
    frame_pass_encoder.set_pipeline(normals_renderer.render_pipeline)
    normals_renderer.render(
        frame_pass_encoder, context.mesh_registry["landscape_tri_mesh"]
    )

    # # Render the agents
    # # Note this needs to be driven from the scene.agents not the mesh_data.
    # agent_mesh_data: list[MeshData] = mesh_registry.filter("agent_model")
    # for agent_renderer in agent_renderers:
    #     frame_pass_encoder.set_pipeline(agent_renderer.render_pipeline)
    #     for mesh_data in agent_mesh_data:
    #         agent_renderer.render(frame_pass_encoder, frame_data, mesh_data)

    # Draw the overlay.
    # viewport_data = create_array('f', [canvas_width, canvas_height])
    # device.queue.write_buffer(frame_data.overlay_buffers[OverlayBufferNames.VIEWPORT], 0, viewport_data)
    # print(f"Viewport: {canvas_width},{canvas_height}")
    # # fmt: off
    # overlay_config = [
    #     0, 0,               # X,Y
    #     canvas_width,       # Width
    #     canvas_height,      # Height
    #     1.0, 0.0, 0.0, 1.0, # Background Color (Red),
    #     0.0, 0.0, 1.0, 1.0  # Foreground Color (Blue)
    # ]
    # # fmt: on
    # overlay_config_data = create_array('f', overlay_config)
    # device.queue.write_buffer(frame_data.overlay_buffers[OverlayBufferNames.CONFIG], 0, overlay_config_data)

    # frame_pass_encoder.set_pipeline(overlay.render_pipeline)
    # overlay.render(frame_pass_encoder, frame_data, scene)

    # Submit the draw calls to the GPU.
    frame_pass_encoder.end()
    context.device.queue.submit([command_encoder.finish()])

class SimulationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

PERF_MONITOR_ERROR_MSG = "The Performance Monitor sent an EOFError. The process may have crashed."
class WebGPUSimulation(Observable):
    @log_call
    def __init__(
        self,
        parent: wx.Window,
        canvas: WgpuWidget,
        scene_file: str,
        scene_loader: SceneLoader,
    ) -> None:
        super().__init__()
        self._scene_file = scene_file
        self._scene_loader = scene_loader
        self._sim_context_builder = SimulationContextBuilder(
            canvas= canvas,
            mesh_registry = MeshRegistry(),
            renderers = {},
            uniforms = UniformRegistry(),
            extensions ={}
        )
        self._sim_context: SimulationContext # This is set by the self._sim_context_builder in the launch method.
        
        self._task_scheduler = TaskScheduler()
        self._pre_sim_task_scheduler = TaskScheduler()
        self._perf_monitor: Maybe[PerformanceMonitor] = Something(PerformanceMonitor())
        self._perf_receive_pipe: Maybe[Connection] = Nothing()

        # self._overlay = Overlay() # TODO: Transition to a GPURenderer

        self._sim_loop: WGPUSimLoop = WGPUSimLoop(
            scheduler = self._task_scheduler,
            window = canvas
        )
                
    def bind_event_listeners(self, frame: wx.Panel) -> None:
        """
        Given a panel, binds event listeners.
        """
        frame.Bind(wx.EVT_CHAR, self._handle_key_pressed)
        frame.Connect(-1, -1, WGPU_SIM_LOOP_EVENT, self._handle_sim_loop_event)

    def _handle_sim_loop_event(self, event: WGPUSimLoopEvent) -> None:
        match event.msg:
            case WGPUSimLoopEventMsg.REDRAW:
                self._sim_context.canvas.request_draw()
            case WGPUSimLoopEventMsg.UPDATE_FPS:
                self._update_fps()
            case WGPUSimLoopEventMsg.UTILITY_SAMPLES_COLLECTED:
                self._update_frame_performance_metrics()
            case WGPUSimLoopEventMsg.TIME_TO_MONITOR_HARDWARE:
                pass
                # self._update_hardware_metrics()
            case WGPUSimLoopEventMsg.SIMULATION_STARTED:
                pass
            case WGPUSimLoopEventMsg.SIMULATION_STOPPED:
                pass
            case _:
                print(f"SimLoopEvent: Got a message I can't handle. {event.msg}")
        

    @log_call
    def launch(self) -> None:
        """
        Starts the simulation running.
        """
        self._sim_context_builder.scene = self._scene_loader.load(self._scene_file)
        self._construct_landscape_mesh(self._sim_context_builder)
        self._construct_agent_meshes(self._sim_context_builder)
        self._initialize_graphics_pipeline(self._sim_context_builder)

        # Setup the Rendering Pipelines
        self._prepare_landscape_renderer(self._sim_context_builder)
        self._prepare_normals_renderer(self._sim_context_builder)
        # self._prepare_agent_renderers(self._sim_context_builder)
        # self._prepare_overlays(self._sim_context_builder)

        # Start the sim loop.
        if self._sim_context_builder.is_ready():
            self._sim_context = self._sim_context_builder.create_context()
            # Bind functions to key data structures.
            self._bound_draw_frame = partial(
                draw_frame,
                self._sim_context,
                self._sim_context_builder.renderers
            )
            self._sim_context.canvas.request_draw(self._bound_draw_frame)
            self._sim_loop.simulation_state = SimulationState.RUNNING
            self._start_perf_monitor()
            self._sim_loop.start(self._sim_context)
        else:
            raise SimulationError("Attempted to launch the simulation before it was ready.")

    @log_call
    def shutdown(self) -> None:
        # 1. Stop the simulation thread and task scheduler.
        self.simulation_state = SimulationState.ENDED
        self._task_scheduler.stop()

        # 2. Stop the performance monitor process if it's going.
        if self._perf_monitor.is_something():
            self._perf_monitor.unwrap().stop()
            self._perf_monitor = Nothing()

        # 3. Kill the simulation thread.
        self._sim_loop.end()

        # 4. Remove the reference to the simulations key components.
        self._task_scheduler.purge()
        self._pre_sim_task_scheduler.purge()

        # 6. Purge the Context Object
        self._sim_context.purge()

        # 7. Purge any extensions defined by the Simulation's Project
        # TODO: Re-introduce simulation extensions.
        # simulation_extensions().reset()

    @require_root
    def _start_perf_monitor(self):
        try:
            if self._perf_monitor.is_something():
                self._perf_receive_pipe = Something(self._perf_monitor.unwrap().start(os.getpid()))
        except Exception as e:
            logger.error('Failed to start the performance monitor.')
            logger.error(e, exc_info=True)
        
    def _construct_landscape_mesh(
        self, 
        sim_context_builder: SimulationContextBuilder
    ) -> None:
        """Build a half-edge mesh of the landscape."""
        mesh_registry: MeshRegistry = sim_context_builder.mesh_registry
        scene: Scene = sim_context_builder.scene

        mesh_registry.add_mesh(MeshData("landscape"))
        landscape_lattice_mesh: MeshLike = HalfEdgeMesh(winding=MeshWindingDirection.CW)
        for tile in scene.landscape.tiles.values():
            tile_vertices = cubic_tile_to_vertices(
                tile, scene.landscape.characteristics
            )
            landscape_lattice_mesh.add_polygon(tile_vertices)
        mesh_registry["landscape"].mesh = Something(landscape_lattice_mesh)

        # 2. Tesselate the landscape.
        landscape_tri_mesh: MeshLike = landscape_lattice_mesh.deep_copy()
        FanTesselator().tesselate(landscape_tri_mesh)

        # 4. Calculate the normals for the tessellated landscape mesh.
        landscape_tri_mesh.calculate_face_normals()
        landscape_tri_mesh.calculate_vertex_normals()

        mesh_registry.add_mesh(
            MeshData(
                "landscape_tri_mesh",
                lod=1,
                mesh_previous_lod_alias=Something("landscape"),
                mesh=Something(landscape_tri_mesh),
                vertex_buffer=Something(SimpleMeshPacker().pack(landscape_tri_mesh)),
                normals_buffer=Something(NormalPacker().pack(landscape_tri_mesh)),
            )
        )
        mesh_registry["landscape"].next_lod_alias = Something("landscape_tri_mesh")

    def _construct_agent_meshes(
        self, 
        sim_context_builder: SimulationContextBuilder
    ) -> None:
        mesh_registry: MeshRegistry = sim_context_builder.mesh_registry
        scene: Scene = sim_context_builder.scene

        if len(scene.agents) == 0:
            return

        obj_loader = ObjLoader()
        tesselator = FanTesselator()
        mesh_packer = SimpleMeshPacker()
        normals_packer = NormalPacker()
        dirs = search_directories()

        agent: AgentLike
        for agent in scene.agents:
            # For an agent, find it's Agent Definition, load the specified 3d model if
            # it isn't already.
            if agent.agent_def_alias not in mesh_registry:
                # Find the model
                model_path: str = scene.agent_definitions[
                    agent.agent_def_alias
                ].agent_model
                file_found, verified_path = find_valid_path(model_path, dirs)
                if not file_found:
                    raise SceneLoadingError(
                        f"Could not find the 3D model at {model_path} or in {dirs}."
                    )

                # Load the model into a mesh.
                obj_model = obj_loader.load(verified_path)
                agent_mesh: MeshLike = obj_to_mesh(obj_model)

                # Tesselate any polygons that aren't triangles.
                if requires_triangulation(agent_mesh):
                    tesselator.tesselate(agent_mesh)

                # Build the mesh data.
                mesh_data = MeshData(
                    alias=agent.agent_def_alias,
                    lod=0,
                    mesh=Something(agent_mesh),
                    vertex_buffer=Something(mesh_packer.pack(agent_mesh)),
                    normals_buffer=Something(normals_packer.pack(agent_mesh)),
                )
                mesh_registry.add_mesh(mesh_data, tags=["agent_model"])

    def _initialize_graphics_pipeline(
        self, 
        sim_context_builder: SimulationContextBuilder
    ) -> None:
        # Initialize the graphics pipeline via WebGPU.
        canvas: WgpuWidget = sim_context_builder.canvas
        adapter: wgpu.GPUAdapter = self._provision_adapter(canvas)
        device = self._provision_gpu_device(adapter)
        sim_context_builder.device = device
        canvas_context: wgpu.GPUCanvasContext = canvas.get_context()

        # Set the GPUCanvasConfiguration to control how drawing is done.
        render_texture_format: str = canvas_context.get_preferred_format(
            device.adapter
        )

        canvas_context.configure(
            device=device,
            usage=wgpu.flags.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
            format=render_texture_format,
            view_formats=[],
            color_space="bgra8unorm-srgb",
            alpha_mode="opaque",
        )

        sim_context_builder.render_texture_format = render_texture_format

    def _prepare_landscape_renderer(
        self, 
        sim_context_builder: SimulationContextBuilder
    ) -> None:
        pc = PipelineConfiguration()
        builder: RenderingPipelineBuilder = LandscapeRendererBuilder() 
        render_pipeline = builder.build(sim_context_builder, pc)
        renderer: GPURenderer = LandscapeRenderer(render_pipeline)
        sim_context_builder.renderers['landscape_renderer'] = renderer

    def _prepare_normals_renderer(
        self, 
        sim_context_builder: SimulationContextBuilder
    ) -> None:
        pc = PipelineConfiguration()
        builder: RenderingPipelineBuilder = NormalsRendererBuilder()
        render_pipeline = builder.build(sim_context_builder, pc)
        renderer: GPURenderer = NormalsRenderer(render_pipeline)
        sim_context_builder.renderers['normals_renderer'] = renderer

    # def _prepare_agent_renderers(
    #     self, 
    #     sim_context_builder: SimulationContextBuilder
    # ) -> None:
    #     """
    #     Create a renderer for each agent definition. Note: That there may not be any
    #     agents for a specific agent definition as agents can be added dynamically
    #     while the simulation is running.

    #     Questions: 
    #     What if I put the renderer on the MeshData instance?
    #     I don't think I like that. For example, the landscape is rendered
    #     with two different rendering pipelines. One for the mesh and one
    #     for the normals.

    #     Probably, need the renderers to be fairly static in their place
    #     in the larger pipeline and move the MeshData instances to the correct
    #     renderers.

    #     Alternatively, I could treat MeshData like a bit of a scene graph.
    #     With that approach, I could "tag" MeshData instances with what renderers
    #     they need to be applied. Other tags could be used to filter out things
    #     like "render_normals", "visible", "selected", "agents" vs "entities", etc.

    #     This harkens back to kinda how the Scene worked in the 2D engine.
    #     To do that approach, I would need to make MeshRegistry be a bit more
    #     sophisticated than just a dict.
    #     """
    #     self._agent_renderers = [] # TODO: Move this to the SimulationContextBuilders...

    #     for agent_def_alias in sim_context_builder.scene.agent_definitions:
    #         renderer = AgentRenderer()
    #         renderer.prepare(sim_context_builder)
    #         self._agent_renderers.append(renderer)

    # def _prepare_overlays(
    #     self,
    #     sim_context_builder: SimulationContextBuilder
    # ) -> None:
    #     self._overlay.prepare(sim_context_builder)
        
    def _handle_key_pressed(self, event: wx.Event) -> None:
        """
        Handle when a user presses a button on their keyboard.
        """
        # TODO: Migrate the key handling logic in agents_playground/terminal/keyboard/key_interpreter.py
        # TODO: Expand to handle more than just A/D/W/S keys.
        """
        EXPLANATION
        ASCII key codes use a single bit position between upper and lower case so
        x | 0x20 will force any key to be lower case.

        For example:
        A is 65 or 1000001
        32 -> 0x20 -> 100000
        1000001 | 100000 -> 1100001 -> 97 -> 'a'
        """
        key_str = chr(event.GetKeyCode() | 0x20)  # type: ignore

        # A/D are -/+ On on the X-Axis
        # S/W are -/+ On on the Z-Axis
        match key_str:  # type: ignore
            case "a":
                self._sim_context.scene.camera.position.i -= 1
                self._sim_context.scene.camera.update()
                print_camera(self._sim_context.scene.camera)
            case "d":
                self._sim_context.scene.camera.position.i += 1
                self._sim_context.scene.camera.update()
                print_camera(self._sim_context.scene.camera)
            case "w":
                self._sim_context.scene.camera.position.k += 1
                self._sim_context.scene.camera.update()
                print_camera(self._sim_context.scene.camera)
            case "s":
                self._sim_context.scene.camera.position.k -= 1
                self._sim_context.scene.camera.update()
                print_camera(self._sim_context.scene.camera)
            case "f":
                print_camera(self._sim_context.scene.camera)
            case _:
                pass
        self._sim_context.canvas.request_draw()

    def _provision_adapter(
        self, canvas: wgpu.gui.WgpuCanvasInterface
    ) -> wgpu.GPUAdapter:
        """
        Create a high performance GPUAdapter for a Canvas.
        """
        return wgpu.gpu.request_adapter(  # type: ignore
            canvas=canvas, power_preference="high-performance"
        )

    def _provision_gpu_device(self, adapter: wgpu.GPUAdapter) -> wgpu.GPUDevice:
        """
        Get an instance of the GPUDevice that is associated with a
        provided GPUAdapter.
        """
        return adapter.request_device(
            label="only-gpu-device",
            required_features=[],
            required_limits={},
            default_queue={},
        )

    @require_root
    def _update_hardware_metrics(self) -> None:
        """
        Retrieve the performance metrics from the performance monitoring process and 
        update the UI.
        """
        # Note: Not providing a value to Pipe.poll makes it return immediately.
        if not self._perf_receive_pipe.is_something():
            return
        
        pipe: Connection = self._perf_receive_pipe.unwrap()
        try:
            if pipe.readable and pipe.poll():
                metrics: PerformanceMetrics = pipe.recv()

                uptime = TimeUtilities.display_seconds(metrics.sim_running_time)
                print(uptime)
                msg: str = f"""
CPU:{metrics.cpu_utilization.latest:.2f}
USS: {metrics.memory_unique_to_process.latest:.2f} MB
RSS: {metrics.non_swapped_physical_memory_used.latest:.2f} MB
VMS: {metrics.virtual_memory_used.latest:.2f} MB
Page Faults: {metrics.page_faults.latest}
Pageins: {metrics.pageins.latest}
"""
                print(msg)
                """
                dpg.configure_item(
                    self._ui_components.time_running_widget_id, label=uptime
                )

                dpg.configure_item(
                    self._ui_components.cpu_util_widget_id,
                    label=f"CPU:{metrics.cpu_utilization.latest:.2f}",
                )

                dpg.set_value(
                    item=self._ui_components.cpu_util_plot_id,
                    value=metrics.cpu_utilization.samples,
                )

                dpg.configure_item(
                    self._ui_components.process_memory_used_widget_id,
                    label=f"USS: {metrics.memory_unique_to_process.latest:.2f} MB",
                )

                dpg.set_value(
                    item=self._ui_components.process_memory_used_plot_id,
                    value=metrics.memory_unique_to_process.samples,
                )

                dpg.configure_item(
                    self._ui_components.physical_memory_used_widget_id,
                    label=f"RSS: {metrics.non_swapped_physical_memory_used.latest:.2f} MB",
                )

                dpg.set_value(
                    item=self._ui_components.physical_memory_used_plot_id,
                    value=metrics.non_swapped_physical_memory_used.samples,
                )

                dpg.configure_item(
                    self._ui_components.virtual_memory_used_widget_id,
                    label=f"VMS: {metrics.virtual_memory_used.latest:.2f} MB",
                )

                dpg.set_value(
                    item=self._ui_components.virtual_memory_used_plot_id,
                    value=metrics.virtual_memory_used.samples,
                )

                dpg.configure_item(
                    self._ui_components.page_faults_widget_id,
                    label=f"Page Faults: {metrics.page_faults.latest}",
                )

                dpg.set_value(
                    item=self._ui_components.page_faults_plot_id,
                    value=metrics.page_faults.samples,
                )

                dpg.configure_item(
                    self._ui_components.pageins_widget_id,
                    label=f"Pageins: {metrics.pageins.latest}",
                )

                dpg.set_value(
                    item=self._ui_components.pageins_plot_id,
                    value=metrics.pageins.samples,
                )
                """
        except EOFError as e:
            logger.error(PERF_MONITOR_ERROR_MSG)
            logger.error(e)
            traceback.print_exception(e)
    
    def _update_frame_performance_metrics(self) -> None:
        per_frame_samples: dict[str, SamplesDistribution] = self._sim_context.stats.per_frame_samples
        metrics: list[list] = []
        if "frame-tick" in per_frame_samples:
            metrics.append(['Frame Processing'] + per_frame_samples["frame-tick"].stats_as_list())
        
        if "running-tasks" in per_frame_samples:
            metrics.append(['Running Tasks'] + per_frame_samples["running-tasks"].stats_as_list())
        
        log_table(
            header  = ["Metric", "Per Second", "# Samples", "Average", "Minimum", "P25", "P50", "P75", "Maximum"], 
            rows    = metrics,
            message = 'Performance Metrics',
        )

    def _update_fps(self) -> None:
        per_frame_samples: dict[str, SamplesDistribution] = self._sim_context.stats.per_frame_samples
        metrics: list[list] = []

        if "draw_frame" in per_frame_samples:
            metrics.append(['Draw Frame'] + per_frame_samples["draw_frame"].stats_as_list())

        log_table(
            header  = ["Metric", "Per Second", "# Samples", "Average", "Minimum", "P25", "P50", "P75", "Maximum"], 
            rows    = metrics,
            message = 'Frames per Second',
        )