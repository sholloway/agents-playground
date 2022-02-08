from typing import List

import dearpygui.dearpygui as dpg

from agents_playground.agents.path import AgentPath, AgentStep
from agents_playground.simulation.context import SimulationContext, Size
from agents_playground.sys.logger import get_default_logger
from agents_playground.renderers.color import PrimaryColors

logger = get_default_logger()

# FIXME The loose contract of the layer renderers sucks. 
# Should probably not use the Callables.invoke method and 
# get a better defined contract. Perhaps a Protocol?
# 
# BUG: Can't deal with more than one path.
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
  logger.info('Renderer: render_path')
  context: SimulationContext = data['context']
  path: AgentPath = context.details['path']
  cell_size: Size = context.details['cell_size']
  cell_center_x_offset: float = context.details['cell_center_x_offset']
  cell_center_y_offset: float = context.details['cell_center_y_offset']

  # Transform the path of cells into canvas points.
  displayed_path: List[List[float]] = []
  for step in path:
    # NOTE: Is there a better way than hasattr? Protocols?
    if hasattr(step, 'location') and step.location:
      point = [
        step.location.x * cell_size.width + cell_center_x_offset, 
        step.location.y * cell_size.height + cell_center_y_offset
      ]
      displayed_path.append(point)
  dpg.draw_polyline(displayed_path, closed=True, color=PrimaryColors.red)

def render_paths(**data) -> None:
  """Draws multiple path.
  
  Args
    - context: A SimulationContext instance.
    
  Context Details
    - cell_size
    - paths
    - cell_center_x_offset
    - cell_center_y_offset
  """
  logger.info('Renderer: render_paths')
  context: SimulationContext = data['context']
  paths: List[AgentPath] = context.details['paths']
  cell_size: Size = context.details['cell_size']
  cell_center_x_offset: float = context.details['cell_center_x_offset']
  cell_center_y_offset: float = context.details['cell_center_y_offset']

  # Transform the path of cells into canvas points.
  for path in paths:
    displayed_path: List[List[float]] = []
    for step in path:
      # NOTE: Is there a better way than hasattr? Protocols?
      if hasattr(step, 'location') and step.location:
        point = [
          step.location.x * cell_size.width + cell_center_x_offset, 
          step.location.y * cell_size.height + cell_center_y_offset
        ]
        displayed_path.append(point)
    dpg.draw_polyline(displayed_path, closed=True, color=PrimaryColors.red)