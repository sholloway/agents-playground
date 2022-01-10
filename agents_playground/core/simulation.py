from abc import ABC, abstractmethod
from collections import OrderedDict
from dataclasses import dataclass
from enum import Enum
from math import floor
import threading
from time import sleep
from typing import Callable, List, Optional, Tuple, Union

import dearpygui.dearpygui as dpg

from agents_playground.core.observe import Observable
from agents_playground.core.time_utilities import (
  MS_PER_SEC,
  TIME_PER_FRAME, 
  TimeInMS, 
  TimeUtilities
)
from agents_playground.core.callable_utils import CallableUtility

class SimulationEvents(Enum):
  WINDOW_CLOSED = 'WINDOW_CLOSED'

class SimulationState(Enum):
  INITIAL = 'simulation:state:initial'
  RUNNING = 'simulation:state:running'
  STOPPED = 'simulation:state:stopped'
  ENDED = 'simulation:state:ended'

SimulationStateTable = {
  SimulationState.INITIAL: SimulationState.RUNNING,
  SimulationState.RUNNING: SimulationState.STOPPED,
  SimulationState.STOPPED: SimulationState.RUNNING
}

RUN_SIM_TOGGLE_BTN_START_LABEL = 'Start'
RUN_SIM_TOGGLE_BTN_STOP_LABEL = 'Stop'

SimulationStateToLabelMap = {
  SimulationState.INITIAL: RUN_SIM_TOGGLE_BTN_START_LABEL,
  SimulationState.RUNNING: RUN_SIM_TOGGLE_BTN_STOP_LABEL,
  SimulationState.STOPPED: RUN_SIM_TOGGLE_BTN_START_LABEL
}

# TODO: Find a better home for Color
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

# TODO: SimulationContext is going to need some kind of expansion mechanism.
# There is the general context and then the simulation specific context details.
@dataclass(init=False)
class SimulationContext:
  parent_window: Size
  canvas: Size
  agent_style: AgentStyle

  def __init__(self) -> None:
    self.parent_window = Size()
    self.canvas = Size()
    self.agent_style = AgentStyle()

Tag = Union[int, float]

@dataclass
class RenderLayer:
  id: Tag
  label: str
  menu_item: Tag
  layer: Callable

class Simulation(ABC, Observable):
  _primary_window_ref: Union[int, str]

  def __init__(self) -> None:
    super().__init__()
    self._sim_current_state: SimulationState = SimulationState.INITIAL
    self._context: SimulationContext = SimulationContext()
    self._sim_window_ref = dpg.generate_uuid()
    self._sim_menu_bar_ref = dpg.generate_uuid()
    self._sim_initial_state_dl_ref = dpg.generate_uuid()
    self._buttons = {
      'sim': {
        'run_sim_toggle_btn': dpg.generate_uuid()
      }
    }
    self._stats = {
      'fps': dpg.generate_uuid(),
      'utilization': dpg.generate_uuid(),
      'cycle_duration': dpg.generate_uuid(),
      'schedule_checked_per_cycle': dpg.generate_uuid()
    }
    self._layers: OrderedDict[Tag, RenderLayer] = {}
    self._sim_run_rate: float = 0.200 #How fast to run the simulation.
    self._title: str = "Set the Simulation Title"
    self._sim_stopped_check_time: float = 0.5
    self._fps_rate: float = 0
    self._utilization_rate: float = 0

  @property
  def simulation_state(self) -> SimulationState:
    return self._sim_current_state

  @simulation_state.setter
  def simulation_state(self, next_state: SimulationState) -> None:
    self._sim_current_state = next_state

  @property
  def primary_window(self) -> Union[int, str]:
    """Returns the primary window."""
    return self._primary_window_ref

  @primary_window.setter
  def primary_window(self, primary_window_ref: Union[int, str]) -> None:
    """Assigns the primary window to the simulation window."""
    self._primary_window_ref = primary_window_ref

  @property
  def simulation_title(self) -> str:
    return self._title

  @simulation_title.setter
  def simulation_title(self, value: str) -> None:
    self._title = value

  def add_layer(self, layer: Callable, label: str) -> None:
    """Adds a layer

    Args
      - id: The layer identifier.
      - layer: The code to run to render the layer. 
      - label: The text to display in the Layers menu of the simulation toolbar.
    """
    # Makes the layer available for rendering in the draw_list.
    # Adds a toggle control in the Layers menu.
    layer_id: Tag = dpg.generate_uuid()
    menu_item_id: Tag = dpg.generate_uuid()
    self._layers[layer_id] = RenderLayer(layer_id, label, menu_item_id, layer)

  def launch(self):
    """Opens the Simulation Window"""
    parent_width: Optional[int] = dpg.get_item_width(self.primary_window)
    parent_height: Optional[int] = dpg.get_item_height(self.primary_window)

    with dpg.window(tag=self._sim_window_ref, 
      label=self.simulation_title, 
      width=parent_width, 
      height=parent_height, 
      on_close=self._handle_sim_closed):
      self._setup_menu_bar()
      if self._sim_current_state is SimulationState.INITIAL:
        self._initial_render()
      else:
        self._start_simulation()

  def _start_simulation(self):
    self._establish_context()
    self._initialize_layers()
    self._bootstrap_simulation_render()

    # Create a thread for updating the simulation.
    # Note: A daemonic thread cannot be "joined" by another thread. 
    # They are destroyed when the main thread is terminated.
    self._sim_thread = threading.Thread( #name="single-agent-thread", 
      target=self._sim_loop, 
      args=(), 
      daemon=True
    )
    self._sim_thread.start()

  def _establish_context(self) -> None:
    '''Setups the variables used by the simulation.'''
    self._context.parent_window.width = dpg.get_item_width(super().primary_window)
    self._context.parent_window.height = dpg.get_item_width(super().primary_window)
    self._context.canvas.width = self._context.parent_window.width if self._context.parent_window.width else 0
    self._context.canvas.height = self._context.parent_window.height - 40 if self._context.parent_window.height else 0
    # TODO: Make this extensible.

  def _initialize_layers(self) -> None:
    """Initializes the rendering code for each registered layer."""
    with dpg.drawlist(
      parent=self._sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height):
      for rl in self._layers.values():
        with dpg.draw_layer(tag=rl.id):
          CallableUtility.invoke(rl.layer, self._context)
  
  def _handle_sim_closed(self, sender, app_data, user_data):
    #1. Kill the simulation thread.
    self._sim_current_state = SimulationState.ENDED

    # 2. Notify the parent window that this simulation has been closed.
    super().notify(SimulationEvents.WINDOW_CLOSED.value)

  def _setup_menu_bar(self):
    with dpg.menu_bar(tag=self._sim_menu_bar_ref):
      dpg.add_button(label=SimulationStateToLabelMap[self._sim_current_state], tag=self._buttons['sim']['run_sim_toggle_btn'], callback=self._run_sim_toggle_btn_clicked)
      self._setup_layers_menu()
      self._setup_menu_bar_ext()

  def _setup_layers_menu(self) -> None:
    with dpg.menu(label="Layers"):
      rl: RenderLayer
      for rl in self._layers.values():
        dpg.add_menu_item(
          label=rl.label, 
          callback=self._toggle_layer, 
          tag=rl.menu_item, 
          check=True, 
          default_value=True, 
          user_data=rl.id)
      
  def _run_sim_toggle_btn_clicked(self, sender, item_data, user_data ):
    next_state: SimulationState = SimulationStateTable[self.simulation_state]
    next_label: str = SimulationStateToLabelMap[next_state]
    self._update_ui(sender, next_label)
    self.simulation_state = next_state

  def _update_ui(self, sender, next_label):
      dpg.set_item_label(sender, next_label)
    
      if self.simulation_state is SimulationState.INITIAL:
      # special case for starting the simulation for the first time.
        if dpg.does_item_exist(self._sim_initial_state_dl_ref):
          dpg.delete_item(self._sim_initial_state_dl_ref) 
        self._start_simulation()
  
  def _sim_loop(self, **args):
    """The thread callback that processes a simulation tick.
    
    Using the definitions in agents_playground.core.time_utilities, this enforces 
    a fixed time step of TIME_PER_FRAME assuming a constant frame rate of 
    TARGET_FRAMES_PER_SEC.

    It prevents a simulation from running faster than the target frame rate but 
    does nothing to help during a slow down.

    The function determines the current frame in a 1 second rolling window and passes
    that to the _sim_loop_tick() as the tick parameter.
    """
    current_second_start: TimeInMS = 0.0
    current_second_end: TimeInMS = current_second_start + MS_PER_SEC
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        frame_start: TimeInMS = TimeUtilities.now()
        if (frame_start > current_second_end):
          # We've started a new second. 
          current_second_start = frame_start
          current_second_end = current_second_start + MS_PER_SEC
        frame = floor((frame_start - current_second_start)/TIME_PER_FRAME) + 1
        self._sim_loop_tick(current_frame=frame)
        amount_to_sleep_ms = frame_start + TIME_PER_FRAME - TimeUtilities.now()
        amount_to_sleep_sec = amount_to_sleep_ms/MS_PER_SEC
        if (amount_to_sleep_ms > 0):
          sleep(amount_to_sleep_sec) 
      else:
        # Give the CPU a break and sleep a bit before checking if we're still paused.
        sleep(self._sim_stopped_check_time) 

  def _toggle_layer(self, sender, item_data, user_data):
    if user_data:
      if item_data:
        dpg.show_item(user_data)
      else: 
        dpg.hide_item(user_data)  

  @abstractmethod
  def _initial_render(self) -> None:
    """Define the render setup for when the simulation has been launched but not started."""

  @abstractmethod
  def _bootstrap_simulation_render(self) -> None:
    """Define the render setup for when the render is started."""

  @abstractmethod
  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""

  @abstractmethod
  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""

  