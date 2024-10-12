from fractions import Fraction
from math import radians

from agents_playground.fp import Something
from agents_playground.scene import Scene
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.tasks.register import task, task_input, task_output
from agents_playground.tasks.types import (
    TaskGraphLike,
    TaskInputs,
    TaskOutputs,
)


@task_input(type=Scene, name="scene")
@task_input(type=Fraction, name="aspect_ratio")
@task()
def construct_projection_matrix(
    task_graph: TaskGraphLike, inputs: TaskInputs, outputs: TaskOutputs
) -> None:
    scene: Scene = inputs.scene

    aspect_ratio: Fraction = inputs.aspect_ratio

    scene.camera.projection_matrix = Something(
        Matrix4x4.perspective(
            aspect_ratio=aspect_ratio, v_fov=radians(72.0), near=0.1, far=100.0
        )
    )
