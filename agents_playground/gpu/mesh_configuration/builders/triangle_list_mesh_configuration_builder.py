from array import array as create_array
from typing import Dict, List

import wgpu
import wgpu.backends.wgpu_native


class TriangleListMeshConfigurationBuilder:
    def __init__(self, prefix: str) -> None:
        self._prefix = prefix

    def configure_pipeline_primitives(self) -> Dict:
        """
        Specify what type of geometry should the GPU render.
        Returns a structs.PrimitiveState
        """
        primitive_config = {
            "topology": wgpu.PrimitiveTopology.triangle_list,  # type: ignore
            "front_face": wgpu.FrontFace.ccw,  # type: ignore Note, that the OBJ spec lists verts in ccw order.
            "cull_mode": wgpu.CullMode.none,  # type: ignore
        }
        return primitive_config

    def create_vertex_buffer(
        self, device: wgpu.GPUDevice, vertices: List[float]
    ) -> wgpu.GPUBuffer:
        vbo_data = create_array("f", vertices)
        return device.create_buffer_with_data(
            label=f"{self._prefix} Vertex Buffer",
            data=vbo_data,
            usage=wgpu.BufferUsage.VERTEX,  # type: ignore
        )

    def create_vertex_normals_buffer(
        self, device: wgpu.GPUDevice, normals: List[float]
    ) -> wgpu.GPUBuffer:
        vertex_normals_data = create_array("f", normals)
        return device.create_buffer_with_data(
            label=f"{self._prefix} Vertex Normals Buffer",
            data=vertex_normals_data,
            usage=wgpu.BufferUsage.VERTEX,  # type: ignore
        )

    def create_index_buffer(
        self, device: wgpu.GPUDevice, indices: List[int]
    ) -> wgpu.GPUBuffer:
        ibo_data = create_array("I", indices)
        return device.create_buffer_with_data(
            label=f"{self._prefix} Index Buffer",
            data=ibo_data,
            usage=wgpu.BufferUsage.INDEX,  # type: ignore
        )
