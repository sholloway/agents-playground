from wgpu import GPURenderPassEncoder

from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.spatial.mesh import MeshData
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=MeshData, name="landscape_tri_mesh")
@task_input(type=GPURenderer, name="landscape_renderer")
@task_input(type=GPURenderPassEncoder, name="render_pass_encoder")
@task()
def render_landscape(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Render the landscape to the active render pass."""
    # Set the landscape rendering pipe line as the active one.
    # Encode the landscape drawing instructions.
    landscape_renderer: GPURenderer = inputs.landscape_renderer
    render_pass_encoder: GPURenderPassEncoder = inputs.render_pass_encoder
    landscape_tri_mesh: MeshData = inputs.landscape_tri_mesh

    render_pass_encoder.set_pipeline(landscape_renderer.render_pipeline)
    landscape_renderer.render(render_pass_encoder, landscape_tri_mesh)
