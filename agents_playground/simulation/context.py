from dataclasses import dataclass, field
from typing import Any, cast

import wgpu
from wgpu import GPUDevice, GPUBuffer, GPUBindGroup
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.agents.spec.agent_spec import AgentStyleLike
from agents_playground.core.types import Size
from agents_playground.fp import Maybe, Something, wrap
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.scene import Scene
from agents_playground.simulation.statistics import SimulationStatistics
from agents_playground.spatial.mesh import MeshRegistry
from agents_playground.sys.logger import get_default_logger, log_call

logger = get_default_logger()


class Uniform:
    """Represents a uniform for rendering pipeline."""
    def __init__(
        self, 
        buffer: GPUBuffer | None = None, 
        bind_group: GPUBindGroup | None = None
    ) -> None:
        self._buffer: Maybe[GPUBuffer] = wrap(buffer)
        self._bind_group: Maybe[GPUBindGroup] = wrap(bind_group)

    @property
    def buffer(self) -> Maybe[GPUBuffer]:
        return self._buffer
    
    @property
    def bind_group(self) -> Maybe[GPUBindGroup]:
        return self._bind_group
    
    @buffer.setter
    def buffer(self, other: GPUBuffer) -> None:
        self._buffer = Something(other)
    
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
        bind_group: GPUBindGroup | None = None) -> None:
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
    
    # Rendering Pipelines
    # Ultimately, I need to get to a place were the draw function 
    # just loops over the renders. Or... The draw function can 
    # be replaced by Sims. (e.g. Support Forward vs Deferred Rendering)
    renderers: dict[str, GPURenderer]
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

    @log_call
    def __init__(self, 
        scene: Scene, 
        canvas: WgpuWidget,
        render_texture_format: str,
        device: GPUDevice, 
        renderers: dict[str, GPURenderer],
        mesh_registry: MeshRegistry,
        extensions: dict[Any, Any],
        uniforms: UniformRegistry
    ) -> None:
        self.stats = SimulationStatistics()
        self.scene = scene
        self.render_texture_format = render_texture_format
        self.canvas = canvas
        self.device = device
        self.renderers = renderers
        self.mesh_registry = mesh_registry
        self.extensions = extensions
        self.uniforms = uniforms

    @log_call
    def __del__(self) -> None:
        pass

    def purge(self) -> None:
        self.extensions.clear()
        self.mesh_registry.clear()
        self.renderers.clear()

class SimulationContextBuilder:
    """
    Used to construct a simulation context.
    This prevents having to have Maybe or nullable fields on the 
    SimulationContext object.
    """
    
    def __init__(self, 
        scene: Scene | None = None,
        canvas: WgpuWidget | None = None,
        render_texture_format: str | None = None,
        device: GPUDevice | None = None,
        renderers: dict[str, GPURenderer] | None = None,
        mesh_registry: MeshRegistry | None = None,
        extensions: dict[Any, Any] | None = None,
        uniforms: UniformRegistry | None = None,
    ) -> None:
        self._scene: Maybe[Scene] = wrap(scene)
        self._canvas: Maybe[WgpuWidget] = wrap(canvas)
        self._render_texture_format: Maybe[str] = wrap(render_texture_format)
        self._device: Maybe[GPUDevice] = wrap(device)
        self._renderers: Maybe[dict[str, GPURenderer]] = wrap(renderers)
        self._mesh_registry: Maybe[MeshRegistry] = wrap(mesh_registry)
        self._extensions: Maybe[dict[Any, Any]] = wrap(extensions)
        self._uniforms: Maybe[UniformRegistry] = wrap(uniforms)

    def _error_msg(self, context: str) -> str:
        return f"The {context} attribute hasn't been set on the simulation context builder."
        
    @property
    def scene(self) -> Scene:
        return self._scene.unwrap_or_throw(self._error_msg('scene'))
    
    @property
    def canvas(self) -> WgpuWidget:
        return self._canvas.unwrap_or_throw(self._error_msg('canvas'))
    
    @property
    def render_texture_format(self) -> str:
        return self._render_texture_format.unwrap_or_throw(self._error_msg('render_texture_format'))
    
    @property
    def device(self) -> GPUDevice:
        return self._device.unwrap_or_throw(self._error_msg('device'))
    
    @property
    def renderers(self) -> dict[str, GPURenderer]:
        return self._renderers.unwrap_or_throw(self._error_msg('renderers'))
    
    @property
    def mesh_registry(self) -> MeshRegistry:
        return self._mesh_registry.unwrap_or_throw(self._error_msg('mesh_registry'))
    
    @property
    def extensions(self) -> dict[Any, Any]:
        return self._extensions.unwrap_or_throw(self._error_msg('extensions'))
    
    @property
    def uniforms(self) -> UniformRegistry:
        return self._uniforms.unwrap_or_throw(self._error_msg('uniforms'))
    
    @scene.setter
    def scene(self, other: Scene) -> None:
        self._scene = Something(other)
    
    @canvas.setter
    def canvas(self, other: WgpuWidget) -> None:
        self._canvas = Something(other)
    
    @render_texture_format.setter
    def render_texture_format(self, other: str) -> None:
        self._render_texture_format = Something(other)
    
    @device.setter
    def device(self, other: GPUDevice) -> None:
        self._device = Something(other)
    
    @renderers.setter
    def renderers(self, other: dict[str, GPURenderer]) -> None:
        self._renderers = Something(other)
    
    @mesh_registry.setter
    def mesh_registry(self, other: MeshRegistry) -> None:
        self._mesh_registry = Something(other)
    
    @extensions.setter
    def extensions(self, other: dict[Any, Any]) -> None:
        self._extensions = Something(other)
    
    @uniforms.setter
    def uniforms(self, other: UniformRegistry) -> None:
        self._uniforms = Something(other)
    
    def is_ready(self) -> bool:
        """Returns True if all fields are set."""
        items_set = [item.is_something() for item in self.__dict__.values()]
        return all(items_set)

    def create_context(self) -> SimulationContext:
        return SimulationContext(
            scene = self.scene, 
            canvas = self.canvas,
            render_texture_format = self.render_texture_format,
            device = self.device,
            renderers = self.renderers,
            mesh_registry = self.mesh_registry,
            extensions = self.extensions,
            uniforms=self.uniforms
        ) 