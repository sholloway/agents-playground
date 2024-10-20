import wgpu
from wgpu import GPUDevice
from wgpu.gui.wx import WgpuWidget

from agents_playground.scene import Scene
from agents_playground.simulation.context import SimulationContext, UniformRegistry
from agents_playground.spatial.mesh import MeshRegistry
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    SimulationPhase,
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


# fmt: off
@task_input( type=Scene,             name="scene")
@task_input( type=WgpuWidget,        name="canvas")
@task_input( type=str,               name="render_texture_format")
@task_input( type=GPUDevice,         name="gpu_device")
@task_output(type=SimulationContext, name="simulation_context", release_on=SimulationPhase.ON_SHUTDOWN)
@task()
# fmt: on
# TODO: Re-evaluate if the engine still needs a simulation context.
# It might make sense to have a FrameContext.
def create_simulation_context(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    # Get the inputs

    scene: Scene = inputs.scene
    canvas: WgpuWidget = inputs.canvas
    render_texture_format: str = inputs.render_texture_format
    device: GPUDevice = inputs.gpu_device

    sc = SimulationContext(
        scene=scene,
        canvas=canvas,
        render_texture_format=render_texture_format,
        device=device,
        mesh_registry=MeshRegistry(),
        extensions={},
        uniforms=UniformRegistry(),
    )

    # Register the output
    outputs.simulation_context = sc
