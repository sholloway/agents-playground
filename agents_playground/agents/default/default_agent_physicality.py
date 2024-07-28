from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox
from agents_playground.spatial.frustum import Frustum
from agents_playground.spatial.coordinate import Coordinate

class DefaultAgentPhysicality(AgentPhysicalityLike):
    def __init__(
        self, size: Size, aabb: AABBox, frustum: Frustum, scale_factor: float = 1.0
    ) -> None:
        self.size = size
        self.aabb = aabb
        self.frustum = frustum
        self.scale_factor = scale_factor

    def calculate_aabb(self, agent_location: Coordinate, cell_size: Size) -> None:
        """
        Defines an axis aligned bounding box in 2D for an agent.
        """
        raise NotImplementedError()