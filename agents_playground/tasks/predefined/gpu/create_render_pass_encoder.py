from wgpu import GPUCommandEncoder, GPURenderPassEncoder

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=GPUCommandEncoder, name="command_encoder")
@task_input(type=dict, name="color_attachment")
@task_input(type=dict, name="depth_stencil_attachment")
@task_output(type=GPURenderPassEncoder, name="render_pass_encoder")
@task()
def create_render_pass_encoder(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Encode the drawing instructions."""
    command_encoder: GPUCommandEncoder = inputs.command_encoder
    color_attachment: dict = inputs.color_attachment
    depth_stencil_attachment: dict = inputs.depth_stencil_attachment

    # The first command to encode is the instruction to do a rendering pass.
    render_pass_encoder: GPURenderPassEncoder = command_encoder.begin_render_pass(
        label="Draw Frame Render Pass",
        color_attachments=[color_attachment],
        depth_stencil_attachment=depth_stencil_attachment,
        occlusion_query_set=None,  # type: ignore
        timestamp_writes=None,
        max_draw_count=50_000_000,  # Default
    )
    outputs.render_pass_encoder = render_pass_encoder
