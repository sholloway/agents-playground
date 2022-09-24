
from typing import List
import dearpygui.dearpygui as dpg
from agents_playground.agents.agent import Agent

from agents_playground.agents.structures import Size
from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger
from agents_playground.renderers.color import Color

logger = get_default_logger()

def render_agents(**data) -> None:
  context: SimulationContext = data['context']
  agent_refs: List[Tag] = context.details['agent_node_refs']
  agent_size: Size = context.agent_style.size
  
  agent_width_half: float = agent_size.width / 2.0
  agent_height_half: float = agent_size.height / 2.0
  
  for agent_ref in agent_refs:
    with dpg.draw_node(tag=agent_ref):
      # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
      dpg.draw_triangle(
        p1=(agent_width_half,0), 
        p2=(-agent_width_half, -agent_height_half), 
        p3=(-agent_width_half, agent_height_half), 
        color=context.agent_style.stroke_color, 
        fill=context.agent_style.fill_color, 
        thickness=context.agent_style.stroke_thickness
      )

def render_agents_scene(**data) -> None:
  context: SimulationContext = data['context']
  scene: Scene = context.scene
  agent_size: Size = context.agent_style.size
  
  agent_width_half: float = agent_size.width / 2.0
  agent_height_half: float = agent_size.height / 2.0
  
  for agent in scene.agents.values():
    with dpg.draw_node(tag=agent.id):
      # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
      # The location of the triangle is transformed by update_all_agents_display()
      # which is called in the SimLoop.
      dpg.draw_triangle(
        tag=agent.render_id,
        p1=(agent_width_half,0), 
        p2=(-agent_width_half, -agent_height_half), 
        p3=(-agent_width_half, agent_height_half), 
        color=context.agent_style.stroke_color, 
        # color=agent.crest,
        # fill=agent.crest, 
        fill = None,
        thickness=context.agent_style.stroke_thickness
      )