import math
import threading
from time import sleep, perf_counter
from typing import Optional

import dearpygui.dearpygui as dpg

from simulation import Simulation, SimulationEvents

"""
What do I want here?
- Top down 2D perspective.
- Agent is a triangle with the tip indicating orientation.
- Button for starting/stopping the simulation.
- Some kind of landscape with obsticles to navigate.
  - Perhaps there are different "maps" that can be selected via a combo box or menu.
- Toggle the calculated path off and on.
- Dynamically pick starting point & end point?

Questions
- How do layer's work?
- Adding a background color to a drawlist.
- Context Menus?
"""
class SingleAgentSimulation(Simulation):
  def __init__(self) -> None:
    super().__init__()
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

    # Starting point cell[9,4] -> Cell 10,5
    agent_starting_point = (9 * self._cell_width, 4 * self._cell_height)
    
    with dpg.window(label=self._title, width=parent_width, height=parent_height, on_close=self._handle_sim_closed):
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
          pass

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

      # Move the agent to it's starting point
      dpg.apply_transform(item=self._agent_ref, transform=dpg.create_translation_matrix(agent_starting_point))

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
      if current_step < len(self._path) - 1:
        current_step += 1
      else:
        current_step = 0
      
      next_location = (self._path[current_step][0] * self._cell_width, self._path[current_step][1] * self._cell_height)
      dpg.apply_transform(item=self._agent_ref, transform=dpg.create_translation_matrix(next_location))