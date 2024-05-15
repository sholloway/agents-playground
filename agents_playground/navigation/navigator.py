from __future__ import annotations
from enum import Enum
from typing import List, Optional, Set, Tuple, Union

from agents_playground.core.priority_queue import PriorityQueue
from agents_playground.navigation.navigation_mesh import Junction, NavigationMesh
from agents_playground.navigation.waypoint import Waypoint, NavigationCost
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

Route = List[Coordinate]


def build_path(endpoint: Waypoint) -> Route:
    """
    Given a Waypoint, builds a path following the waypoint's parent pointers.
    Note: Will fail if there is a loop.

    Returns
    A path instance.
    """
    points: Route = []

    current: Optional[Waypoint] = endpoint
    while current is not None:
        points.append(getattr(current, "point"))
        current = getattr(current, "predecessor")

    points.reverse()
    return points


class NavigationResultStatus(Enum):
    SUCCESS = True
    FAILURE = False


NavigationRouteResult = Union[None, Route]
RouteAction = str


class Navigator:
    def __init__(self) -> None:
        pass

    def __del__(self) -> None:
        logger.info("Navigator destroyed.")

    # TODO: Make this method cache-able
    """
    Debugging
    The issue: Sometimes a path can be found sometimes it cannot for the same destination.

    Possible Issues:
    1. I think the issue is the graph can have loops. This can cause a node to need to
    be inspected multiple times, but perhaps the node is rejected the first time as
    part of a bad path.

    2. There is no way to turn around on the apartment street.
    3. The north bound street has multiple cycles.
    3. Issue with the Waypoint data structure. The fact that it can only have one predecessor may be the issue.

    Possible Solutions
    - Need to get more nuanced with how visited_locations is used.
    """

    def find_route(
        self,
        starting_location: Coordinate,
        desired_location: Coordinate,
        nav_mesh: NavigationMesh,
    ) -> Tuple[NavigationResultStatus, NavigationRouteResult]:
        """Charts a route using the navigation mesh between two points on the grid.

        Args
          - starting_location: Where the agent currently is in cell coordinates.
          - desired_location: Where the agent wants to go in cell coordinates.
          - nav_mesh: The data structure that represents the possible places an agent can visit.

        Returns
          Returns a tuple of the form (NavigationResultStatus, None | Route).
        """
        # print(f'Attempting to route from {starting_location} to {desired_location}')
        debug_order_evaluated: List[RouteAction] = []
        visited_locations: Set[Coordinate] = set()
        possible_steps: PriorityQueue = PriorityQueue()

        starting_point = Waypoint(starting_location, None)
        starting_point.cost_from_start = 0
        starting_point.cost_to_target = starting_point.point.find_manhattan_distance(
            desired_location
        )
        possible_steps.push(starting_point, starting_point, starting_point.total_cost())

        debug_routing_pass: int = 0
        debug_order_evaluated.append(f"\nRouting to {desired_location}")
        while len(possible_steps) > 0:
            _ignore_cost: float
            current_location: Waypoint
            _ignore_data: Optional[dict]
            _ignore_cost, current_location, _ignore_data = possible_steps.pop()

            debug_routing_pass += 1
            # print(f'Routing pass: {debug_routing_pass}')
            if current_location.point == desired_location:
                return (NavigationResultStatus.SUCCESS, build_path(current_location))
            else:
                debug_order_evaluated.append(
                    f"\n{debug_routing_pass} {current_location.point} != {desired_location}"
                )
                visited_locations.add(current_location.point)
                # Find the corresponding junction in the navigation mesh for the current location.
                current_junction: Junction = nav_mesh.get_junction_by_location(
                    current_location.point
                )
                debug_order_evaluated.append(
                    f"\n {debug_routing_pass} Current Junction {current_junction.toml_id} -> {current_junction.connects_to}"
                )

                if current_junction is None:
                    raise Exception(
                        f"\nJunction could not be fond for location ({current_location.point.x},{current_location.point.y})."
                    )

                # Explore the locations that can be reached in the navigation mesh at the current junction.
                for neighbor_location_toml_id in current_junction.connects_to:
                    # Find the neighbor's junction and mapped location.
                    neighbor_junction: Junction = nav_mesh.get_junction_by_toml_id(
                        neighbor_location_toml_id
                    )
                    neighbor: Waypoint = Waypoint(
                        neighbor_junction.location, current_location
                    )

                    debug_order_evaluated.append(
                        f"\n\t{debug_routing_pass} Evaluating neighbor {neighbor_junction.toml_id}"
                    )

                    # Ignore the location if that's where we just came from
                    # This shouldn't happen in the nav mesh, but could if there accidental two node loops.
                    if (current_location.predecessor is not None) and (
                        neighbor.point == current_location.predecessor.point
                    ):
                        debug_order_evaluated.append(
                            f"\n\t{debug_routing_pass} Ignoring {neighbor_junction.toml_id}. Just came from there."
                        )
                        continue

                    cost_to_add_step_to_path: (
                        NavigationCost
                    ) = current_location.total_cost() + current_location.point.find_manhattan_distance(
                        neighbor.point
                    )
                    neighbor.cost_from_start = cost_to_add_step_to_path
                    neighbor.cost_to_target = neighbor.point.find_manhattan_distance(
                        desired_location
                    )

                    # We could have visited this location before from a different path.
                    # If that's the case, then remove it from the visited set or possible queue.
                    if (neighbor.point in visited_locations) and (
                        cost_to_add_step_to_path
                        < starting_point.point.find_manhattan_distance(neighbor.point)
                    ):
                        debug_order_evaluated.append(
                            f"\n\t{debug_routing_pass} Removing {neighbor_junction.toml_id} from visited locations to enable reconsidering it."
                        )
                        visited_locations.remove(neighbor.point)

                    if (neighbor in possible_steps) and (
                        cost_to_add_step_to_path
                        < starting_point.point.find_manhattan_distance(neighbor.point)
                    ):
                        debug_order_evaluated.append(
                            f"\n\t{debug_routing_pass} Removing {neighbor_junction.toml_id} from possible_steps to enable reconsidering it."
                        )
                        possible_steps.remove(neighbor)

                    if (neighbor not in possible_steps) and (
                        neighbor.point not in visited_locations
                    ):
                        debug_order_evaluated.append(
                            f"\n\t{debug_routing_pass} Adding {neighbor_junction.toml_id} to possible_steps."
                        )
                        possible_steps.push(neighbor, neighbor, neighbor.total_cost())

                    debug_order_evaluated.append("\n")
        else:
            debug_order_evaluated.append(
                f"\n{debug_routing_pass} The possible_steps queue is empty.\n"
            )
            debug_order_evaluated.append(possible_steps.__str__())
            debug_order_evaluated.append("\nVisited Locations:\n")
            debug_order_evaluated.append(visited_locations.__str__())

        with open("debug_navigation.txt", "w") as f:
            f.writelines(debug_order_evaluated)

        return (NavigationResultStatus.FAILURE, None)
