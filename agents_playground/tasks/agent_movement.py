"""
Module containing coroutines related to moving agents.
"""
from __future__ import annotations
from types import SimpleNamespace

import dearpygui.dearpygui as dpg
from functools import lru_cache
import itertools
from math import copysign, radians
import random
from typing import Generator, List, Tuple, cast

from agents_playground.agents.agent import Agent, AgentActionState, AgentStateMap
from agents_playground.agents.direction import Vector2d
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.core.types import Coordinate
from agents_playground.navigation.navigation_mesh import Junction, NavigationMesh
from agents_playground.navigation.navigator import NavigationResultStatus, Navigator, Route, NavigationRouteResult
from agents_playground.paths.linear_path import LinearPath
from agents_playground.paths.circular_path import CirclePath
from agents_playground.renderers.color import Color
from agents_playground.renderers.path import line_segment_renderer
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
  scene: Scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  speed: float = kwargs['speed'] 

  agent: Agent = scene.agents[agent_id]
  path: LinearPath = cast(LinearPath, scene.paths[path_id])
  segments_count = path.segments_count()
  active_path_segment: int = kwargs['step_index']
  active_t: float = 0 # In the range of [0,1]
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_path_segment, active_t)
      agent.move_to(Coordinate(pt[0], pt[1]), scene.agent_style.size, scene.cell_size)
      direction: Vector2d = path.direction(active_path_segment)
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
  scene: Scene = kwargs['scene']
  agent_id: Tag = kwargs['agent_id']
  path_id = kwargs['path_id']
  active_t: float = kwargs['starting_degree'] # In the range of [0, 2*pi]
  speed: float = kwargs['speed'] 
  direction = int(copysign(1, speed))

  agent: Agent = scene.agents[agent_id]
  path: CirclePath = cast(CirclePath, scene.paths[path_id])
  
  max_degree = 360
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_t)
      agent.move_to(Coordinate(pt[0], pt[1]), scene.agent_style.size, scene.cell_size)
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
        scene.agents[agent_id].move_to(Coordinate(pt[0], pt[1]), scene.agent_style.size, scene.cell_size)
        group_motion[agent_id]['active_t'] += group_motion[agent_id]['speed']

        direction = int(copysign(1, group_motion[agent_id]['speed']))
        direction_vector: Vector2d = path.direction(int(group_motion[agent_id]['segment']))
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


"""
Note: 
Currently this coroutine is deciding the agent's next state. 
Might want/need to migrate that responsibility to something that is self contained.
"""
def agent_random_navigation(*args, **kwargs) -> Generator:
  """ Randomly navigate agents to various locations.
    For every agent in the scene:
      1. Choose a destination. 
      2. Route a course.
      3. Traverse the course.
      4. Once a destination is reached, rest for a bit, then repeat.
  """
  logger.info('agent_random_navigation: Starting task.')
  scene: Scene = kwargs['scene']   
  walking_speed_range: List[float] = kwargs['speed_range']   
  navigator: Navigator = Navigator()
  find_route_with_cache = lru_cache(maxsize=1156)(navigator.find_route)

  try:
    while True:
      """
      As we start out, an agent can have various states. 
      1. RESTING: It is at a location, resting. 
      2. PLANNING: It is ready to travel and needs to select its next destination.
      3. ROUTING: It has selected a destination and needs to request from the 
          Navigator to plan a route. 
      4. TRAVELING: It is traversing a route between two locations.
      """
      agent: Agent
      for agent in scene.agents.values():
        match agent.actionable_state:
          case AgentActionState.RESTING if not agent.resting_counter.at_min_value():
            # print('Agent is resting.')
            agent.resting_counter.decrement()
          case AgentActionState.RESTING if agent.resting_counter.at_min_value():
            # Go to next state (i.e. Planning).
            # print('Agent is done resting. Transitioning to next state.')
            agent.actionable_state = AgentStateMap[AgentActionState.RESTING]
          case AgentActionState.PLANNING:
            # print('Agent is planning.')
            agent.move_to(
              find_exit_of_current_location(agent.location, scene.nav_mesh), 
              scene.agent_style.size, 
              scene.cell_size
            )
            agent.visible = True
            agent.desired_location = select_next_location(scene, agent.location, scene.nav_mesh)
            # Go to next state (i.e. Routing).
            agent.actionable_state = AgentStateMap[AgentActionState.PLANNING]
          case AgentActionState.ROUTING:
            """
            A few decision points:
            1. We need an instance of the AgentNavigator that's going to persist from run to run.
              Should it live in the coroutine or elsewhere?
            2. We should we track which route an agent is on?
            """
            # print('Agent is routing.')
            result_status: NavigationResultStatus
            possible_route: NavigationRouteResult
            # print(find_route_with_cache.cache_info())
            result_status, possible_route = find_route_with_cache(agent.location, agent.desired_location, scene.nav_mesh)
            if result_status == NavigationResultStatus.SUCCESS:
              # target_junction: Junction = scene.nav_mesh.get_junction_by_location(agent.desired_location)
              # print(f'A route was found between {agent.location} and {target_junction.toml_id}.')
              # print(route)
              # Let's just stick this on the agent for the moment.
              # Some other options are to have it bound in this coroutine or on the Scene instance.
              # Convert the list of Waypoints to a LinearPath object.
              # To do that I need to convert List[Point(x,y)] to (x,y, xx, yy, xxx, yyy...)
              route: Route = cast(Route, possible_route)
              control_points = tuple(itertools.chain.from_iterable(route))
              agent.active_route = LinearPath(dpg.generate_uuid(), control_points, line_segment_renderer, False)
              agent.active_path_segment = 1
              agent.walking_speed = random.triangular(low = walking_speed_range[0], high = walking_speed_range[1])
              agent.active_t = 0 # In the range of [0,1]
              agent.actionable_state = AgentStateMap[AgentActionState.ROUTING]
            else:
              # print(f'A route could not be found between {agent.location} and {agent.desired_location}.')
              raise Exception('Agent Navigation Failure')
          case AgentActionState.TRAVELING if agent.location != agent.desired_location:
            # print('An agent is traveling.')
            travel(agent, scene)
          case AgentActionState.TRAVELING if agent.location == agent.desired_location:
            # Transition ot the next state (i.e. resting).
            # print('Agent has arrived at destination.')
            agent.actionable_state = AgentStateMap[AgentActionState.TRAVELING]
            agent.resting_counter.reset()

            # At this point, make the agent invisible to indicate 
            # it's inside it's destination.
            agent.visible = False
          case AgentActionState.IDLE:
            print('Agent is idle.')
            pass
          case _:
            # Nothing to do...
            print('Unexpected Agent state.')
            pass
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_random_navigation - GeneratorExit')
  finally:
    logger.info('Task: agent_random_navigation - Task Completed')

import random
      
def select_specific_location(scene: Scene, current_location: Coordinate, nav_mesh: NavigationMesh) -> Coordinate:
  target_junction: Junction = nav_mesh.get_junction_by_toml_id('factory-entrance')
  return cast(Coordinate, target_junction.location)

location_groups = (
  'factories', 'schools','churches','main_street_businesses','parks',
  'gov_buildings','big_box_stores','apartment_buildings'
)

# never going to parks, gov_buildings, big_box_stores, apartment_buildings

def select_next_location(scene: Scene, current_location: Coordinate, nav_mesh: NavigationMesh) -> Coordinate:
  """Randomly select a location to travel to. Ensures that the current location is not selected."""
  # 1. Find a location.
  location_selected: bool = False
  while not location_selected:
    random_location_group: str = random.choice(location_groups)
    random_location: SimpleNamespace = random.choice(list(scene.entities[random_location_group].values()))
    location_selected = random_location.location != current_location

  # 2. Find the entrance junction for the location on the navigation mesh.
  filter_method = lambda j: j.entity_id == random_location.toml_id and 'entrance' in j.toml_id

  # BUG: The reason it keeps going to just a handful of locations is because 
  # It's searching for entity_id and entrance. Unfortunately the entity ID isn't unique. 
  # I need to either change the entity id to be unique or add a category to the junction definition. 
  # Barf...
  location_entrance_junction: Junction = next(filter(filter_method, nav_mesh.junctions())) # raises StopIteration if no match

  return cast(Coordinate, location_entrance_junction.location)

def find_exit_of_current_location(current_location: Coordinate, nav_mesh: NavigationMesh) -> Coordinate:
  current_junction = nav_mesh.get_junction_by_location(current_location)
  exit_junction__toml_id: str = current_junction.toml_id.replace('entrance', 'exit')
  exit_junction: Junction = nav_mesh.get_junction_by_toml_id(exit_junction__toml_id)
  return cast(Coordinate, exit_junction.location)

def travel(agent: Agent, scene: Scene) -> None:
  """For each tick, move along the active route until the destination is reached."""
  path: LinearPath = agent.active_route
  segments_count = path.segments_count()
  
  pt: Tuple[float, float] = path.interpolate(agent.active_path_segment, agent.active_t)
  agent.move_to(Coordinate(*pt), scene.agent_style.size, scene.cell_size)
  direction: Vector2d = path.direction(agent.active_path_segment)
  agent.face(direction)

  agent.active_t += agent.walking_speed
  if agent.active_t > 1:
    agent.active_t = 0
    if agent.active_path_segment < segments_count:
      # Move to next segment.
      agent.active_path_segment = agent.active_path_segment + 1 
    else:
      # Done traveling.
      agent.move_to(agent.desired_location, scene.agent_style.size, scene.cell_size)
        
