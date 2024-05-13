
from types import SimpleNamespace
from typing import Callable
from agents_playground.agents.default.default_agent_system import DefaultAgentSystem
from agents_playground.agents.memory.agent_memory_model import AgentMemoryModel

from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.agents.spec.agent_movement_attributes import AgentMovementAttributes
from agents_playground.agents.spec.agent_physicality_spec import AgentPhysicalityLike
from agents_playground.agents.spec.agent_position_spec import AgentPositionLike
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_state_spec import AgentStateLike
from agents_playground.agents.spec.agent_style_spec import AgentStyleLike
from agents_playground.agents.spec.agent_system import AgentSystemLike

class DefaultAgent(AgentLike):
  def __init__(
    self, 
    initial_state: AgentStateLike, 
    style: AgentStyleLike,
    identity: AgentIdentityLike,
    physicality: AgentPhysicalityLike,
    position: AgentPositionLike,
    movement: AgentMovementAttributes,
    agent_memory: AgentMemoryModel,
    internal_systems: AgentSystemLike = DefaultAgentSystem(
      'root_system'
    ),
    agent_def_alias: str = ''
  ) -> None:
    """Creates a new instance of an agent.
    
    Args:
      initial_state - The initial configuration for the various state fields.
      style - Define's the agent's look.
      identity - All of the agent's IDs.
      physicality - The agent's physical attributes.
      position - All the attributes related to where the agent is.
      movement - Attributes used for movement.
      memory - The agent's internal memory banks.
      internal_systems - The subsystems that the agent is comprised of.
    """
    self.agent_state      = initial_state
    self.style            = style
    self.identity         = identity
    self.physicality      = physicality
    self.position         = position
    self.movement         = movement
    self.memory           = agent_memory
    self.internal_systems = internal_systems
    self.agent_def_alias  = agent_def_alias