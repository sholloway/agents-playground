from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.fp import Something
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.transformation.configuration import TransformationConfiguration
from agents_playground.spatial.vector.vector import Vector


class DefaultAgentPosition(AgentPositionLike):
    def __init__(
        self,
        facing: Vector,
        location: Coordinate,
        last_location: Coordinate,
        desired_location: Coordinate,
    ) -> None:
        self.facing = facing
        self.location = location
        self.last_location = last_location
        self.desired_location = desired_location
        self.transformation = Something(
            TransformationConfiguration(
                translation=list(location.to_tuple()),
                rotation=[],  # TODO: Integrate with the facing vector.
                scale=[],
            )
        )

    def move_to(self, new_location: Coordinate) -> None:
        self.last_location = self.location
        self.location = new_location
