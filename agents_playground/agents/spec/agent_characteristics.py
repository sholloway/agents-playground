
from typing import NamedTuple

from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_memory_model import AgentMemoryLike
from agents_playground.agents.spec.agent_movement_attributes import AgentMovementAttributes
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike

class AgentCharacteristics(NamedTuple):
  identity: AgentIdentityLike        # All of the agent's IDs.
  physicality: AgentPhysicalityLike  # The agent's physical attributes.
  position: AgentPositionLike        # All the attributes related to where the agent is.     
  movement: AgentMovementAttributes  # Attributes used for movement.
  style: AgentStyleLike              # Define's the agent's look.
  memory: AgentMemoryLike            # The agent's memory banks.