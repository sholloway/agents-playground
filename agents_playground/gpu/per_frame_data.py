from dataclasses import dataclass, field

import wgpu
import wgpu.backends.wgpu_native


@dataclass
class PerFrameData:
    """
    Data class for grouping the things that can be updated by the client.
    """

    # Landscape Stuff
    landscape_num_primitives: int = -1

    # Normals Rendering Stuff
    normals_num_primitives: int = -1

    # HUD
    overlay_buffers: dict[str, wgpu.GPUBuffer] = field(default_factory=dict)
    overlay_bind_groups: dict[int, wgpu.GPUBindGroup] = field(default_factory=dict)

    # Scene
    display_config_buffer: wgpu.GPUBuffer | None = None
    # model_world_transform_buffer: wgpu.GPUBuffer | None = None

    # Camera
    camera_buffer: wgpu.GPUBuffer | None = None

    # Agents

    def __repr__(self) -> str:
        msg = f"""
    PerFrameData
    Number of Primitives: {self.landscape_num_primitives}
    Camera Buffer {self.camera_buffer}
    Display Config Buffer {self.display_config_buffer}
    """
        return msg
