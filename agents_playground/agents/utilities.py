from typing import cast
import dearpygui.dearpygui as dpg

from math import atan2

from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.core.types import Size
from agents_playground.renderers.color import Color
from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag
from agents_playground.spatial.types import Coordinate
from agents_playground.spatial.vector2d import Vector2d

def update_all_agents_display(scene: Scene) -> None:
  render_changed = lambda a: a.agent_render_changed
  scene_graph_changed = lambda a: a.agent_scene_graph_changed
  anything_changed = lambda a: a.agent_render_changed or a.agent_scene_graph_changed

  # Update the display of all the agents that have changed.
  agent: AgentLike
  for agent in filter(render_changed, scene.agents.values()):
    dpg.configure_item(agent.identity.id,      show = agent.agent_state.visible)
    dpg.configure_item(agent.identity.aabb_id, show = agent.agent_state.visible)

  # Update the location of all the agents that have changed in the scene graph.
  for agent in filter(scene_graph_changed, scene.agents.values()):
    update_agent_in_scene_graph(agent, agent.identity.id, scene.cell_size)

  # Reset all the agents
  for agent in filter(anything_changed, scene.agents.values()):
    agent.reset()

def update_agent_in_scene_graph(agent: AgentLike, node_ref: Tag, terrain_offset: Size) -> None:
  """
  Updates a given agent in the scene graph. 

  Parameters
  - agent: The agent to update in the scene graph.
  - node_ref: The DPG reference (tag id) for the node containing the agent in the scene graph.
  - terrain_offset: A point that represents the offset of 1 unit (e.g. grid cell) in the terrain.
  """
  # Scale the agent if there is a scaling factor. 
  scaling = agent.physicality.scale_factor
  scale = dpg.create_scale_matrix((scaling, scaling))

  # 1. Build a matrix for rotating the agent to be in the direction it's facing.
  facing: Vector2d = cast(Vector2d, agent.position.facing)
  radians = atan2(facing.j, facing.i)
  rotate = dpg.create_rotation_matrix(radians, (0,0,1))
  
  # 2. Create a matrix for shifting from being centered at (0,0) to being in a terrain cell.
  # BUG: This needs to be driven by the actual cell size!
  # If the cell size isn't 20x20 then this will cause graphical skew.
  shift_from_origin_to_cell = dpg.create_translation_matrix((10,10))

  # 3. Find the target location on terrain by projecting from cell location to 
  #    the canvas space.
  location_on_grid = agent.position.location.multiply(Coordinate(terrain_offset.width, terrain_offset.height))

  # 4. Build a matrix for shifting from the first cell (0,0) to the target cell.
  translate = dpg.create_translation_matrix(tuple(location_on_grid))

  # 5. Build an affine transformation matrix by multiplying the transformation 
  #    and rotation matrices together.
  # Note: The affect of the cumulative transformation is calculated right to left.
  # So, the rotation happens, then the shift to the first cell, then the shift to 
  # the target cell.
  affine_transformation_matrix = translate * shift_from_origin_to_cell * rotate * scale
  
  # 6. Apply the transformation to the node in the scene graph containing the agent.
  if dpg.does_item_exist(item = node_ref):
    dpg.apply_transform(item = node_ref, transform=affine_transformation_matrix)

  # 7. Update the agent's AABB corresponding rectangle's location.
  if dpg.does_item_exist(item = agent.identity.aabb_id):
    dpg.configure_item(
      agent.identity.aabb_id, 
      pmin = agent.physicality.aabb.min.coordinates, 
      pmax = agent.physicality.aabb.max.coordinates
    )

  # 9. Update the agent's View Frustum
  if dpg.does_item_exist(item = cast(int,agent.identity.frustum_id)):
    dpg.configure_item(
      item  = cast(int,agent.identity.frustum_id), 
      points = [
        [*agent.physicality.frustum.vertices[0].coordinates], 
        [*agent.physicality.frustum.vertices[1].coordinates], 
        [*agent.physicality.frustum.vertices[2].coordinates], 
        [*agent.physicality.frustum.vertices[3].coordinates]
      ]
    )

def render_selected_agent(render_id: Tag, color: Color) -> None:
  if render_id is not None and dpg.does_item_exist(item=render_id):
    dpg.configure_item(item = render_id, fill = color)

def render_deselected_agent(render_id: Tag, color: Color) -> None:
  if render_id is not None and dpg.does_item_exist(item=render_id):
    dpg.configure_item(render_id, fill = color)