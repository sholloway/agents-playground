from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.core.types import AABBox, EmptyAABBox, Size

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