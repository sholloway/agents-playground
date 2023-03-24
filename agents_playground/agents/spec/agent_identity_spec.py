from typing import Protocol

from agents_playground.simulation.tag import Tag

class AgentIdentityLike(Protocol):
  id: Tag         # The ID used for the group node in the scene graph.
  toml_id: Tag    # The ID used in the TOML file.
  render_id: Tag  # The ID used for the triangle in the scene graph.
  aabb_id: Tag    # The ID used rendering the agent's AABB.