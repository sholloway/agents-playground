from agents_playground.agents.spec.agent_movement_attributes import (
    AgentMovementAttributes,
)


class DefaultAgentMovementAttributes(AgentMovementAttributes):
    """By default there aren't any movement specific attributes"""

    def __init__(self) -> None:
        pass
