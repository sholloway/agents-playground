"""
Module that contains renderers for drawing circles.
"""
import dearpygui.dearpygui as dpg

from agents_playground.legacy.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext


def simple_circle_renderer(self, context: SimulationContext) -> None:
  dpg.draw_circle(
    tag=self.id, 
    center = self.location, 
    radius=self.active_radius, 
    color=self.color, 
    fill=self.fill)