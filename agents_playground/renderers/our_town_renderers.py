"""
Module that contains renderers for the Out Town simulation.
"""
import dearpygui.dearpygui as dpg

from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext


def ot_building_renderer(self, context: SimulationContext) -> None:
  # Need to convert the building's width, height, and location values into pmin/pmax.
  min_x, min_y = 10, 400
  max_x, max_y = 300, 10
  lower_left_corner = (min_x, min_y)
  upper_right_corner = (max_x, max_y)

  dpg.draw_rectangle(
    tag=self.id, 
    pmin=lower_left_corner,
    pmax=upper_right_corner,
    color=self.color, 
    fill=self.fill)