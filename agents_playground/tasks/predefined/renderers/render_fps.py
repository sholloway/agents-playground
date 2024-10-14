import wgpu
from wgpu import GPURenderPassEncoder

from agents_playground.gpu.renderers.gpu_renderer import GPURenderer

from agents_playground.spatial.mesh import MeshData
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import TaskGraphLike, TaskInputs, TaskOutputs

# fmt: off
@task_input(type=MeshData,             name="fps_text_data")
@task_input(type=GPURenderer,          name="fps_text_renderer")
@task_input(type=GPURenderPassEncoder, name="render_pass_encoder")
@task()
def render_fps(
    task_graph: TaskGraphLike, 
    inputs: TaskInputs, 
    outputs: TaskOutputs
) -> None:
# fmt: on
    fps_text_data: MeshData = inputs.fps_text_data
    fps_text_renderer: GPURenderer  = inputs.fps_text_renderer
    render_pass_encoder: GPURenderPassEncoder = inputs.render_pass_encoder

    render_pass_encoder.set_pipeline(fps_text_renderer.render_pipeline)
    fps_text_renderer.render(render_pass_encoder, fps_text_data)
