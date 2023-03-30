from agents_playground.project.extensions import register_entity
from agents_playground.scene.scene import Scene

@register_entity(label='agent_state_display_refresh')
def agent_state_display_refresh(self, scene: Scene) -> None:
  return