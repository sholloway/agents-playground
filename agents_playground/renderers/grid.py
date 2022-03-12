from math import floor

import dearpygui.dearpygui as dpg
from agents_playground.agents.structures import Size
from agents_playground.sys.logger import get_default_logger
from agents_playground.renderers.color import Color

logger = get_default_logger()

def render_grid(**data) -> None:
  """Draws a grid on a solid background.
  
  Args
    - context: A SimulationContext instance.
  """
  logger.info('Renderer: render_grid')
  context = data['context']
  cell_size: Size = context.details['cell_size']
  rows: int = floor(context.canvas.height/cell_size.height) - 1
  columns: int = floor(context.canvas.width/cell_size.width) - 1
  grid_background_color: Color = (255,255,255)
  grid_width = columns * cell_size.width
  grid_height = rows * cell_size.height
  grid_line_color: Color = (45, 45, 45)
  grid_line_thickness: float = 1

  dpg.draw_rectangle(pmin=(0,0),pmax=(grid_width, grid_height), fill=grid_background_color)
  # For right now, just draw a grid.
  for row in range(rows + 1): # Draw horizontal lines
    vertical_offset = row * cell_size.height
    dpg.draw_line(
      p1=(0, vertical_offset), 
      p2=(grid_width, vertical_offset), 
      color=grid_line_color, 
      thickness=grid_line_thickness
    )

  for col in range(columns+1): # Draw vertical lines
    horizontal_offset = col * cell_size.width
    dpg.draw_line(
      p1=(horizontal_offset, 0), 
      p2=(horizontal_offset, grid_height), 
      color=grid_line_color, 
      thickness=grid_line_thickness
    )