import math
import threading
from time import sleep, perf_counter
from typing import Optional
from enum import Enum

import dearpygui.dearpygui as dpg

from simulation import Simulation, SimulationEvents

"""
What do I want here?
- [X] Top down 2D perspective.
- [X] Agent is a triangle with the tip indicating orientation.
- [X] Toggle the calculated path off and on.
- [X] Button for starting/stopping the simulation.
- [ ] Have a description of what the simulation does and instructions to click 
      the start button when in the initial state.
- [ ] The triangle rotates when changing direction.
- [ ] Some kind of landscape with obsticles to navigate.
  - Perhaps there are different "maps" that can be selected via a combo box or menu.
- Dynamically pick starting point & end point?

Questions
- Context Menus?
"""
RUN_SIM_TOGGLE_BTN_START_LABEL = 'Start'
RUN_SIM_TOGGLE_BTN_STOP_LABEL = 'Stop'

# TODO: Move to simulation.py
class SimulationState(Enum):
  INITIAL = 'simulation:state:initial'
  RUNNING = 'simulation:state:running'
  STOPPED = 'simulation:state:stopped'

SimulationStateTable = {
  SimulationState.INITIAL: SimulationState.RUNNING,
  SimulationState.RUNNING: SimulationState.STOPPED,
  SimulationState.STOPPED: SimulationState.RUNNING
}

SimulationStateToLabelMap = {
  SimulationState.INITIAL: RUN_SIM_TOGGLE_BTN_START_LABEL,
  SimulationState.RUNNING: RUN_SIM_TOGGLE_BTN_STOP_LABEL,
  SimulationState.STOPPED: RUN_SIM_TOGGLE_BTN_START_LABEL
}

class SingleAgentSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
    self._sim_current_state: SimulationState = SimulationState.INITIAL
    self._buttons = {
      'sim': {
        'run_sim_toggle_btn': dpg.generate_uuid()
      }
    }
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
    self._title = "Single Agent Simulation"
    self._cell_width: int = 20
    self._cell_height: int = 20
    self._cell_center_x_offset: float = self._cell_width/2
    self._cell_center_y_offset: float = self._cell_height/2
    self._path = [
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

  def launch(self):
    parent_width: Optional[int] = dpg.get_item_width(super().primary_window())
    parent_height: Optional[int]  = dpg.get_item_height(super().primary_window())
    canvas_width: int = parent_width if parent_width else 0
    canvas_height: int = parent_height - 40 if parent_height else 0

    rows: int = math.floor(canvas_height/self._cell_height) - 1
    columns: int = math.floor(canvas_width/self._cell_width) - 1
    grid_background_color = (255,255,255)
    grid_width = columns*self._cell_width
    grid_height = rows*self._cell_height
    grid_line_color = (0, 0, 0)
    grid_line_thickness: float = 1

    # Agent stuff
    agent_stroke_thickness: float = 1.0
    agent_stroke_color = (255,255,255)
    agent_fill_color = (0, 0, 255)
    agent_width: float = 20
    agent_height: float = 20
    agent_width_half: float = agent_width/2
    agent_height_half: float = agent_height/2

    with dpg.window(label=self._title, width=parent_width, height=parent_height, on_close=self._handle_sim_closed):
      with dpg.menu_bar():
        dpg.add_button(label=RUN_SIM_TOGGLE_BTN_START_LABEL, tag=self._buttons['sim']['run_sim_toggle_btn'], callback=self._run_sim_toggle_btn_clicked)
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

      with dpg.drawlist(width=canvas_width, height=canvas_height): 
        with dpg.draw_layer(tag=self._layers['terrain']): 
          dpg.draw_rectangle(pmin=(0,0),pmax=(grid_width,grid_height), fill=grid_background_color)
          # For right now, just draw a grid.
          for row in range(rows + 1): # Draw horizontal lines
            vertical_offset = row * self._cell_height
            dpg.draw_line(p1=(0, vertical_offset), p2=(grid_width, vertical_offset), color=grid_line_color, thickness=grid_line_thickness)

          for col in range(columns+1): # Draw vertical lines
            horizontal_offset = col * self._cell_width
            dpg.draw_line(p1=(horizontal_offset, 0), p2=(horizontal_offset, grid_height), color=grid_line_color, thickness=grid_line_thickness)

        with dpg.draw_layer(tag=self._layers['navigation_mesh']): # navigation mesh?
          pass

        with dpg.draw_layer(tag=self._layers['path']): # Path
          # Transform the path of cells into canvas points.
          displayed_path = []
          for step in self._path:
            point = [
              step[0] * self._cell_width + self._cell_center_x_offset, 
              step[1] * self._cell_height + self._cell_center_y_offset
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
              thickness=agent_stroke_thickness)

    # Create a thread for updating the simulation.
    sim_thread = threading.Thread(name="single-agent-thread", target=self._sim_loop, args=(), daemon=True)
    sim_thread.start()

  def _handle_sim_closed(self, sender, app_data, user_data):
    super().notify(SimulationEvents.WINDOW_CLOSED.value)

  def _sim_loop(self, **args):
    # For now, just have the agent step through a path.
    current_step: int = 0
    while True:
      sleep(0.200) 
      if self._sim_current_state is SimulationState.RUNNING:
        if current_step < len(self._path) - 1:
          current_step += 1
        else:
          current_step = 0
        
        next_location = (self._path[current_step][0] * self._cell_width, self._path[current_step][1] * self._cell_height)
        dpg.apply_transform(item=self._agent_ref, transform=dpg.create_translation_matrix(next_location))

  def _toggle_layer(self, sender, item_data, user_data):
    print(f'Sender: {sender} | Item Data: {item_data} | User Data: {user_data}')
    if user_data:
      if item_data:
        dpg.show_item(user_data)
      else: 
        dpg.hide_item(user_data)

  def _run_sim_toggle_btn_clicked(self, sender, item_data, user_data ):
    next_state: SimulationState = SimulationStateTable[self._sim_current_state]
    next_label: str = SimulationStateToLabelMap[next_state]
    self._sim_current_state = next_state
    dpg.set_item_label(sender, next_label)