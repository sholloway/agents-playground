from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox, AABBox2d
from agents_playground.spatial.frustum import Frustum
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vertex import Vertex2d

class DefaultAgentPhysicality(AgentPhysicalityLike):
  def __init__(
    self, 
    size: Size, 
    aabb: AABBox,
    frustum: Frustum, 
    scale_factor: float = 1.0
  ) -> None:
    self.size         = size
    self.aabb         = aabb
    self.frustum      = frustum
    self.scale_factor = scale_factor

  def calculate_aabb(self, agent_location: Coordinate, cell_size: Size) -> None:
    agent_half_width:float  = self.size.width  / 2.0
    agent_half_height:float = self.size.height / 2.0
    cell_half_width         = cell_size.width  / 2.0
    cell_half_height        = cell_size.height / 2.0

    # 1. Convert the agent's location to a canvas space.
    agent_loc: Coordinate = agent_location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. Agent's are shifted to be drawn in near the center of a grid cell, 
    # the AABB needs to be shifted as well.
    agent_loc = agent_loc.shift(Coordinate(cell_half_width, cell_half_height))

    # 3. Create an AABB for the agent with the agent's location at its centroid.
    self.aabb = AABBox2d(
      center = Vertex2d(
        x = agent_loc.x, 
        y = agent_loc.y
      ), 
      half_width  = agent_half_width, 
      half_height = agent_half_height
    ) 