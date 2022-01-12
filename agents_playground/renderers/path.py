from typing import List

import dearpygui.dearpygui as dpg

from agents_playground.agents.path import AgentPath, AgentStep
from agents_playground.simulation.context import SimulationContext, Size

# FIXME The loose contract of the layer renderers sucks. 
# Should probably not use the Callables.invoke method and 
# get a better defined contract.
def render_path(**data) -> None:
  """Draws a path.
  
  Args
    - context: A SimulationContext instance.
    
  Context Details
    - cell_size
    - path
    - cell_center_x_offset
    - cell_center_y_offset
  """
  context: SimulationContext = data['context']
  cell_size: Size = context.details['cell_size']
  path: AgentPath = context.details['path']
  cell_center_x_offset: float = context.details['cell_center_x_offset']
  cell_center_y_offset: float = context.details['cell_center_y_offset']

  # Transform the path of cells into canvas points.
  displayed_path: List[List[float]] = []
  for step in path:
    if isinstance(step, AgentStep) and step.location:
      point = [
        step.location.x * cell_size.width + cell_center_x_offset, 
        step.location.y * cell_size.height + cell_center_y_offset
      ]
      displayed_path.append(point)
  dpg.draw_polyline(displayed_path, closed=True, color=(255,0,0))