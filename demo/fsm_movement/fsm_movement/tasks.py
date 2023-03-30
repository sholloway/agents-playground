from math import copysign, radians
from typing import cast, Generator, Tuple

from agents_playground.agents.direction import Vector2d
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.core.types import Coordinate
from agents_playground.paths.circular_path import CirclePath
from agents_playground.project.extensions import register_task
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

@register_task(label = 'agent_traverse_circular_path')
def agent_traverse_circular_path(*args, **kwargs) -> Generator:
  """A task that moves an agent along a circular path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - starting_degree: Where on the circle to start the animation.
  """
  logger.info('Task: agent_traverse_circular_path - Initializing Task')
  scene: Scene = kwargs['scene']
  agent_id: Tag = kwargs['agent_id']
  path_id = kwargs['path_id']
  active_t: float = kwargs['starting_degree'] # In the range of [0, 2*pi]
  speed: float = kwargs['speed'] 
  direction = int(copysign(1, speed))

  agent: AgentLike = scene.agents[agent_id]
  path: CirclePath = cast(CirclePath, scene.paths[path_id])
  
  max_degree = 360
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_t)
      agent.move_to(Coordinate(pt[0], pt[1]), scene.cell_size)
      tangent_vector: Vector2d = path.tangent(pt, direction)
      agent.face(tangent_vector)

      active_t += speed
      if active_t > max_degree:
        active_t = 0
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_circular_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_circular_path - Task Completed')