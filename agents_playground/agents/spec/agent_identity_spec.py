from typing import Protocol

from agents_playground.simulation.tag import Tag

class AgentIdentityLike(Protocol):
  id: Tag           # The ID used for the group node in the scene graph.
  community_id: Tag # The ID used in the Scene file (TOML, JSON, etc). TODO: Merge ID and community ID after removing DearPyGUI.
  render_id: Tag    # The ID used for the triangle in the scene graph.
  aabb_id: Tag      # The ID used rendering the agent's AABB.
  frustum_id: Tag   # The ID used for rendering the agent's view frustum.

  # TODO: This needs to be extensible. How can a sim define additional shapes
  # to render if they all need a unique tag?