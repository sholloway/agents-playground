from math import floor

import dearpygui.dearpygui as dpg
from agents_playground.agents.structures import Size
from agents_playground.sys.logger import get_default_logger
from agents_playground.renderers.color import Color, Colors

logger = get_default_logger()

def render_grid(**data) -> None:
  """Draws a grid on a solid background.
  
  Args
    - context: A SimulationContext instance.
  """
  logger.info('Renderer: render_grid')
  context = data['context']
  cell_size: Size = context.scene.cell_size
  rows: int = floor(context.canvas.height/cell_size.height) - 1
  columns: int = floor(context.canvas.width/cell_size.width) - 1
  grid_background_color: Color = Colors.white.value
  grid_width = columns * cell_size.width
  grid_height = rows * cell_size.height
  grid_line_color: Color = (45, 45, 45)
  grid_marker_line: Color = Colors.red.value
  grid_marker_line_thickness:float = 1.3
  grid_marker: int = 10
  grid_line_thickness: float = 1

  dpg.draw_rectangle(pmin=(0,0),pmax=(grid_width, grid_height), fill=grid_background_color)
  
  # Draw horizontal lines
  for row in range(rows + 1): 
    vertical_offset = row * cell_size.height
    line_color = grid_line_color if row % grid_marker else grid_marker_line
    line_thickness = grid_line_thickness if row % grid_marker else grid_marker_line_thickness
    dpg.draw_line(
      p1=(0, vertical_offset), 
      p2=(grid_width, vertical_offset), 
      color=line_color, 
      thickness=line_thickness
    )

  # Draw vertical lines
  for col in range(columns+1): 
    horizontal_offset = col * cell_size.width
    line_color = grid_line_color if col % grid_marker else grid_marker_line
    line_thickness = grid_line_thickness if col % grid_marker else grid_marker_line_thickness
    dpg.draw_line(
      p1=(horizontal_offset, 0), 
      p2=(horizontal_offset, grid_height), 
      color=line_color, 
      thickness=line_thickness
    )

  