"""
Module that defines functions for working with a pulsing circle.
"""
import dearpygui.dearpygui as dpg

from agents_playground.scene.scene import Scene

def update_active_radius(self, scene: Scene) -> None:
  circle = scene.entities[self.entity_grouping][self.toml_id]
  if dpg.does_item_exist(circle.id):
    dpg.configure_item(circle.id, radius = circle.active_radius)