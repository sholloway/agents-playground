from agents_playground.loaders.scene_loader import SceneLoader
from agents_playground.scene import Scene
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import TaskGraphLike, TaskInputs, TaskOutputs


@task_input(type=str, name="scene_file_path")
@task_output(type=Scene, name="scene")
@task()
def load_scene(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    """
    A task that is responsible for parsing the provided scene file.

    Effects:
    - The JSON scene file that is provided as an input is parsed.
    - The resulting Scene instance is allocated as an output.
    """
    # Load the Scene.
    scene_loader = SceneLoader()
    scene: Scene = scene_loader.load(inputs.scene_file_path)

    # Allocate the task outputs.
    outputs.scene = scene
