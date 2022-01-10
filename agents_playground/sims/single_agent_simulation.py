import itertools
import math
from typing import List, Optional, Sized, Tuple, Union, cast

import dearpygui.dearpygui as dpg

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Direction, DIR_ROTATION
from agents_playground.agents.path import AgentAction, AgentPath, AgentStep, IdleStep
from agents_playground.agents.structures import Point
from agents_playground.core.simulation import (
  Simulation,
  SimulationContext, 
  SimulationState,
  Size
)
from agents_playground.sys.logger import log, get_default_logger
from agents_playground.agents.utilities import update_agent_in_scene_graph

SIM_DESCRIPTION = 'Single agent simulation of an agent following a predefined path.'
SIM_INSTRUCTIONs = 'Click the start button to begin the simulation.'

Color = Tuple[int, int, int]

def s(x: int, y: int, dir: Optional[Direction] = None, cost: int = 5) -> List[AgentAction]:
  """Convenance function for building a path step.
  
  Args:
    x: The tile/cell horizontal location to move to in the step.
    y: The tile/cell vertical location to move to in the step.
    dir: The direction the agent should face. 
    cost: The number of frames the step should take to complete.

  Returns:
    A list of actionable steps. 
  """
  steps: List[AgentAction] = []
  for _ in range(cost):
    steps.append(IdleStep())
  steps.append(AgentStep(Point(x,y), dir))
  return steps

class SingleAgentSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self.menu_items = {
      'display': {
        'terrain': dpg.generate_uuid(),
        'path': dpg.generate_uuid()
      }
    }
    self._agent_ref: Union[int, str] = dpg.generate_uuid()
    self.simulation_title = "Single Agent simulation"
    self._cell_size = Point(20, 20)
    self._cell_center_x_offset: float = self._cell_size.x/2
    self._cell_center_y_offset: float = self._cell_size.y/2
    self._agent: Agent = Agent() # Create an agent at (0,0)
    self._path: AgentPath = self._build_path()
    self._agent.movement_strategy(build_path_walker(self._path))
    self.add_layer(render_terrain_layer, 'Terrain')
    self.add_layer(render_navigation_mesh_layer, 'Navigation Mesh')
    self.add_layer(render_path_layer, 'Path')
    self.add_layer(render_agents_layer, 'Agents')

  def _build_path(self) -> AgentPath:
    path = [
      # Walk 5 steps East.
      s(9,4, Direction.EAST,0), s(10,4), s(11,4), s(12,4), s(13,4), s(14,4),
      # Walk 3 steps south
      s(14, 5, Direction.SOUTH), s(14, 6), s(14, 7),
      # Walk 6 steps to the East
      s(15, 7, Direction.EAST), s(16, 7), s(17, 7), s(18, 7), s(19, 7), s(20, 7),
      # Walk 2 steps south
      s(20, 8, Direction.SOUTH), s(20, 9),
      # Walk 8 steps to the West
      s(19, 9, Direction.WEST, 0), s(18, 9, Direction.WEST, 0), s(17, 9, Direction.WEST, 0), s(16, 9, Direction.WEST, 0), s(15, 9, Direction.WEST, 0), s(14, 9, Direction.WEST, 0), s(13, 9, Direction.WEST, 0), s(12, 9, Direction.WEST, 0),
      ## Walk North 3 steps
      s(12, 8, Direction.NORTH), s(12, 7), s(12, 6), 
      # Walk West 3 steps
      s(11, 6, Direction.WEST), s(10, 6), s(9, 6),
      # Walk North
      s(9, 5, Direction.NORTH)
    ]
    return list(itertools.chain.from_iterable(path))

  def _sim_loop_tick(self, **data):
    """Handles one tick of the simulation."""
    self._agent.explore(**data)
    update_agent_in_scene_graph(self._agent, self._agent_ref, self._cell_size)

  def _setup_menu_bar_ext(self):
    pass

  def _initial_render(self) -> None:
    parent_width: Optional[int] = dpg.get_item_width(super().primary_window)
    parent_height: Optional[int]  = dpg.get_item_height(super().primary_window)
    canvas_width: int = parent_width if parent_width else 0
    canvas_height: int = parent_height - 40 if parent_height else 0

    with dpg.drawlist(tag=self._sim_initial_state_dl_ref, parent=self._sim_window_ref, width=canvas_width, height=canvas_height): 
      dpg.draw_text(pos=(20,20), text=SIM_DESCRIPTION, size=13)
      dpg.draw_text(pos=(20,40), text=SIM_INSTRUCTIONs, size=13)

  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    context.details['cell_size'] = self._cell_size
    context.details['path'] = self._path

    context.details['cell_center_x_offset'] = self._cell_center_x_offset
    context.details['cell_center_y_offset'] = self._cell_center_y_offset
    context.details['agent_ref'] = self._agent_ref

  def _bootstrap_simulation_render(self) -> None:
    first_step = self._path[0]
    first_step.run(self._agent)
    update_agent_in_scene_graph(self._agent, self._agent_ref, self._cell_size)
    
def build_path_walker(path_to_walk: AgentPath, starting_step_index=-1):
  """A closure that enables an agent to traverse a list of points.
  
  Args:
    path_to_walk: The path the agent will traverse.
    starting_step_index: The index of the step the agent starts on.
  """
  path:AgentPath = path_to_walk
  step_index = starting_step_index

  def walk_path(agent: Agent, **data) -> None:
    """Simulates the agent walking down a determined path.
    
    An agent travels at the speed of 1 cell per 3 frames.

    Args:
      agent: The agent that this function is bound to.
      data: Dictionary catch all for additional args.
    """
    nonlocal step_index, path
    step_index = step_index + 1 if step_index < len(path) - 1 else 0
    step = path[step_index]
    step.run(agent)

  return walk_path

# TODO: Move these to a static class so I can reuse some of them across sims. 
def render_terrain_layer(**data) -> None:
  context = data['context']
  cell_size = context.details['cell_size']
  rows: int = math.floor(context.canvas.height/cell_size.y) - 1
  columns: int = math.floor(context.canvas.width/cell_size.x) - 1
  grid_background_color: Color = (255,255,255)
  grid_width = columns * cell_size.x
  grid_height = rows * cell_size.y
  grid_line_color: Color = (45, 45, 45)
  grid_line_thickness: float = 1

  dpg.draw_rectangle(pmin=(0,0),pmax=(grid_width, grid_height), fill=grid_background_color)
  # For right now, just draw a grid.
  for row in range(rows + 1): # Draw horizontal lines
    vertical_offset = row * cell_size.y
    dpg.draw_line(
      p1=(0, vertical_offset), 
      p2=(grid_width, vertical_offset), 
      color=grid_line_color, 
      thickness=grid_line_thickness
    )

  for col in range(columns+1): # Draw vertical lines
    horizontal_offset = col * cell_size.x
    dpg.draw_line(
      p1=(horizontal_offset, 0), 
      p2=(horizontal_offset, grid_height), 
      color=grid_line_color, 
      thickness=grid_line_thickness
    )

def render_navigation_mesh_layer(**data) -> None:
  pass

def render_path_layer(**data) -> None:
  context = data['context']
  cell_size = context.details['cell_size']
  path = context.details['path']
  cell_center_x_offset = context.details['cell_center_x_offset']
  cell_center_y_offset = context.details['cell_center_y_offset']

  # Transform the path of cells into canvas points.
  displayed_path: List[List[float]] = []
  for step in path:
    if isinstance(step, AgentStep) and step.location:
      point = [
        step.location.x * cell_size.x + cell_center_x_offset, 
        step.location.y * cell_size.y + cell_center_y_offset
      ]
      displayed_path.append(point)
  dpg.draw_polyline(displayed_path, closed=True, color=(255,0,0))

def render_agents_layer(**data) -> None:
  context: SimulationContext = data['context']
  agent_ref = context.details['agent_ref']
  agent_size: Size = context.agent_style.size
  
  agent_width_half: float = agent_size.width / 2.0
  agent_height_half: float = agent_size.height / 2.0
  
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