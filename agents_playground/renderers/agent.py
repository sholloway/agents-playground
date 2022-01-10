
import dearpygui.dearpygui as dpg

from agents_playground.renderers.color import Color
from agents_playground.agents.structures import Size
from agents_playground.simulation.context import SimulationContext

def render_agents(**data) -> None:
  context: SimulationContext = data['context']
  agent_ref = context.details['agent_ref']
  agent_size: Size = context.agent_style.size
  
  agent_width_half: float = agent_size.width / 2.0
  agent_height_half: float = agent_size.height / 2.0
  
  with dpg.draw_node(tag=agent_ref):
    # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
    dpg.draw_triangle(
      p1=(agent_width_half,0), 
      p2=(-agent_width_half, -agent_height_half), 
      p3=(-agent_width_half, agent_height_half), 
      color=context.agent_style.stroke_color, 
      fill=context.agent_style.fill_color, 
      thickness=context.agent_style.stroke_thickness
    )