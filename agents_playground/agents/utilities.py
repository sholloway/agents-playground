from typing import Union
import dearpygui.dearpygui as dpg
from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import DIR_ROTATION
from agents_playground.agents.structures import Point

def update_agent_in_scene_graph(agent: Agent, node_ref: Union[int, str], terrain_offset: Point) -> None:
    """
    Updates a given agent in the scene graph. 

    Parameters
    - agent: The agent to update in the scene graph.
    - node_ref: The DPG reference (tag id) for the node containing the agent in the scene graph.
    - terrain_offset: A point that represents the offset of 1 unit (e.g. grid cell) in the terrain.
    """
    # 1. Build a matrix for rotating the agent to be in the direction it's facing.
    rotate = dpg.create_rotation_matrix(DIR_ROTATION[agent.facing], (0,0,-1))
    
    # 2. Create a matrix for shifting from being centered at (0,0) to being in a terrain cell.
    shift_from_origin_to_cell = dpg.create_translation_matrix((10,10))

    # 3. Find the target location on terrain by projecting from cell location to 
    #    the canvas space.
    location_on_grid = agent.location.multiply(terrain_offset)

    # 4. Build a matrix for shifting from the first cell (0,0) to the target cell.
    translate = dpg.create_translation_matrix(tuple(location_on_grid))
  
    # 5. Build an affine transformation matrix by multiplying the transformation 
    #    and rotation matrices together.
    # Note: The affect of the cumulative transforation is calculated right to left.
    # So, the rotation happens, then the shift to the first cell, then the shift to 
    # the target cell.
    affine_transformation_matrix = translate * shift_from_origin_to_cell * rotate
    
    # 6. Apply the transformation to the node in the scene graph containing the agent.
    dpg.apply_transform(item=node_ref, transform=affine_transformation_matrix)

    agent.reset()