from math import copysign, radians
from typing import List
from typing import cast, Generator, Tuple

import dearpygui.dearpygui as dpg
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.paths.linear_path import LinearPath
from agents_playground.paths.circular_path import CirclePath
from agents_playground.project.extensions import register_renderer, register_task
from agents_playground.renderers.color import Color, PrimaryColors
from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext, Size
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector.vector2d import Vector2d

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

@register_renderer(label='line_segment_renderer')
def line_segment_renderer(path: LinearPath, cell_size: Size, offset: Size, closed_loop=True) -> None:
  """Can be attached to a LinearPath for rendering"""
  displayed_path: List[List[float]] = []
  for cp in path.control_points():
      point = [
        cp[0] * cell_size.width + offset.width, 
        cp[1] * cell_size.height + offset.height
      ]
      displayed_path.append(point)
  dpg.draw_polyline(displayed_path, color=PrimaryColors.red.value, closed=closed_loop)

@register_renderer(label='circular_path_renderer')
def circle_renderer(path: CirclePath, cell_size: Size, offset: Size) -> None:
  center = (
    path._center[0] * cell_size.width + offset.width, 
    path._center[1] * cell_size.height + offset.height, 
  )
  radius = path.radius * cell_size.width
  dpg.draw_circle(center, radius, color=PrimaryColors.red.value)

@register_task(label = 'agent_traverse_linear_path')
def agent_traverse_linear_path(*args, **kwargs) -> Generator:
  """A task that moves an agent along a path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - step_index: The starting point on the path.
  """
  logger.info('agent_traverse_linear_path: Starting task.')
  scene: Scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  speed: float = kwargs['speed'] 

  agent: AgentLike = scene.agents[agent_id]
  path: LinearPath = cast(LinearPath, scene.paths[path_id])
  segments_count = path.segments_count()
  active_path_segment: int = kwargs['step_index']
  active_t: float = 0 # In the range of [0,1]
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_path_segment, active_t)
      agent.move_to(Coordinate(pt[0], pt[1]), scene.cell_size)
      direction: Vector2d = path.direction(active_path_segment)
      agent.face(direction, scene.cell_size)

      active_t += speed
      if active_t > 1:
        active_t = 0
        active_path_segment = active_path_segment + 1 if active_path_segment < segments_count else 1
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_linear_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_linear_path - Task Completed')

@register_task(label = 'agent_traverse_circular_path')
def agent_traverse_circular_path(*args, **kwargs) -> Generator:
  """A task that moves an agent along a circular path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - starting_degree: Where on the circle to start the animation.
  """
  logger.info('agent_traverse_circular_path: Starting task.')
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
      agent.face(tangent_vector, scene.cell_size)

      active_t += speed
      if active_t > max_degree:
        active_t = 0
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_circular_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_circular_path - Task Completed')

@register_task(label = 'agent_pacing')
def agent_pacing(*args, **kwargs) -> Generator:
  logger.info('agent_pacing: Starting task.')
  scene: Scene = kwargs['scene']      
  agent_ids: Tuple[Tag, ...] = kwargs['agent_ids']
  path_id: Tag = kwargs['path_id']
  starting_segments: Tuple[int, ...] = kwargs['starting_segments']
  speeds: Tuple[float, ...] = kwargs['speeds']
  path: LinearPath = cast(LinearPath, scene.paths[path_id])
  segments_count = path.segments_count()
  explore_color: Color =  kwargs['explore_color']
  return_color: Color = kwargs['return_color']

  direction_color = { 1: explore_color, -1: return_color }

  # build a structure of the form: want = { 'id' : {'speed': 0.3, 'segment': 4}}
  values = list(map(lambda i: {'speed': i[0], 'segment': i[1], 'active_t': 0}, list(zip(speeds, starting_segments))))
  group_motion = dict(zip(agent_ids, values))

  try:
    while True:
      # Update each agent's location.
      for agent_id in group_motion:
        pt: Tuple[float, float] = path.interpolate(int(group_motion[agent_id]['segment']), group_motion[agent_id]['active_t'])
        scene.agents[agent_id].move_to(Coordinate(pt[0], pt[1]), scene.cell_size)
        group_motion[agent_id]['active_t'] += group_motion[agent_id]['speed']

        direction = int(copysign(1, group_motion[agent_id]['speed']))
        direction_vector: Vector2d = path.direction(int(group_motion[agent_id]['segment']))
        direction_vector = direction_vector.scale(direction)
        scene.agents[agent_id].face(direction_vector, scene.cell_size)
        
        # Handle moving an agent to the next line segment.
        """
        TODO: This is a good candidate for using polymorphism for handling 
        switching direction.
        Scenarios:
          - Going Forward, Reverse Required
          - Going Forward, Keep Going
          - Going Back, Reverse Required
          - Going Back, Keep Going
        """

        if group_motion[agent_id]['active_t'] < 0 or group_motion[agent_id]['active_t'] > 1:
          # End of the Line: The segment the agent is on has been exceeded. 
          # Need to go to the next segment or reverse direction.
          
          if direction == -1:
            if group_motion[agent_id]['segment'] <= 1:
              # Reverse Direction
              group_motion[agent_id]['active_t'] = 0
              group_motion[agent_id]['speed'] *= -1
              scene.agents[agent_id].style.fill_color = direction_color[-direction]
              scene.agents[agent_id].agent_state.require_render = True
            else:
              # Keep Going
              group_motion[agent_id]['active_t'] = 1
              group_motion[agent_id]['segment'] += direction
          else: 
            if group_motion[agent_id]['segment'] < segments_count:
              # Keep Going
              group_motion[agent_id]['active_t'] = 0
              group_motion[agent_id]['segment'] += direction
            else:
              # Reverse Direction
              group_motion[agent_id]['active_t'] = 1
              group_motion[agent_id]['speed'] *= -1
              scene.agents[agent_id].style.fill_color = direction_color[-direction]
              scene.agents[agent_id].agent_state.require_render = True
        
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_pacing - GeneratorExit')
  finally:
    logger.info('Task: agent_pacing - Task Completed')

@register_task(label = 'agents_spinning')
def agents_spinning(*args, **kwargs) -> Generator:
  """ Rotate a group of agents individually in place. 
        
  Rotation is done by updating the agent's facing direction at a given speed
  per frame.
  """  
  logger.info('agents_spinning: Starting task.')
  scene: Scene = kwargs['scene']      
  agent_ids: Tuple[Tag, ...] = kwargs['agent_ids']
  speeds: Tuple[float, ...] = kwargs['speeds']

  # build a structure of the form: want = { 'id' : {'speed': 0.3}
  values = list(map(lambda i: {'speed': i[0]}, list(zip(speeds))))
  group_motion = dict(zip(agent_ids, values))
  rotation_amount = radians(5)

  try:
    while True:
      agent_id: Tag
      for agent_id in agent_ids:
        rot_dir = int(copysign(1, group_motion[agent_id]['speed']))
        agent: AgentLike = scene.agents[agent_id]
        new_orientation = agent.position.facing.rotate(rotation_amount * rot_dir)
        agent.face(new_orientation, scene.cell_size)
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agents_spinning - GeneratorExit')
  finally:
    logger.info('Task: agents_spinning - Task Completed')