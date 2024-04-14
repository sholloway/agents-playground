from types import SimpleNamespace
from typing import Tuple

import dearpygui.dearpygui as dpg

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.constants import DEFAULT_FONT_SIZE
from agents_playground.legacy.project.extensions import register_renderer
from agents_playground.paths.circular_path import CirclePath
from agents_playground.renderers.color import Color, PrimaryColors
from agents_playground.simulation.context import SimulationContext, Size

@register_renderer(label='circular_path_renderer')
def circle_renderer(path: CirclePath, cell_size: Size, offset: Size) -> None:
  center = (
    path._center[0] * cell_size.width + offset.width, 
    path._center[1] * cell_size.height + offset.height, 
  )
  radius = path.radius * cell_size.width
  dpg.draw_circle(center, radius, color=PrimaryColors.red.value)

@register_renderer(label='text_display')
def text_display(self: SimpleNamespace, context: SimulationContext) -> None:
  """Renders text for an entity state display.
  
  Args:
    - self: An entity is dynamically bound to the render function.
    - context: The simulation context for the running sim.
  """
  # Convert the specified location on the entity from cell coordinates to pixels.
  cell_size:Size = context.scene.cell_size
  location_in_pixels: Tuple[int,int] = (
    self.location[0] * cell_size.width, 
    self.location[1] * cell_size.height
  )

  agent: AgentLike = context.scene.agents[self.agent_id]
  state_name: str = agent.agent_state.current_action_state.name
  dpg.draw_text(
    tag = self.id, 
    pos = location_in_pixels, 
    size  = DEFAULT_FONT_SIZE,
    text = f'State: {state_name}')