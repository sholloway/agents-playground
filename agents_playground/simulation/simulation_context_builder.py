from typing import Any

from wgpu import GPUDevice
from wgpu.gui.wx import WgpuWidget

from agents_playground.fp import Maybe, Something, wrap
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.scene import Scene
from agents_playground.simulation.context import SimulationContext, UniformRegistry
from agents_playground.spatial.mesh import MeshRegistry

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
            mesh_registry = self.mesh_registry,
            extensions = self.extensions,
            uniforms=self.uniforms
        ) 