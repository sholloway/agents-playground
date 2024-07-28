import wgpu
import wgpu.backends.wgpu_native

"""
For now, just get an overlay that is a solid color that is constrained to a fixed space.
"""
class Overlay:
    def __init__(self) -> None:
        self._render_pipeline: wgpu.GPURenderPipeline

    @property
    def render_pipeline(self) -> wgpu.GPURenderPipeline:
        return self._render_pipeline

    def prepare(self, device: wgpu.GPUDevice) -> None:
        pass 

    def render(self, render_pass: wgpu.GPURenderPassEncoder) -> None:
        pass




