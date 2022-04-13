import dearpygui.dearpygui as dpg

from agents_playground.simulation.context import SimulationContext


def render_stats(**data) -> None:
  """Render a text overlay of the active runtime statistics.
  
  Args:
    - 
  """
  context: SimulationContext = data['context']
  stats = context.stats
  # TODO Need to make the stats text display on top of the terrain.
  dpg.draw_text(tag=stats.fps.id, pos=(20,20), text=f'Frame Rate (Hz): {stats.fps.value}', size=13)
  dpg.draw_text(tag=stats.utilization.id, pos=(20,40), text=f'Utilization (%): {stats.utilization.value}', size=13)