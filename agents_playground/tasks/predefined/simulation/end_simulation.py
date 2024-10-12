from agents_playground.core.webgpu_sim_loop import WGPUSimLoop
from agents_playground.tasks.register import task, task_input
from agents_playground.tasks.types import TaskGraphLike, TaskInputs, TaskOutputs


@task_input(type=WGPUSimLoop, name="sim_loop")
@task(pin_to_main_thread=True)
def end_simulation(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    sim_loop: WGPUSimLoop = inputs.sim_loop
    sim_loop.end()
