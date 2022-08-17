"""
Module that contains renderers for the Out Town simulation.
"""
import dearpygui.dearpygui as dpg

from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext


def building_renderer(self, context: SimulationContext) -> None:
  # Need to convert the building's width, height, and location values into pmin/pmax.
  # Location on a building is the upper left corner. DPG has the origin of [0,0]
  # at the upper left corner of the screen.

  dpg.draw_rectangle(
    tag=self.id, 
    pmin=self.location,
    pmax=(self.location[0] + self.width, self.location[1] + self.height),
    color=self.color, 
    fill=self.fill)