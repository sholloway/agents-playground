from abc import abstractmethod
from typing import Protocol

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.gpu.per_frame_data import PerFrameData

from agents_playground.scene import Scene
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.mesh import MeshData


class GPURendererException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GPURenderer(Protocol):
    @property
    @abstractmethod
    def render_pipeline(self) -> wgpu.GPURenderPipeline: ...

    @abstractmethod
    def prepare(
        self,
        device: wgpu.GPUDevice,
        render_texture_format: str,
        mesh_data: MeshData,
        scene: Scene,
        frame_data: PerFrameData,
    ) -> PerFrameData: ...

    @abstractmethod
    def render(
        self,
        render_pass: wgpu.GPURenderPassEncoder,
        frame_data: PerFrameData,
        mesh_data: MeshData,
    ) -> None: ...
