from wgpu.gui.wx import WgpuWidget

from agents_playground.core.webgpu_sim_loop import WGPUSimLoop
from agents_playground.gpu.task_driven_renderer import TaskDrivenRenderer
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.sim_state import SimulationState
from agents_playground.tasks.graph.detailed_task_graph_sampler import (
    DetailedTaskGraphSampler,
)
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    SimulationTasks,
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=WgpuWidget, name="canvas")
@task_input(type=SimulationTasks, name="simulation_tasks")
@task_input(type=SimulationContext, name="simulation_context")
@task_output(type=WGPUSimLoop, name="sim_loop")
@task_output(type=TaskDrivenRenderer, name="task_renderer")
@task(pin_to_main_thread=True)
def start_simulation_loop(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:

    simulation_tasks: SimulationTasks = inputs.simulation_tasks
    sim_context: SimulationContext = inputs.simulation_context
    canvas: WgpuWidget = inputs.canvas

    # Create the top level renderer and bind it to the canvas.
    task_renderer = TaskDrivenRenderer(
        task_graph=task_graph,
        render_tasks=simulation_tasks.render_tasks,
        snapshot_sampler=DetailedTaskGraphSampler(),
    )
    canvas.request_draw(task_renderer.render)

    sim_loop = WGPUSimLoop(
        window=canvas, per_frame_tasks=simulation_tasks.per_frame_tasks
    )

    # Track the outputs
    outputs.task_renderer = task_renderer
    outputs.sim_loop = sim_loop

    # Start the simulation loop. Note that this spins up a new thread.
    sim_loop.simulation_state = SimulationState.RUNNING
    sim_loop.start(sim_context)
