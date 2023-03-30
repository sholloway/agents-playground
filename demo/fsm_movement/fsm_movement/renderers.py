import dearpygui.dearpygui as dpg

from agents_playground.project.extensions import register_renderer
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
def text_display() -> None:
  print('Renderer text_display called.')