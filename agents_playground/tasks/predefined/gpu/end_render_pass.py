from wgpu import GPUCommandEncoder, GPUDevice, GPURenderPassEncoder

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=GPUDevice, name="gpu_device")
@task_input(type=GPUCommandEncoder, name="command_encoder")
@task_input(type=GPURenderPassEncoder, name="render_pass_encoder")
@task(require_before=["render_landscape", "render_fps"])
def end_render_pass(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Submit the draw calls to the GPU."""
    device: GPUDevice = inputs.gpu_device
    render_pass_encoder: GPURenderPassEncoder = inputs.render_pass_encoder

    command_encoder: GPUCommandEncoder = inputs.command_encoder
    render_pass_encoder.end()
    device.queue.submit([command_encoder.finish()])
