print("Loading agents_playground.tasks.predefined.bootstrap")
import logging

from agents_playground.scene import Scene
from agents_playground.simulation.simulation_context_builder import (
    SimulationContextBuilder,
)
from agents_playground.spatial.mesh import MeshData
from agents_playground.sys.logger import get_default_logger
from agents_playground.tasks.register import task, task_input, task_output

logger: logging.Logger = get_default_logger()


@task_output(type=Scene, name="scene")
@task()
def load_scene(scene_path: str) -> None:
    logger.info("Running load_scene task.")


@task_input(type=Scene, name="scene")
@task_output(type=MeshData, name="landscape")
@task_output(type=MeshData, name="landscape_tri_mesh")
@task(require_before=["load_scene"])
def load_landscape_mesh(sim_context_builder: SimulationContextBuilder) -> None:
    logger.info("Running load_landscape_mesh task.")


@task(require_before=["load_landscape_mesh"])
def initialize_graphics_pipeline(
    sim_context_builder: SimulationContextBuilder,
) -> None:
    logger.info("Running initialize_graphics_pipeline task.")


@task(require_before=["initialize_graphics_pipeline"])
def prepare_landscape_renderer(
    sim_context_builder: SimulationContextBuilder,
) -> None:
    logger.info("Running initialize_graphics_pipeline task.")
