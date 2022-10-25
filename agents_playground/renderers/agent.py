
from typing import List
import dearpygui.dearpygui as dpg
from agents_playground.agents.agent import Agent
from agents_playground.core.types import Size


from agents_playground.scene.scene import Scene
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.tag import Tag
from agents_playground.styles.agent_style import AgentStyle
from agents_playground.sys.logger import get_default_logger
from agents_playground.renderers.color import Color

logger = get_default_logger()

def render_agents_in_scene(**data) -> None:
  context: SimulationContext = data['context']
  scene: Scene = context.scene
  
  for agent in scene.agents.values():
    agent_style = agent.style
    agent_size: Size = agent_style.size
    agent_width_half: float = agent_size.width / 2.0
    agent_height_half: float = agent_size.height / 2.0

    with dpg.draw_node(tag=agent.id):
      # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
      # The location of the triangle is transformed by update_all_agents_display()
      # which is called in the SimLoop.
      dpg.draw_triangle(
        tag=agent.render_id,
        p1=(agent_width_half,0), 
        p2=(-agent_width_half, -agent_height_half), 
        p3=(-agent_width_half, agent_height_half), 
        color=agent.style.stroke_color, 
        fill=agent.style.fill_color, 
        thickness=agent.style.stroke_thickness
      )

def render_agents_aabb(**data) -> None:
  context: SimulationContext = data['context']
  agent: Agent
  for agent in context.scene.agents.values():
    aabb = agent.bounding_box
    dpg.draw_rectangle(
      tag = agent.aabb_id,
      pmin = aabb.min, 
      pmax = aabb.max, 
      color = agent.style.aabb_stroke_color,
      thickness = agent.style.aabb_stroke_thickness
    )