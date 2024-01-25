"""
Module containing coroutines related to moving agents.
"""
from __future__ import annotations
from types import SimpleNamespace

import dearpygui.dearpygui as dpg
from functools import lru_cache
import itertools
import random
from typing import Generator, List, Tuple, cast

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.project.extensions import register_task
from agents_playground.core.task_scheduler import ScheduleTraps
from agents_playground.navigation.navigation_mesh import Junction, NavigationMesh
from agents_playground.navigation.navigator import NavigationResultStatus, Navigator, Route, NavigationRouteResult
from agents_playground.paths.linear_path import LinearPath
from agents_playground.legacy.scene.scene import Scene
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector2d import Vector2d

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

from a_star_navigation.renderers import line_segment_renderer
from a_star_navigation.agent_states import AgentStateNames

"""
Note: 
Currently this coroutine is deciding the agent's next state. 
Might want/need to migrate that responsibility to something that is self contained.
"""
@register_task(label='agent_random_navigation')
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
      agent: AgentLike
      for agent in scene.agents.values():
        match agent.agent_state.current_action_state.name:
          case AgentStateNames.RESTING_STATE.name if not agent.movement.resting_counter.at_min_value():
            # print('Agent is resting.')
            agent.movement.resting_counter.decrement()
          case AgentStateNames.RESTING_STATE.name if agent.movement.resting_counter.at_min_value():
            # Go to next state (i.e. Planning).
            # print('Agent is done resting. Transitioning to next state.')
            agent.agent_state.transition_to_next_action(agent.agent_characteristics())
          case AgentStateNames.PLANNING_STATE.name:
            # print('Agent is planning.')
            agent.move_to(
              find_exit_of_current_location(agent.position.location, scene.nav_mesh), 
              scene.cell_size
            )
            agent.agent_state.set_visibility(True)
            next_location: Coordinate = select_next_location(
              scene, 
              agent.position.location, 
              scene.nav_mesh
            )

            if next_location is None:
              raise Exception(f'Could not select a next location.')

            agent.position.desired_location = next_location
            agent.agent_state.transition_to_next_action(agent.agent_characteristics())
          case AgentStateNames.ROUTING_STATE.name:
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
            result_status, possible_route = find_route_with_cache(
              agent.position.location, 
              agent.position.desired_location, 
              scene.nav_mesh
            )
            
            if result_status == NavigationResultStatus.SUCCESS:
              # target_junction: Junction = scene.nav_mesh.get_junction_by_location(agent.desired_location)
              # print(f'A route was found between {agent.location} and {target_junction.toml_id}.')
              # Let's just stick this on the agent for the moment.
              # Some other options are to have it bound in this coroutine or on the Scene instance.
              # Convert the list of Waypoints to a LinearPath object.
              # To do that I need to convert List[Point(x,y)] to (x,y, xx, yy, xxx, yyy...)
              route: Route = cast(Route, possible_route)
              control_points = tuple(itertools.chain.from_iterable(route))
              agent.movement.active_route = LinearPath(
                dpg.generate_uuid(), 
                control_points, 
                line_segment_renderer, 
                False
              )
              agent.movement.active_path_segment = 1
              agent.movement.walking_speed = random.triangular(
                low = walking_speed_range[0], 
                high = walking_speed_range[1]
              )
              agent.movement.active_t = 0 # In the range of [0,1]
              agent.agent_state.transition_to_next_action(agent.agent_characteristics())
            else:
              print(f'A route could not be found between {agent.position.location} and {agent.position.desired_location}.')
              raise Exception('Agent Navigation Failure')
          case AgentStateNames.TRAVELING_STATE.name if agent.position.location != agent.position.desired_location:
            # print('An agent is traveling.')
            travel(agent, scene)
          case AgentStateNames.TRAVELING_STATE.name if agent.position.location == agent.position.desired_location:
            # Transition ot the next state (i.e. resting).
            # print('Agent has arrived at destination.')
            agent.agent_state.transition_to_next_action(agent.agent_characteristics())
            agent.movement.resting_counter.reset()

            # At this point, make the agent invisible to indicate 
            # it's inside it's destination.
            agent.agent_state.set_visibility(False)
          case AgentStateNames.IDLE_STATE.name:
            # print('Agent is idle.')
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

  location_entrance_junction: Junction = next(filter(filter_method, nav_mesh.junctions())) # raises StopIteration if no match

  return cast(Coordinate, location_entrance_junction.location)

def find_exit_of_current_location(current_location: Coordinate, nav_mesh: NavigationMesh) -> Coordinate:
  current_junction = nav_mesh.get_junction_by_location(current_location)
  exit_junction__toml_id: str = current_junction.toml_id.replace('entrance', 'exit')
  exit_junction: Junction = nav_mesh.get_junction_by_toml_id(exit_junction__toml_id)
  return cast(Coordinate, exit_junction.location)

def travel(agent: AgentLike, scene: Scene) -> None:
  """For each tick, move along the active route until the destination is reached."""
  path: LinearPath = agent.movement.active_route
  segments_count = path.segments_count()
  
  pt: Tuple[float, float] = path.interpolate(agent.movement.active_path_segment, agent.movement.active_t)
  agent.move_to(Coordinate(*pt), scene.cell_size)
  direction: Vector2d = path.direction(agent.movement.active_path_segment)
  agent.face(direction, scene.cell_size)

  agent.movement.active_t += agent.movement.walking_speed
  if agent.movement.active_t > 1:
    agent.movement.active_t = 0
    if agent.movement.active_path_segment < segments_count:
      # Move to next segment.
      agent.movement.active_path_segment = agent.movement.active_path_segment + 1 
    else:
      # Done traveling.
      agent.move_to(agent.position.desired_location, scene.cell_size)
