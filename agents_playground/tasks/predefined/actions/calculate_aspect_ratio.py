from fractions import Fraction
from wgpu.gui.wx import WgpuWidget

from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    SimulationPhase,
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=WgpuWidget, name="canvas")
@task_output(
    type=Fraction, name="aspect_ratio", release_on=SimulationPhase.END_OF_FRAME
)
@task()
def calculate_aspect_ratio(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """Calculate the current aspect ratio."""
    canvas: WgpuWidget = inputs.canvas
    canvas_width, canvas_height = canvas.GetSize()
    aspect_ratio = Fraction(canvas_width, canvas_height)
    task_graph.provision_resource("aspect_ratio", instance=aspect_ratio)
