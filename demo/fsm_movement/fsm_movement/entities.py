from types import SimpleNamespace
import dearpygui.dearpygui as dpg
from agents_playground.agents.spec.agent_spec import AgentLike

from agents_playground.legacy.project.extensions import register_entity
from agents_playground.legacy.scene.scene import Scene

@register_entity(label='agent_state_display_refresh')
def agent_state_display_refresh(self: SimpleNamespace, scene: Scene) -> None:
  """
  Update function for the state_displays entities.

  Args:
  - self: A bound entity. 
  - scene: The active simulation scene.
  """
  agent: AgentLike = scene.agents[self.agent_id]
  state_name: str = agent.agent_state.current_action_state.name
  dpg.configure_item(item = self.id, text = f'State: {state_name}')
