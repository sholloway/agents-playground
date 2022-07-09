from abc import ABC, abstractmethod
from collections import OrderedDict

from math import floor
import threading
from time import sleep
from typing import Callable, Dict, Optional,  Union

import dearpygui.dearpygui as dpg

from agents_playground.core.observe import Observable
from agents_playground.core.time_utilities import (
  MS_PER_SEC,
  TIME_PER_FRAME,
  UPDATE_BUDGET, 
  TimeInMS, 
  TimeUtilities
)
from agents_playground.core.callable_utils import CallableUtility
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.render_layer import RenderLayer
from agents_playground.simulation.sim_events import SimulationEvents
from agents_playground.simulation.sim_state import (
  SimulationState,
  SimulationStateTable,
  SimulationStateToLabelMap
)
from agents_playground.simulation.statistics import SimulationStatistics
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger

logger = get_default_logger()

class SimulationOld(ABC, Observable):
  _primary_window_ref: Union[int, str]

  def __init__(self) -> None:
    super().__init__()
    logger.info('Simulation: Initializing')
    self._sim_current_state: SimulationState = SimulationState.INITIAL
    self._context: SimulationContext = SimulationContext(dpg.generate_uuid)
    self._sim_window_ref = dpg.generate_uuid()
    self._sim_menu_bar_ref = dpg.generate_uuid()
    self._sim_initial_state_dl_ref = dpg.generate_uuid()
    self._buttons = {
      'sim': {
        'run_sim_toggle_btn': dpg.generate_uuid()
      }
    }
    self._layers: OrderedDict[Tag, RenderLayer] = OrderedDict()
    self._sim_run_rate: float = 0.200 #How fast to run the simulation.
    self._title: str = "Set the Simulation Title"
    self._sim_description = 'Set the Simulation Description'
    self._sim_instructions = 'Set the Simulation Instructions'
    self._sim_stopped_check_time: float = 0.5
    self._fps_rate: float = 0
    self._utilization_rate: float = 0
    self.add_layer(render_stats, "Statistics")

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
    logger.info('Simulation: Launching')
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
    logger.info('Simulation: Starting simulation')
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
    logger.info('Simulation: Establishing simulation context.')
    self._context.parent_window.width = dpg.get_item_width(self.primary_window)
    self._context.parent_window.height = dpg.get_item_width(self.primary_window)
    self._context.canvas.width = self._context.parent_window.width if self._context.parent_window.width else 0
    self._context.canvas.height = self._context.parent_window.height - 40 if self._context.parent_window.height else 0
    self._context.agent_style.stroke_thickness = 1.0
    self._context.agent_style.stroke_color = (255,255,255)
    self._context.agent_style.fill_color = (0, 0, 255)
    self._context.agent_style.size.width = 20
    self._context.agent_style.size.height = 20
    self._establish_context_ext(self._context)

  def _initialize_layers(self) -> None:
    """Initializes the rendering code for each registered layer."""
    logger.info('Simulation: Initializing Layers')
    with dpg.drawlist(
      parent=self._sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height):
      for rl in self._layers.values():
        with dpg.draw_layer(tag=rl.id):
          CallableUtility.invoke(rl.layer, {'context': self._context})
  
  def _handle_sim_closed(self, sender, app_data, user_data):
    logger.info('Simulation: Closing the simulation.')
    #1. Kill the simulation thread.
    self._sim_current_state = SimulationState.ENDED

    # 2. Notify the parent window that this simulation has been closed.
    super().notify(SimulationEvents.WINDOW_CLOSED.value)

  def _setup_menu_bar(self):
    logger.info('Simulation: Setting up the menu bar.')
    with dpg.menu_bar(tag=self._sim_menu_bar_ref):
      dpg.add_button(label=SimulationStateToLabelMap[self._sim_current_state], tag=self._buttons['sim']['run_sim_toggle_btn'], callback=self._run_sim_toggle_btn_clicked)
      self._setup_layers_menu()
      self._setup_menu_bar_ext()

  def _setup_layers_menu(self) -> None:
    logger.info('Simulation: Setting up layer\'s menu.')
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
    logger.info('Simulation: Simulation toggle button clicked.')
    next_state: SimulationState = SimulationStateTable[self.simulation_state]
    next_label: str = SimulationStateToLabelMap[next_state]
    self._update_ui(sender, next_label)
    self.simulation_state = next_state

  def _update_ui(self, sender, next_label):
    logger.info('Simulation: Updating UI')
    dpg.set_item_label(sender, next_label)
  
    if self.simulation_state is SimulationState.INITIAL:
    # special case for starting the simulation for the first time.
      if dpg.does_item_exist(self._sim_initial_state_dl_ref):
        dpg.delete_item(self._sim_initial_state_dl_ref) 
      self._start_simulation()
  
  def _sim_loop(self, **data):
    """The thread callback that processes a simulation tick.
    
    Using the definitions in agents_playground.core.time_utilities, this enforces 
    a fixed time step of TIME_PER_FRAME assuming a constant frame rate of 
    TARGET_FRAMES_PER_SEC.

    It prevents a simulation from running faster than the target frame rate but 
    does nothing to help during a slow down.

    The function determines the current frame in a 1 second rolling window and passes
    that to the _sim_loop_tick() as the tick parameter.
    """
    data['current_second_start'] = 0.0 # TimeInMS
    data['current_second_end'] = data['current_second_start'] + MS_PER_SEC # TimeInMS
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        self._process_sim_cycle(**data)
      else:
        # Give the CPU a break and sleep a bit before checking if we're still paused.
        sleep(self._sim_stopped_check_time) 

  def _process_sim_cycle(self, **data) -> None:
    frame_start: TimeInMS = TimeUtilities.now()
    loop_stats = {}
    if (frame_start > data['current_second_end']):
      # We've started a new second. 
      data['current_second_start'] = frame_start
      data['current_second_end'] = data['current_second_start'] + MS_PER_SEC
    frame = floor((frame_start - data['current_second_start'])/TIME_PER_FRAME) + 1
    loop_stats['time_started_running_tasks'] = TimeUtilities.now()
    self._sim_loop_tick(current_frame=frame)
    loop_stats['time_finished_running_tasks'] = TimeUtilities.now()
    self._update_statistics(loop_stats)
    amount_to_sleep_ms = frame_start + TIME_PER_FRAME - TimeUtilities.now()
    amount_to_sleep_sec = amount_to_sleep_ms/MS_PER_SEC
    if (amount_to_sleep_ms > 0):
      sleep(amount_to_sleep_sec) 

  # TODO Split the stats calculations from the rendering. 
  # Probably only need to render once a second, not every cycle.
  def _update_statistics(self, stats: dict[str, float]) -> None:
    self._context.stats.fps.value = dpg.get_frame_rate()
    self._context.stats.utilization.value = round(((stats['time_finished_running_tasks'] - stats['time_started_running_tasks'])/UPDATE_BUDGET) * 100, 2)

    # This is will cause a render. Need to be smart with how these are grouped.
    # There may be a way to do all the scene graph manipulation and configure_item
    # calls in a single buffer.
    # TODO Look at https://dearpygui.readthedocs.io/en/latest/documentation/staging.html
    dpg.configure_item(item=self._context.stats.fps.id, text=f'Frame Rate (Hz): {self._context.stats.fps.value}')
    dpg.configure_item(item=self._context.stats.utilization.id, text=f'Utilization (%): {self._context.stats.utilization.value}')  

  def _toggle_layer(self, sender, item_data, user_data):
    if user_data:
      if item_data:
        dpg.show_item(user_data)
      else: 
        dpg.hide_item(user_data)  

  def _initial_render(self) -> None:
    """Define the render setup for when the simulation has been launched but not started."""
    parent_width: Optional[int] = dpg.get_item_width(self.primary_window)
    parent_height: Optional[int]  = dpg.get_item_height(self.primary_window)
    canvas_width: int = parent_width if parent_width else 0
    canvas_height: int = parent_height - 40 if parent_height else 0

    with dpg.drawlist(tag=self._sim_initial_state_dl_ref, parent=self._sim_window_ref, width=canvas_width, height=canvas_height): 
      dpg.draw_text(pos=(20,20), text=self._sim_description, size=13)
      dpg.draw_text(pos=(20,40), text=self._sim_instructions, size=13)

  @abstractmethod
  def _bootstrap_simulation_render(self) -> None:
    """Define the render setup for when the render is started."""

  @abstractmethod
  def _sim_loop_tick(self, **args):
    """Handles one tick of the simulation."""

  @abstractmethod
  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
  
  @abstractmethod
  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""

# TODO: Find a home.
def render_stats(**data) -> None:
  """Render a text overlay of the active runtime statistics.
  
  Args:
    - 
  """
  context: SimulationContext = data['context']
  stats = context.stats
  # TODO Need to make the stats text display on top of the terrain.
  dpg.draw_text(tag=stats.fps.id, pos=(20,20), text=f'Frame Rate (Hz): {stats.fps.value}', size=13)
  dpg.draw_text(tag=stats.utilization.id, pos=(20,40), text=f'Utilization (%): {stats.utilization.value}', size=13)