from typing import NamedTuple, Optional, Tuple, Union
from dataclasses import dataclass

import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.core.event_based_simulation import EventBasedSimulation
from agents_playground.agents.structures import Point
from agents_playground.agents.utilities import update_agent_in_scene_graph

SIM_DESCRIPTION = 'Event based agent simulation.'
SIM_INSTRUCTIONs = 'Click the start button to begin the simulation.'

# TODO: Find a home for these.
Color = Tuple[int, int, int]

@dataclass(init=False)
class Size:
  width: Union[None, int, float]
  height: Union[None, int, float]

@dataclass(init=False)
class AgentStyle:
  stroke_thickness: float
  stroke_color: Color
  fill_color: Color 
  size: Size 

  def __init__(self) -> None:
    self.size = Size()

@dataclass(init=False)
class SimulationContext:
  parent_window: Size
  canvas: Size
  agent_style: AgentStyle

  def __init__(self) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.agent_style = AgentStyle()

class EventBasedAgentsSim(EventBasedSimulation):
  def __init__(self) -> None:
    super().__init__()
    self._agent: Agent = Agent()
    self._context: SimulationContext = SimulationContext()
    self._layers = {
      'agents': dpg.generate_uuid()
    }
    self._agent_ref: Union[int, str] = dpg.generate_uuid()
    self._cell_size = Point(20, 20)
  
  def _initial_render(self) -> None:
    self._context.parent_window.width = dpg.get_item_width(super().primary_window)
    self._context.parent_window.height = dpg.get_item_width(super().primary_window)
    self._context.canvas.width = self._context.parent_window.width if self._context.parent_window.width else 0
    self._context.canvas.height = self._context.parent_window.height - 40 if self._context.parent_window.height else 0

    with dpg.drawlist(
      tag=self._sim_initial_state_dl_ref, 
      parent=self._sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height): 
      dpg.draw_text(pos=(20,20), text=SIM_DESCRIPTION, size=13)
      dpg.draw_text(pos=(20,40), text=SIM_INSTRUCTIONs, size=13)

  def _bootstrap_simulation_render(self) -> None:
    self._context.agent_style.stroke_thickness = 1.0
    self._context.agent_style.stroke_color = (255,255,255)
    self._context.agent_style.fill_color = (0, 0, 255)
    self._context.agent_style.size.width = 20
    self._context.agent_style.size.height = 20
    agent_half_size: Size = Size()
    agent_half_size.width = self._context.agent_style.size.width / 2
    agent_half_size.height = self._context.agent_style.size.height / 2

    with dpg.drawlist(
      parent=self._sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height): 
      with dpg.draw_layer(tag=self._layers['agents']): # Agents
        with dpg.draw_node(tag=self._agent_ref):
          # Draw the triangle centered at cell (0,0) in the grid and pointing EAST.
          dpg.draw_triangle(
            p1=(agent_half_size.width,0), 
            p2=(-agent_half_size.width, -agent_half_size.height), 
            p3=(-agent_half_size.width, agent_half_size.height), 
            color=self._context.agent_style.stroke_color, 
            fill=self._context.agent_style.fill_color, 
            thickness=self._context.agent_style.stroke_thickness
          )
    
    self._agent.move_to(Point(10, 10))
    update_agent_in_scene_graph(self._agent, self._agent_ref, self._cell_size)

  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""
    pass

  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
    pass

  