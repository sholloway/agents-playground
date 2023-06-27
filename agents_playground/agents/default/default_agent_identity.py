from typing import Callable
from agents_playground.agents.spec.agent_identity_spec import AgentIdentityLike
from agents_playground.simulation.tag import Tag

class DefaultAgentIdentity(AgentIdentityLike):
  def __init__(self, id_generator: Callable[...,Tag]) -> None:
    self.id         = id_generator()
    self.render_id  = id_generator()
    self.toml_id    = id_generator()
    self.aabb_id    = id_generator()  
    self.frustum_id = id_generator()