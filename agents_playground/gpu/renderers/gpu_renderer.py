from abc import abstractmethod
from typing import Protocol

import wgpu
import wgpu.backends.wgpu_native

from agents_playground.spatial.mesh import MeshData

class GPURendererException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class GPURenderer(Protocol):
    @property
    @abstractmethod
    def render_pipeline(self) -> wgpu.GPURenderPipeline: ...

    @abstractmethod
    def render(
        self,
        render_pass: wgpu.GPURenderPassEncoder,
        mesh_data: MeshData,
    ) -> None: ...
