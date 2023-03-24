from typing import Protocol

from agents_playground.core.types import AABBox, Coordinate, Size


class AgentPhysicalityLike(Protocol):
  size: Size 
  aabb: AABBox 

  def calculate_aabb(self, agent_location: Coordinate, cell_size: Size) -> None:
    agent_half_width:float  = self.size.width  / 2.0
    agent_half_height:float = self.size.height / 2.0
    cell_half_width         = cell_size.width  / 2.0
    cell_half_height        = cell_size.height / 2.0

    # 1. Convert the agent's location to a canvas space.
    # agent_loc: Coordinate = cell_to_canvas(agent.location, cell_size)
    agent_loc: Coordinate = agent_location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. Agent's are shifted to be drawn in near the center of a grid cell, 
    # the AABB needs to be shifted as well.
    agent_loc = agent_loc.shift(Coordinate(cell_half_width, cell_half_height))

    # 3. Create an AABB for the agent with the agent's location at its centroid.
    min_coord = Coordinate(agent_loc.x - agent_half_width, agent_loc.y - agent_half_height)
    max_coord = Coordinate(agent_loc.x + agent_half_width, agent_loc.y + agent_half_height)
    self.aabb = AABBox(min_coord, max_coord)
