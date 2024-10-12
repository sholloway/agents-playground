from wgpu import GPUDevice, GPUTexture

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=GPUDevice, name="gpu_device")
@task_input(type=GPUTexture, name="texture_target")
@task_output(type=GPUTexture, name="depth_texture")
@task()
def create_depth_texture(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Create a depth texture for the Z-Buffer."""
    device: GPUDevice = inputs.gpu_device
    current_texture: GPUTexture = inputs.texture_target
    depth_texture: GPUTexture = device.create_texture(
        label="Z Buffer Texture",
        size=current_texture.size,
        usage=wgpu.TextureUsage.RENDER_ATTACHMENT,  # type: ignore
        format=wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
    )

    task_graph.provision_resource("depth_texture", instance=depth_texture)
