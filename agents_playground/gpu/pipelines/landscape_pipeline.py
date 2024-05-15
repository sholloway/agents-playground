from functools import partial
from math import radians
import os
from pathlib import Path

import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.landscape_renderer import LandscapeRenderer
from agents_playground.loaders.obj_loader import Obj, ObjLoader

from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.mesh import MeshBuffer


class LandscapePipeline(WebGpuPipeline):
    """
    Establishes a GPU rendering pipeline for visualizing an OBJ model.
    """

    def __init__(self) -> None:
        super().__init__()
        self._landscape_mesh: MeshBuffer
        self._camera: Camera

    @property
    def mesh(self) -> MeshBuffer:
        return self._landscape_mesh

    @mesh.setter
    def mesh(self, other: MeshBuffer) -> None:
        self._landscape_mesh = other

    @property
    def camera(self) -> Camera:
        return self._camera

    @camera.setter
    def camera(self, other: Camera) -> None:
        self._camera = other

    def initialize_pipeline(self, canvas: WgpuWidget) -> None:
        # Initialize WebGPU
        adapter: wgpu.GPUAdapter = self._provision_adapter(canvas)
        device: wgpu.GPUDevice = self._provision_gpu_device(adapter)
        canvas_context: wgpu.GPUCanvasContext = canvas.get_context()

        # Enable Tracing
        # wgpu.backends.wgpu_native.request_device_tracing(adapter, './wgpu_traces')

        # Set the GPUCanvasConfiguration to control how drawing is done.
        render_texture_format = canvas_context.get_preferred_format(device.adapter)
        canvas_context.configure(
            device=device,
            usage=wgpu.flags.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
            format=render_texture_format,
            view_formats=[],
            color_space="bgra8unorm-srgb",
            alpha_mode="opaque",
        )

        # Setup the Transformation Model.
        model_world_transform = Matrix4x4.identity()

        # Setup the Renderer
        renderer: GPURenderer = LandscapeRenderer()

        # Prepare the per-frame data.
        frame_data: PerFrameData = renderer.prepare(
            device,
            render_texture_format,
            self._landscape_mesh,
            self._camera,
            model_world_transform,
        )

    def refresh_aspect_ratio(self, aspect_ratio: float) -> None:
        # self._camera.projection_matrix = Matrix4x4.perspective(
        #     aspect_ratio= aspect_ratio,
        #     v_fov = radians(72.0),
        #     near = 0.1,
        #     far = 100.0
        #   )
        # self._bound_update_uniforms()
        # Throwing an error at the moment because I don't think this is actually needed.
        raise NotImplementedError()

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

    def _select_model(self) -> str:
        """
        Find the path for the desired scene.
        """
        scene_dir = "poc/pyside_webgpu/pyside_webgpu/demos/obj/models"
        scene_filename = "skull.obj"
        return os.path.join(Path.cwd(), scene_dir, scene_filename)

    def _parse_model_file(self, scene_file_path: str) -> Obj:
        return ObjLoader().load(scene_file_path)
