from dataclasses import dataclass
from typing import Any

from wgpu import GPUDevice, GPUBuffer, GPUBindGroup
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.fp import Maybe, Something, wrap
from agents_playground.scene import Scene
from agents_playground.simulation.statistics import SimulationStatistics
from agents_playground.spatial.mesh import MeshRegistry
from agents_playground.sys.logger import get_default_logger, log_call

logger = get_default_logger()


class Uniform:
    """Represents a uniform for rendering pipeline."""

    def __init__(
        self, buffer: GPUBuffer | None = None, bind_group: GPUBindGroup | None = None
    ) -> None:
        self._buffer: Maybe[GPUBuffer] = wrap(buffer)
        self._bind_group: Maybe[GPUBindGroup] = wrap(bind_group)

    @property
    def buffer(self) -> Maybe[GPUBuffer]:
        return self._buffer

    @buffer.setter
    def buffer(self, other: GPUBuffer) -> None:
        self._buffer = Something(other)

    @property
    def bind_group(self) -> Maybe[GPUBindGroup]:
        return self._bind_group

    @bind_group.setter
    def bind_group(self, other: GPUBindGroup) -> None:
        self._bind_group = Something(other)


class UniformRegistryError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UniformRegistry:
    def __init__(self) -> None:
        self._uniforms: dict[str, Uniform] = {}

    def register(
        self,
        label: str,
        buffer: GPUBuffer | None = None,
        bind_group: GPUBindGroup | None = None,
    ) -> None:
        if label in self._uniforms:
            if buffer:
                self._uniforms[label].buffer = buffer
            if bind_group:
                self._uniforms[label].bind_group = bind_group
        else:
            self._uniforms[label] = Uniform(buffer, bind_group)

    def __len__(self) -> int:
        return len(self._uniforms)

    def __contains__(self, key: str) -> bool:
        return key in self._uniforms

    def __getitem__(self, key: str) -> Uniform:
        return self._uniforms[key]


@dataclass(init=False)
class SimulationContext:
    # General Simulation Stuff
    scene: Scene
    stats: SimulationStatistics

    # Top level GPU components
    canvas: WgpuWidget
    render_texture_format: str
    device: GPUDevice

    mesh_registry: MeshRegistry
    uniforms: UniformRegistry

    # Overlay needs to become a GPURender
    # overlay: Overlay

    # This stuff needs to be encapsulated as MeshData and stored in the
    # MeshRegistry...
    # overlay_buffers: dict[str, GPUBuffer]
    # overlay_bind_groups: dict[int, GPUBindGroup]

    # need to track things like the number of primitives to draw
    # for specific things.
    # Perhaps stuff this in MeshRegistry or have a configuration dict[str, int]?
    # Perhaps this should be inferred from the scene graph?
    # landscape_num_primitives: int
    # normals_num_primitives: int

    # Shove these in MeshRegistry...
    # display_config_buffer: GPUBuffer
    # camera_buffer: GPUBuffer

    # Replaces "details" from the 2D Sim Context.
    # This is intended for simulations to stuff things that are
    # simulation specific.
    extensions: dict[Any, Any]

    @log_call()
    def __init__(
        self,
        scene: Scene,
        canvas: WgpuWidget,
        render_texture_format: str,
        device: GPUDevice,
        mesh_registry: MeshRegistry,
        extensions: dict[Any, Any],
        uniforms: UniformRegistry,
    ) -> None:
        self.stats = SimulationStatistics()
        self.scene = scene
        self.render_texture_format = render_texture_format
        self.canvas = canvas
        self.device = device
        self.mesh_registry = mesh_registry
        self.extensions = extensions
        self.uniforms = uniforms

    @log_call()
    def __del__(self) -> None:
        pass

    def purge(self) -> None:
        self.extensions.clear()
        self.mesh_registry.clear()
