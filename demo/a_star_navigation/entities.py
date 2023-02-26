from agents_playground.project.extensions import register_entity

"""
Module that defines the update functions for entities in the Our Town simulation.
"""
import dearpygui.dearpygui as dpg

from agents_playground.scene.scene import Scene

@register_entity(label='ot_update_building')
def update_building(self, scene: Scene) -> None:
  pass

@register_entity(label='ot_update_interstate')
def update_interstate(self, scene: Scene) -> None:
  pass

@register_entity(label='ot_update_junction_nodes')
def update_junction_nodes(self, scene: Scene) -> None:
  pass