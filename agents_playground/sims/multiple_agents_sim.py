
from dataclasses import dataclass
import itertools
from typing import Dict, List, Optional, Tuple

import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction
from agents_playground.agents.path import CirclePath, LinearPath
from agents_playground.agents.structures import Point, Size
from agents_playground.agents.utilities import update_agent_in_scene_graph
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.core.task_based_simulation import TaskBasedSimulation
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.core.time_utilities import TIME_PER_FRAME, TimeInMS
from agents_playground.renderers.agent import render_agents_scene
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import (
  render_interpolated_paths, 
  line_segment_renderer, 
  circle_renderer
)
from agents_playground.renderers.scene import Scene
from agents_playground.sims.event_based_agents import FutureAction
from agents_playground.simulation.context import SimulationContext
from agents_playground.renderers.color import BasicColors
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

TIME_PER_STEP = TIME_PER_FRAME * 6

class MultipleAgentsSim(TaskBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    logger.info('MultipleAgentsSim: Initializing')
    self._sim_description = 'Multiple agents all moving around.'
    self._sim_instructions = 'Click the start button to begin the simulation.'
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    self._scene = Scene()
    self._setup_scene(self._scene)
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_interpolated_paths, 'Path')
    self.add_layer(render_agents_scene, 'Agents')
    
  def _setup_scene(self, scene: Scene) -> None:
    logger.info('MultipleAgentsSim: Setting up the scene')
    linear_path: LinearPath = self._create_path_a()
    scene.add_path(linear_path)

    # Have 4 agents on the same path (path_a), going the same direction.
    a1 = Agent(crest=BasicColors.aqua, id=dpg.generate_uuid())
    a2 = Agent(crest=BasicColors.magenta, id=dpg.generate_uuid())
    a3 = Agent(crest=BasicColors.fuchsia, id=dpg.generate_uuid())
    a4 = Agent(crest=BasicColors.olive, id=dpg.generate_uuid())

    # TODO Can the scene act as more of a DSL for building this stuff up?
    # This type of code shouldn't be in the MultipleAgentsSim class.
    scene.add_agent(a1)
    scene.add_agent(a2)
    scene.add_agent(a3)
    scene.add_agent(a4)

    # Looping Agents: Have four nested closed paths. Have the agents going 
    # in opposite directions and speeds.
    circle_path_a: CirclePath = CirclePath(
      id=dpg.generate_uuid(), 
      center=(40,5), 
      radius=4, 
      renderer=circle_renderer)
    scene.add_path(circle_path_a)

    a5 = Agent(crest=BasicColors.yellow, id=dpg.generate_uuid())

    # Add tasks for the agents on the linear path.
    self._task_scheduler.add_task(
      agent_traverse_linear_path, 
      [], 
      {
        'path_id': linear_path.id,
        'agent_id': a1.id,
        'step_index': 1,
        'scene': scene,
        'run_per_frame': 1,
        'speed': 0.2
      }
    )
    
    self._task_scheduler.add_task(
      agent_traverse_linear_path, 
      [], 
      {
        'path_id': linear_path.id,
        'agent_id': a2.id,
        'step_index': 6,
        'scene': scene,
        'run_per_frame': 1,
        'speed': 0.2
      }
    )

    self._task_scheduler.add_task(
      agent_traverse_linear_path, 
      [], 
      {
        'path_id': linear_path.id,
        'agent_id': a3.id,
        'step_index': 8,
        'scene': scene,
        'run_per_frame': 1,
        'speed': 0.4
      }
    )

    self._task_scheduler.add_task(
      agent_traverse_linear_path, 
      [], 
      {
        'path_id': linear_path.id,
        'agent_id': a4.id,
        'step_index': 14,
        'scene': scene,
        'run_per_frame': 1,
        'speed': 0.6
      }
    )
    
    # Add a task for the agent on the circular paths.
    self._task_scheduler.add_task(
      agent_traverse_circular_path, 
      [], 
      {
        'path_id': circle_path_a.id,
        'agent_id': a5.id,
        'starting_degree': 0,
        'scene': scene,
        'run_per_frame': 1,
        'speed': 0.3
      }
    )

  def _create_path_a(self) -> LinearPath:
    logger.info('MultipleAgentsSim: Building agent paths')
    control_points = (
      # Walk 5 steps East.
      9,4, 10,4, 11,4, 12,4, 13,4, 14,4,
      # Walk 3 steps south
      14,5, 14,6, 14,7,
      # Walk 6 steps to the East
      15,7, 16,7, 17,7, 18,7, 19,7, 20,7,
      # Walk 2 steps south
      20,8, 20,9,
      # Walk 8 steps to the West
      19,9, 18,9, 17,9, 16,9, 15,9, 14,9, 13,9, 12,9,
      # Walk North 3 steps
      12,8, 12,7, 12,6, 
      # Walk West 3 steps
      11,6, 10,6, 9,6,
      # Walk North
      9,5
    )
    return LinearPath(dpg.generate_uuid(), control_points, line_segment_renderer)
  
  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    logger.info('MultipleAgentsSim: Establishing simulation context.')
    context.details['cell_size'] = self._cell_size
    context.details['offset'] = Size(self._cell_center_x_offset, self._cell_center_y_offset)
    # TODO: Transition to passing a scene around. 
    # Perhaps the Scene or context should be transitioned to 
    # FrameParams type object.
    context.details['scene'] = self._scene

    # TODO: Remove this and just pass the scene around.
    context.details['paths'] = self._scene.paths.values()
    

  def _bootstrap_simulation_render(self) -> None:
    logger.info('MultipleAgentsSim: Bootstrapping simulation renderer')
    # I think this is where everything needs to get wired together.
    
  def _sim_loop_tick(self, **args) -> None:
    """Handles one tick of the simulation."""
    # Force a rerender by updating the scene graph.
    self._update_scene_graph(self._scene)
    
  def _update_scene_graph(self, scene: Scene) -> None:
    logger.info('MultipleAgentsSim: Update Scene Graph')
    for agent_id, agent in scene.agents.items():
      update_agent_in_scene_graph(agent, agent_id, self._cell_size)

"""
Design Questions/Thoughts
- TODO: The life cycle methods of a simulation is convoluted. 
  This isn't saving any time. Evaluate collapsing the class hierarchy and doing 
  more composition.
- Design Question: Better to have a task per agent or a task to update all tasks?

- How to deal with timing? Options:
  - Pass the frame in. Some tasks may be restricted to how many times it can run
    per frame.
  - Another option is to deal with velocity and movement vectors. Each step 
    could represent a velocity and a direction to to go.

It feels like a good approach is to introduce the concept of motion vectors however
I need to reconcile that with the concept of a path. 
- Rather than steps, a path needs to be defined by points. 
- On each tick, an agent that is bound to a path would then use the combination
  of interpolation and velocity (factor of time) to determine where it's at.

Physics Primitives
- Speed: How fast an object is moving (scalar).
- Velocity: Speed in a direction (vector).
- Acceleration: The rate of change of the velocity (vector).
- Mass: 
- Friction 

Finding a Position on a Curve
- Linear Interpolation (Real-Time Rendering, equation 13.1, pg 578)
  p(t) = p0 + t*(p1 - p0) = (1-t)*p0 + t*p1
  where t in in the set [0, 1]
  To do this, would first need to identify which points the agent is between
  then interpolate between them.

- Lagrange Interpolation
- Hermite interpolation
- Cubic Interpolation of Splines

Create a task that moves an agent one step on a path.
"""
def agent_traverse_linear_path(*args, **kwargs) -> None:
  """A task that moves an agent along a path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - step_index: The starting point on the path.
  """
  logger.info('agent_traverse_path: Starting task.')
  scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  scene = kwargs['scene']
  speed: float = kwargs['speed'] 

  agent = scene.agents[agent_id]
  path: LinearPath = scene.paths[path_id]
  segments_count = path.segments_count()
  active_path_segment: int = kwargs['step_index']
  active_t: float = 0 # In the range of [0,1]
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_path_segment, active_t)
      agent.move_to(Point(pt[0], pt[1]))

      active_t += speed
      if active_t > 1:
        active_t = 0
        active_path_segment = active_path_segment + 1 if active_path_segment < segments_count else 1
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_update - GeneratorExit')
  finally:
    print('Task: agent_update - task completed')

from math import pi
def agent_traverse_circular_path(*args, **kwargs) -> None:
  """A task that moves an agent along a circular path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - starting_degree: Where on the circle to start the animation.
  """
  logger.info('agent_traverse_circular_path: Starting task.')
  scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  scene = kwargs['scene']
  active_t: float = kwargs['starting_degree'] # In the range of [0, 2*pi]
  speed: float = kwargs['speed'] 

  agent = scene.agents[agent_id]
  path: LinearPath = scene.paths[path_id]
  
  max_radian = 2 * pi
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_t)
      agent.move_to(Point(pt[0], pt[1]))
      active_t += speed
      if active_t > max_radian:
        active_t = 0
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_update - GeneratorExit')
  finally:
    print('Task: agent_update - task completed')