from abc import abstractmethod
from typing import Protocol

from agents_playground.core.types import Size
from agents_playground.spatial.aabbox import AABBox, AABBox2d
from agents_playground.spatial.frustum import Frustum
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vertex import Vertex2d


class AgentPhysicalityLike(Protocol):
    size: Size
    scale_factor: float
    aabb: AABBox
    frustum: Frustum

    @abstractmethod
    def calculate_aabb(self, agent_location: Coordinate, cell_size: Size) -> None:
        """Calculates an axis-aligned bounding box for the agent."""
