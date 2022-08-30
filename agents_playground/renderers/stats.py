import dearpygui.dearpygui as dpg

from agents_playground.simulation.context import SimulationContext


def render_stats(**data) -> None:
  """Render a text overlay of the active runtime statistics."""
  context: SimulationContext = data['context']
  stats = context.stats
  
  dpg.draw_rectangle(pmin=(15,15), pmax=(180,60), fill=(120, 120, 240))
  dpg.draw_text(tag=stats.fps.id, pos=(20,20), text=f'Frame Rate (Hz): {stats.fps.value}', size=13)
  dpg.draw_text(tag=stats.utilization.id, pos=(20,40), text=f'Utilization (%): {stats.utilization.value}', size=13)