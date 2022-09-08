from __future__ import annotations
from enum import Enum
from pickle import TRUE
from sre_constants import SUCCESS
from types import SimpleNamespace
from typing import List, Optional, Set, Tuple, Union
from agents_playground.agents.direction import Direction

from agents_playground.agents.structures import Point
from agents_playground.core.priority_queue import PriorityQueue
from agents_playground.navigation.navigation_mesh import NavigationMesh
from agents_playground.navigation.waypoint import Waypoint

def find_distance(a: Point, b: Point) -> float:
  """Finds the Manhattan distance between two locations."""
  return abs(a.x - b.x) + abs(a.y - b.y)
  
Route = List[Point]

def build_path(endpoint: Waypoint) -> Route:
  """
  Given a Waypoint, builds a path following the waypoint's parent pointers.
  Note: Will fail if there is a loop.

  Returns
  A path instance.
  """
  points : Route = []

  current = endpoint
  while current != None:
    points.append(current.point)
    current = current.predecessor

  points.reverse()
  return points

class NavigationResultStatus(Enum):
  SUCCESS = True
  FAILURE = False

NavigationRouteResult = Union[None, Route]
  
class Navigator:
  def __init__(self) -> None:
    pass
  
  # TODO: Make this method cache-able
  def find_route(
    self, 
    starting_location: Point, 
    desired_location: Point, 
    nav_mesh: NavigationMesh) -> Tuple[NavigationResultStatus, NavigationRouteResult]:
    """ Charts a route using the navigation mesh between two points on the grid.

    Args
      - starting_location: Where the agent currently is in cell coordinates.
      - desired_location: Where the agent wants to go in cell coordinates.
      - nav_mesh: The data structure that represents the possible places an agent can visit.

    Returns
      Returns a tuple of the form (NavigationResultStatus, None | Route).
    """
    print(f'Attempting to route from {starting_location} to {desired_location}')
    visited_locations: Set[Point] = set()
    possible_steps: PriorityQueue = PriorityQueue()

    starting_point = Waypoint(starting_location, None)
    starting_point.cost_from_start = 0
    starting_point.cost_to_target = find_distance(starting_point.point, desired_location)
    possible_steps.push(starting_point, starting_point, starting_point.total_cost())

    routing_pass: int = 0
    while len(possible_steps) > 0:
      _ignore_cost: float
      current_location: Waypoint
      _ignore_data: Optional[dict]
      _ignore_cost, current_location, _ignore_data = possible_steps.pop() 
      routing_pass += 1
      print(f'Routing pass: {routing_pass}')
      if current_location.point == desired_location:
        return (NavigationResultStatus.SUCCESS, build_path(current_location))
      else:
        visited_locations.add(current_location.point)
        # Find the corresponding junction in the navigation mesh for the current location.
        current_junction: SimpleNamespace = nav_mesh.find_junction(current_location.point)
  
        if(current_junction is None):
          raise Exception(f'{current_location.point.x},{current_location.point.y} has no location.')

        # Find the locations that can be reached in the navigation mesh at the current junction.
        connected_locations = nav_mesh.find_connected_locations(current_junction.toml_id)

        for neighbor_location in connected_locations:
          neighbor = Waypoint(neighbor_location, current_location)

          # Ignore the location if that's where we just came from
          if (current_location.predecessor is not None) and (neighbor.point == current_location.predecessor.point) :
            continue

          cost_to_add_step_to_path = current_location.total_cost() + find_distance(current_location.point, neighbor.point)
          neighbor.cost_from_start = cost_to_add_step_to_path
          neighbor.cost_to_target = find_distance(neighbor.point, desired_location)

          # We could have visited this location before from a different path. 
          # If that's the case, then remove it from the visited set or possible queue.
          if (neighbor.point in visited_locations) and (cost_to_add_step_to_path < find_distance(starting_point.point, neighbor.point)) :
            visited_locations.remove(neighbor.point)

          if (neighbor in possible_steps) and (cost_to_add_step_to_path < find_distance(starting_point.point, neighbor.point)):
            possible_steps.remove(neighbor) 
          
          if (neighbor not in possible_steps) and (neighbor.point not in visited_locations):
            possible_steps.push(neighbor, neighbor.total_cost())
  
    return (NavigationResultStatus.FAILURE, None)