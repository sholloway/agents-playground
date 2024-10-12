from wgpu import GPUTexture

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=GPUTexture, name="depth_texture")
@task_output(type=dict, name="depth_stencil_attachment")
@task()
def create_depth_stencil_attachment(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Create a depth stencil attachment."""
    depth_texture: GPUTexture = inputs.depth_texture

    depth_texture_view = depth_texture.create_view()
    depth_stencil_attachment = {
        "view": depth_texture_view,
        "depth_clear_value": 1.0,
        "depth_load_op": wgpu.LoadOp.clear,  # type: ignore
        "depth_store_op": wgpu.StoreOp.store,  # type: ignore
        "depth_read_only": False,
        # I'm not sure about these values.
        "stencil_clear_value": 0,
        "stencil_load_op": wgpu.LoadOp.load,  # type: ignore
        "stencil_store_op": wgpu.StoreOp.store,  # type: ignore
        "stencil_read_only": False,
    }

    outputs.depth_stencil_attachment = depth_stencil_attachment
