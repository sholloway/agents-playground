from wgpu import GPUCommandEncoder, GPUDevice

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    SimulationPhase,
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=GPUDevice, name="gpu_device")
@task_output(
    type=GPUCommandEncoder,
    name="command_encoder",
    release_on=SimulationPhase.END_OF_FRAME,
)
@task()
def create_gpu_encoder(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Create a GPU command encoder."""
    device: GPUDevice = inputs.gpu_device
    command_encoder: GPUCommandEncoder = device.create_command_encoder()
    outputs.command_encoder = command_encoder
