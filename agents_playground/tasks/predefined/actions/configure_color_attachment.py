import wgpu
from wgpu import GPUTexture

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    SimulationPhase,
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=GPUTexture, name="texture_target")
@task_output(
    type=dict, name="color_attachment", release_on=SimulationPhase.END_OF_FRAME
)
@task()
def configure_color_attachment(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Build a render pass color attachment."""
    current_texture: GPUTexture = inputs.texture_target

    # struct.RenderPassColorAttachment
    color_attachment = {
        "view": current_texture.create_view(),
        "resolve_target": None,
        "clear_value": (0.9, 0.5, 0.5, 1.0),  # Clear to pink.
        "load_op": wgpu.LoadOp.clear,  # type: ignore
        "store_op": wgpu.StoreOp.store,  # type: ignore
    }

    outputs.color_attachment = color_attachment
