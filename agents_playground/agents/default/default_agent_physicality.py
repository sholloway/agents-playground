from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox, EmptyAABBox

class DefaultAgentPhysicality(AgentPhysicalityLike):
  def __init__(
    self, 
    size: Size, 
    aabb: AABBox = EmptyAABBox(), 
    scale_factor: float = 1.0
  ) -> None:
    self.size         = size
    self.aabb         = aabb
    self.scale_factor = scale_factor