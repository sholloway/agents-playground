import dearpygui.dearpygui as dpg

from math import atan2
from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import DIR_ROTATION
from agents_playground.core.types import Coordinate, Size
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag

def update_all_agents_display(scene: Scene) -> None:
  render_changed = lambda a: a.agent_render_changed
  scene_graph_changed = lambda a: a.agent_scene_graph_changed
  anything_changed = lambda a: a.agent_render_changed or a.agent_scene_graph_changed

  # Update the display of all the agents that have changed.
  agent: Agent
  for agent in filter(render_changed, scene.agents.values()):
    # dpg.configure_item(agent.render_id, fill = agent.crest)
    dpg.configure_item(agent.id, show = agent.visible)

  # Update the location of all the agents that have changed in the scene graph.
  for agent in filter(scene_graph_changed, scene.agents.values()):
    update_agent_in_scene_graph(agent, agent.id, scene.cell_size)

  # Reset all the agents
  for agent in filter(anything_changed, scene.agents.values()):
    agent.reset()

def update_agent_in_scene_graph(agent: Agent, node_ref: Tag, terrain_offset: Size) -> None:
  """
  Updates a given agent in the scene graph. 

  Parameters
  - agent: The agent to update in the scene graph.
  - node_ref: The DPG reference (tag id) for the node containing the agent in the scene graph.
  - terrain_offset: A point that represents the offset of 1 unit (e.g. grid cell) in the terrain.
  """
  # 1. Build a matrix for rotating the agent to be in the direction it's facing.
  facing = agent.facing
  radians = atan2(facing.j, facing.i)
  rotate = dpg.create_rotation_matrix(radians, (0,0,1))
  
  # 2. Create a matrix for shifting from being centered at (0,0) to being in a terrain cell.
  shift_from_origin_to_cell = dpg.create_translation_matrix((10,10))

  # 3. Find the target location on terrain by projecting from cell location to 
  #    the canvas space.
  location_on_grid = agent.location.multiply(Coordinate(terrain_offset.width, terrain_offset.height))

  # 4. Build a matrix for shifting from the first cell (0,0) to the target cell.
  translate = dpg.create_translation_matrix(tuple(location_on_grid))

  # 5. Build an affine transformation matrix by multiplying the transformation 
  #    and rotation matrices together.
  # Note: The affect of the cumulative transformation is calculated right to left.
  # So, the rotation happens, then the shift to the first cell, then the shift to 
  # the target cell.
  affine_transformation_matrix = translate * shift_from_origin_to_cell * rotate
  
  # 6. Apply the transformation to the node in the scene graph containing the agent.
  if dpg.does_item_exist(item=node_ref):
    dpg.apply_transform(item=node_ref, transform=affine_transformation_matrix)