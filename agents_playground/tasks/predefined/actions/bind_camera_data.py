from fractions import Fraction
from wgpu import GPUBuffer, GPUDevice

from agents_playground.gpu.renderer_builders.renderer_builder import (
    assemble_camera_data,
)
from agents_playground.scene import Scene
from agents_playground.tasks.register import task, task_input
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=Scene, name="scene")
@task_input(type=GPUDevice, name="gpu_device")
@task_input(type=Fraction, name="aspect_ratio")
@task_input(type=GPUBuffer, name="camera_uniforms")
@task()
def bind_camera_data(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    scene: Scene = inputs.scene
    device: GPUDevice = inputs.gpu_device
    camera_uniforms: GPUBuffer = inputs.camera_uniforms

    camera_data = assemble_camera_data(scene.camera)
    device.queue.write_buffer(camera_uniforms, 0, camera_data)
