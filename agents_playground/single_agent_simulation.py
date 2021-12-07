import math

from time import sleep
from typing import List, Optional, Tuple

import dearpygui.dearpygui as dpg

from agents_playground.agent import Agent
from agents_playground.logger import log, get_default_logger
from agents_playground.simulation import (
  Simulation, 
  SimulationState
)
from agents_playground.structures import Point

"""
What do I want here?
- [X] Top down 2D perspective.
- [X] Agent is a triangle with the tip indicating orientation.
- [X] Toggle the calculated path off and on.
- [X] Button for starting/stopping the simulation.
- [X] Have a description of what the simulation does and instructions to click 
      the start button when in the initial state.
- [X] Explicitly kill the simulation thread when the window is closed.
- [X] Pull boilerplate into simulation.py
- [X] Update to actually use the Agent definition.
- [ ] Associate the stepping of the path with the agent.
- [ ] Make the triangle rotates when changing direction.
- [ ] Unit Tests
- [ ] Some kind of landscape with obsticles to navigate.
  - Perhaps there are different "maps" that can be selected via a combo box or menu.
- Dynamically pick starting point & end point?

Questions
- Context Menus?
"""

SIM_DESCRIPTION = 'Single agent simulation of an agent following a predefined path.'
SIM_INSTRUCTIONS = 'Click the start button to begin the simulation.'

Color = Tuple[int, int, int]
AgentPath = List[Tuple[int, int]]

class SingleAgentSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self.menu_items = {
      'display': {
        'terrain': dpg.generate_uuid(),
        'path': dpg.generate_uuid()
      }
    }
    self._layers = {
      'terrain': dpg.generate_uuid(),
      'navigation_mesh': dpg.generate_uuid(),
      'path': dpg.generate_uuid(),
      'agents': dpg.generate_uuid()
    }
    self._agent_ref = dpg.generate_uuid()
    self.simulation_title = "Single Agent Simulation"
    self._cell_size = Point(20, 20)
    self._cell_center_x_offset: float = self._cell_size.x/2
    self._cell_center_y_offset: float = self._cell_size.y/2
    self._agent: Agent = Agent() # Create an agent at (0,0)
    self._path: AgentPath = [
      # Walk 5 steps East.
      (9,4), (10,4), (11,4), (12,4), (13,4), (14,4),
      # Walk 3 steps South
      (14, 5), (14, 6), (14, 7),
      # Walk 6 steps to the East
      (15, 7), (16, 7), (17, 7), (18, 7), (19, 7), (20, 7),
      # Walk 2 steps South
      (20, 8), (20, 9),
      # Walk 8 steps to the West
      (19, 9), (18, 9), (17, 9), (16, 9), (15, 9), (14, 9), (13, 9), (12, 9),
      ## Walk North 3 steps
      (12, 8), (12, 7), (12, 6), 
      # Walk West 3 Steps
      (11, 6), (10, 6), (9, 6),
      # Walk North
      (9, 5)
    ]
    self._agent.movement_strategy(build_path_walker(self._path))

  def _sim_loop(self, **args):
    """The thread callback that processes a simulation tick."""
    # For now, just have the agent step through a path.
    current_step_index: int = 0
    while self.simulation_state is not SimulationState.ENDED:
      sleep(self._sim_run_rate) 
      if self.simulation_state is SimulationState.RUNNING:
        self._agent.explore()
        location_on_grid = self._agent.location.multiply(self._cell_size)
        dpg.apply_transform(item=self._agent_ref, transform=dpg.create_translation_matrix(tuple(location_on_grid)))

  def _toggle_layer(self, sender, item_data, user_data):
    if user_data:
      if item_data:
        dpg.show_item(user_data)
      else: 
        dpg.hide_item(user_data)

  def _setup_menu_bar_ext(self):
    """Setup simulation specific menu items."""
    with dpg.menu(label="Display"):
      dpg.add_menu_item(
        label="Terrain", 
        callback=self._toggle_layer, 
        tag=self.menu_items['display']['terrain'], 
        check=True, 
        default_value=True, 
        user_data=self._layers['terrain'])
      dpg.add_menu_item(
        label="Path", 
        callback=self._toggle_layer, 
        tag=self.menu_items['display']['path'], 
        check=True, 
        default_value=True, 
        user_data=self._layers['path'])

  def _initial_render(self) -> None:
    parent_width: Optional[int] = dpg.get_item_width(super().primary_window())
    parent_height: Optional[int]  = dpg.get_item_height(super().primary_window())
    canvas_width: int = parent_width if parent_width else 0
    canvas_height: int = parent_height - 40 if parent_height else 0

    with dpg.drawlist(tag=self._sim_initial_state_dl_ref, parent=self._sim_window_ref, width=canvas_width, height=canvas_height): 
      dpg.draw_text(pos=(20,20), text=SIM_DESCRIPTION, size=13)
      dpg.draw_text(pos=(20,40), text=SIM_INSTRUCTIONS, size=13)

  def _bootstrap_simulation_render(self) -> None:
    parent_width: Optional[int] = dpg.get_item_width(super().primary_window())
    parent_height: Optional[int]  = dpg.get_item_height(super().primary_window())
    canvas_width: int = parent_width if parent_width else 0
    canvas_height: int = parent_height - 40 if parent_height else 0

    rows: int = math.floor(canvas_height/self._cell_size.y) - 1
    columns: int = math.floor(canvas_width/self._cell_size.x) - 1
    grid_background_color: Color = (255,255,255)
    grid_width = columns * self._cell_size.x
    grid_height = rows * self._cell_size.y
    grid_line_color: Color = (45, 45, 45)
    grid_line_thickness: float = 1

    # Agent Rendering Stuff
    agent_stroke_thickness: float = 1.0
    agent_stroke_color: Color = (255,255,255)
    agent_fill_color: Color = (0, 0, 255)
    agent_width: float = 20
    agent_height: float = 20
    agent_width_half: float = agent_width/2
    agent_height_half: float = agent_height/2

    with dpg.drawlist(parent=self._sim_window_ref, width=canvas_width, height=canvas_height): 
      with dpg.draw_layer(tag=self._layers['terrain']): 
        dpg.draw_rectangle(pmin=(0,0),pmax=(grid_width,grid_height), fill=grid_background_color)
        # For right now, just draw a grid.
        for row in range(rows + 1): # Draw horizontal lines
          vertical_offset = row * self._cell_size.y
          dpg.draw_line(p1=(0, vertical_offset), p2=(grid_width, vertical_offset), color=grid_line_color, thickness=grid_line_thickness)

        for col in range(columns+1): # Draw vertical lines
          horizontal_offset = col * self._cell_size.x
          dpg.draw_line(p1=(horizontal_offset, 0), p2=(horizontal_offset, grid_height), color=grid_line_color, thickness=grid_line_thickness)

      with dpg.draw_layer(tag=self._layers['navigation_mesh']): # navigation mesh?
        pass

      with dpg.draw_layer(tag=self._layers['path']): # Path
        # Transform the path of cells into canvas points.
        displayed_path: List[List[float]] = []
        for step in self._path:
          point = [
            step[0] * self._cell_size.x + self._cell_center_x_offset, 
            step[1] * self._cell_size.y + self._cell_center_y_offset
          ]
          displayed_path.append(point)
        dpg.draw_polyline(displayed_path, closed=True, color=(255,0,0))

      with dpg.draw_layer(tag=self._layers['agents']): # Agents
        with dpg.draw_node(tag=self._agent_ref):
          # Draw the triangle centered at cell (0,0) in the grid.
          dpg.draw_triangle(
            p1=(agent_width_half,0), 
            p2=(0, agent_height), 
            p3=(agent_width, agent_height), 
            color=agent_stroke_color, 
            fill=agent_fill_color, 
            thickness=agent_stroke_thickness
          )

    first_step = self._path[0]
    self._agent.move_to(Point(first_step[0], first_step[1]))
    location_on_grid = self._agent.location.multiply(self._cell_size)
    
    dpg.apply_transform(
      item=self._agent_ref, 
      transform=dpg.create_translation_matrix(tuple(location_on_grid))
    )
    
"""
Closure for an agent walking a path.
Questions
- What file should this live in?
- How do I really want to define a path? List of Points, List of Tuples?, More details: step, turn?
  Tuples are easy to define, but it's a case of writing to the feature, not an abstraction.
"""
def build_path_walker(path_to_walk: AgentPath, starting_step_index=-1):
  """A closure that enables an agent to traverse a list of points."""
  path = path_to_walk
  current_step_index = starting_step_index

  def walk_path(agent: Agent) -> None:
    nonlocal current_step_index, path
    if current_step_index < (len(path) - 1):
      current_step_index += 1
      step = path[current_step_index]
      agent.move_to(Point(step[0], step[1]))
    else:
      current_step_index = 0

  return walk_path