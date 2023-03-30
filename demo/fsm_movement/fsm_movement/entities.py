from agents_playground.project.extensions import register_entity
from agents_playground.scene.scene import Scene

@register_entity(label='agent_state_display_refresh')
def agent_state_display_refresh(self, scene: Scene) -> None:
  return
  # Todo: Will need to do an dpg.configure_item(...) call to trigger an update.
  # The entity renderer is invoked initially by the entity layer function 
  # when the sim starts.