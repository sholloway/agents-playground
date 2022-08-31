"""
Module containing coroutines related to moving agents.
"""
from math import copysign, radians
from typing import Generator, Tuple, cast
from agents_playground.agents.agent import Agent, AgentState, AgentStateMap
from agents_playground.agents.direction import Vector2D
from agents_playground.agents.path import CirclePath, LinearPath
from agents_playground.agents.structures import Point
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.renderers.color import Color
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

def agent_traverse_linear_path(*args, **kwargs) -> Generator:
  """A task that moves an agent along a path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - step_index: The starting point on the path.
  """
  logger.info('agent_traverse_linear_path: Starting task.')
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
      direction: Vector2D = path.direction(active_path_segment)
      agent.face(direction)

      active_t += speed
      if active_t > 1:
        active_t = 0
        active_path_segment = active_path_segment + 1 if active_path_segment < segments_count else 1
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_linear_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_linear_path - Task Completed')

def agent_traverse_circular_path(*args, **kwargs) -> Generator:
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
  direction = int(copysign(1, speed))

  agent: Agent = scene.agents[agent_id]
  path: CirclePath = scene.paths[path_id]

  
  max_degree = 360
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_t)
      agent.move_to(Point(pt[0], pt[1]))
      tangent_vector: Vector2D = path.tangent(pt, direction)
      agent.face(tangent_vector)

      active_t += speed
      if active_t > max_degree:
        active_t = 0
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_circular_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_circular_path - Task Completed')
    
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
        scene.agents[agent_id].move_to(Point(pt[0], pt[1]))
        group_motion[agent_id]['active_t'] += group_motion[agent_id]['speed']

        direction = int(copysign(1, group_motion[agent_id]['speed']))
        direction_vector: Vector2D = path.direction(int(group_motion[agent_id]['segment']))
        direction_vector = direction_vector.scale(direction)
        scene.agents[agent_id].face(direction_vector)
        
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
              scene.agents[agent_id].crest = direction_color[-direction]
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
              scene.agents[agent_id].crest = direction_color[-direction]
        
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_pacing - GeneratorExit')
  finally:
    logger.info('Task: agent_pacing - Task Completed')
    
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
        agent: Agent = scene.agents[agent_id]
        new_orientation = agent.facing.rotate(rotation_amount * rot_dir)
        agent.face(new_orientation)
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agents_spinning - GeneratorExit')
  finally:
    logger.info('Task: agents_spinning - Task Completed')


def agent_random_navigation(*args, **kwargs) -> Generator:
  """ Randomly navigate agents to various locations.
    For every agent in the scene:
      1. Choose a destination. 
      2. Route a course.
      3. Traverse the course.
      4. Once a destination is reached, rest for a bit, then repeat.

    Goals:
    - Migrate A* navigation from the maze project.
    - Develop an address system so the AI can say "go to The Factory".
    - Develop a path caching system so once a path has been generated for 
      a specific route (e.g. Tower 1 to The Factory) agents can just 
      leverage that rather than perform A* every time. Look at the 
      OOTB Python caching options (e.g. @cache).
  """
  logger.info('agents_spinning: Starting task.')
  scene: Scene = kwargs['scene']      

  """
  As we start out, and agent can have various states. 
  1. RESTING: It is at a location, resting. 
  2. PLANNING: It is ready to travel and needs to select its next destination.
  3. ROUTING: It has selected a destination and needs to request from the 
      Navigator to plan a route. 
  4. TRAVELING: It is traversing a route between two locations.
  """
  agent: Agent
  for agent in scene.agents.values():
    match agent.state:
      case AgentState.RESTING if not agent.resting_counter.at_min_value():
        agent.resting_counter.decrement()
      case AgentState.RESTING if agent.resting_counter.at_min_value():
        # Go to next state (i.e. Planning).
        agent.state = AgentStateMap[AgentState.RESTING]
      case AgentState.PLANNING:
        agent.desired_location = select_next_location(agent.location)
        # Go to next state (i.e. Routing).
        agent.state = AgentStateMap[AgentState.PLANNING]
      case AgentState.ROUTING:
        agent.route = AgentNavigator.find_route(agent.location, agent.agent.desired_location)
        agent.state = AgentStateMap[AgentState.ROUTING]
      case AgentState.TRAVELING if agent.location != agent.desired_location:
        travel(agent)
      case AgentState.TRAVELING if agent.location == agent.desired_location:
        # Transition ot the next state (i.e. resting).
        agent.state = AgentStateMap[AgentState.TRAVELING]
        agent.resting_counter.reset()
      case AgentState.IDLE:
        pass
      case _:
        # Nothing to do...
        pass
        
def select_next_location(current_location: Point) -> Point:
  return current_location

class AgentNavigator:
  pass

def travel(agent: Agent) -> None:
  pass
        
