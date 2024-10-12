from wgpu.gui.wx import WgpuWidget
from wgpu import GPUCanvasContext, GPUTexture

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=WgpuWidget, name="canvas")
@task_output(type=GPUTexture, name="texture_target")
@task()
def set_texture_target(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    canvas: WgpuWidget = inputs.canvas
    canvas_context: GPUCanvasContext = canvas.get_context()
    current_texture: GPUTexture = canvas_context.get_current_texture()
    task_graph.provision_resource("texture_target", instance=current_texture)
