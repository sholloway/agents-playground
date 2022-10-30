"""
Single file rewrite of coroutine based simulation.
Prototyping the class design. Will break into modules if this pans out.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from email.policy import default

from multiprocessing.connection import Connection
import os
import statistics
import traceback
from types import MethodType, NoneType, SimpleNamespace
from typing import Any, Callable, Dict, List, NamedTuple, Optional, cast

import dearpygui.dearpygui as dpg
from numpy import str_
from agents_playground.agents.agent import Agent, AgentIdentity, AgentMovement, AgentPhysicality, AgentPosition, AgentState
from agents_playground.agents.direction import Direction
from agents_playground.agents.utilities import render_deselected_agent, render_selected_agent
from agents_playground.console.key_listener import select_displayable_char
from agents_playground.core.constants import DEFAULT_FONT_SIZE, UPDATE_BUDGET
from agents_playground.core.location_utilities import canvas_location_to_coord, canvas_to_cell, cell_to_canvas, location_to_cell

from agents_playground.core.observe import Observable, Observer
from agents_playground.core.performance_monitor import PerformanceMetrics, PerformanceMonitor
from agents_playground.core.privileged import require_root
from agents_playground.core.sim_loop import SimLoop, SimLoopEvent, UTILITY_UTILIZATION_WINDOW
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.callable_utils import CallableUtility
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import AABBox, CanvasLocation, CellLocation, Coordinate, Size
from agents_playground.entities.entities_registry import ENTITIES_REGISTRY
from agents_playground.renderers.color import BasicColors, Color, ColorUtilities, Colors
from agents_playground.renderers.renderers_registry import RENDERERS_REGISTRY
from agents_playground.scene.scene_builder import SceneBuilder
from agents_playground.simulation.context import ConsoleComponents, SimulationContext
from agents_playground.simulation.render_layer import RenderLayer
from agents_playground.simulation.sim_events import SimulationEvents
from agents_playground.simulation.sim_state import (
  SimulationState,
  SimulationStateTable,
  SimulationStateToLabelMap
)
from agents_playground.simulation.tag import Tag
from agents_playground.styles.agent_style import AgentStyle
from agents_playground.sys.logger import get_default_logger
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.tasks.tasks_registry import TASKS_REGISTRY

logger = get_default_logger()

@dataclass
class SimulationUIComponents:
  sim_window_ref: Tag      
  sim_menu_bar_ref: Tag    
  sim_initial_state_dl_ref: Tag
  buttons: dict                
  
  performance_panel_id: Tag 
  fps_widget_id: Tag 
  time_running_widget_id: Tag
  cpu_util_widget_id: Tag
  cpu_util_plot_id: Tag
  process_memory_used_widget_id: Tag
  process_memory_used_plot_id: Tag
  physical_memory_used_widget_id: Tag
  physical_memory_used_plot_id: Tag
  virtual_memory_used_widget_id: Tag
  virtual_memory_used_plot_id: Tag
  page_faults_widget_id: Tag
  page_faults_plot_id: Tag
  pageins_widget_id: Tag
  pageins_plot_id: Tag
    
  utility_bar_plot_id: Tag
  utility_percentiles_plot_id: Tag
  time_spent_rendering_plot_id: Tag
  time_spent_running_tasks_plot_id: Tag

  sim_action_handler: Tag

  console_layer: Tag
  console_input: Tag
  console_output: Tag

  def __init__(self, generate_uuid: Callable[..., Tag]) -> None:
    self.sim_window_ref           = generate_uuid()
    self.sim_menu_bar_ref         = generate_uuid() 
    self.sim_initial_state_dl_ref = generate_uuid() 
    self.buttons={
      'sim': {
        'run_sim_toggle_btn': generate_uuid(),
        'toggle_utility_plot_btn': generate_uuid()
      }
    }
    self.performance_panel_id           = generate_uuid() 
    self.fps_widget_id                  = generate_uuid() 
    self.time_running_widget_id         = generate_uuid() 
    self.cpu_util_widget_id             = generate_uuid() 
    self.cpu_util_plot_id               = generate_uuid() 
    self.process_memory_used_widget_id  = generate_uuid() 
    self.process_memory_used_plot_id    = generate_uuid() 
    self.physical_memory_used_widget_id = generate_uuid() 
    self.physical_memory_used_plot_id   = generate_uuid() 
    self.virtual_memory_used_widget_id  = generate_uuid() 
    self.virtual_memory_used_plot_id    = generate_uuid() 
    self.page_faults_widget_id          = generate_uuid() 
    self.page_faults_plot_id            = generate_uuid() 
    self.pageins_widget_id              = generate_uuid() 
    self.pageins_plot_id                = generate_uuid() 
    
    self.utility_bar_plot_id              = generate_uuid()
    self.utility_percentiles_plot_id      = generate_uuid()
    self.time_spent_rendering_plot_id     = generate_uuid()
    self.time_spent_running_tasks_plot_id = generate_uuid()
    self.sim_action_handler               = generate_uuid()

    self.console_layer  = generate_uuid()
    self.console_menu_item  = generate_uuid()
    self.console_input  = generate_uuid()
    self.console_output = generate_uuid()

class SimulationDefaults:
  PARENT_WINDOW_WIDTH_NOT_SET: int = 0
  PARENT_WINDOW_HEIGHT_NOT_SET: int = 0
  CANVAS_HEIGHT_BUFFER: int = 40

calculate_task_utilization = lambda duration: round((duration/UPDATE_BUDGET) * 100) 

# Todo: Find a home for this.
def agent_bbox(location: Coordinate, agent_size: Size) -> AABBox:
  pass

class NoAgent(Agent):
  """Use when an agent is not present."""
  def __init__(self) -> None:
    off_canvas = Coordinate(-1,-1)
    super().__init__(
      initial_state = AgentState(),
      style       = AgentStyle(),
      identity    = AgentIdentity(dpg.generate_uuid),
      physicality = AgentPhysicality(Size(-1,-1)),
      position    = AgentPosition(
        facing            = Direction.EAST, 
        location          = off_canvas, 
        last_location     = off_canvas, 
        desired_location  = off_canvas
      ),
      movement = AgentMovement()
    )
    
class Simulation(Observable, Observer):
  """This class may potentially replace Simulation."""
  _primary_window_ref: Tag

  def __init__(self, scene_toml: str, scene_reader = SceneReader()) -> None:
    super().__init__()
    logger.info('Simulation: Initializing')
    self._scene_toml = scene_toml
    self._context: SimulationContext = SimulationContext(dpg.generate_uuid)
    self._ui_components = SimulationUIComponents(dpg.generate_uuid)
    self._show_perf_panel: bool = False
   
    self._title: str = "Set the Simulation Title"
    self._sim_description = 'Set the Simulation Description'
    self._sim_instructions = 'Set the Simulation Instructions'
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    self._sim_loop: SimLoop | None = SimLoop(scheduler = self._task_scheduler)
    self._sim_loop.attach(self)
    self.__perf_monitor: PerformanceMonitor | None = PerformanceMonitor()
    self.__perf_receive_pipe: Optional[Connection] = None
    self._scene_reader = scene_reader
    self._selected_agent_id: Tag = None

    # Store all agent's axis-aligned bounding boxes when the sim is paused.
    self._agent_aabbs: Dict[Tag, AABBox] = {} 
    self._agent_aabbs_group_id = dpg.generate_uuid()

    self._console_active_input: str = ''

  def __del__(self) -> None:
    logger.info('Simulation deleted.')
    
  @property
  def simulation_state(self) -> SimulationState:
    if self._sim_loop is not None:
      return self._sim_loop.simulation_state
    else:
      raise Exception('SimLoop not initialized.')

  @simulation_state.setter
  def simulation_state(self, next_state: SimulationState) -> None:
    if self._sim_loop is not None:
      self._sim_loop.simulation_state = next_state
    else:
      raise Exception('SimLoop not initialized.')

  @property
  def primary_window(self) -> Tag:
    """Returns the primary window."""
    return self._primary_window_ref

  @primary_window.setter
  def primary_window(self, primary_window_ref: Tag) -> None:
    """Assigns the primary window to the simulation window."""
    self._primary_window_ref = primary_window_ref

  def launch(self):
    """Opens the Simulation Window"""
    logger.info('Simulation: Launching')
    self._load_scene()
    self._setup_console()
    parent_width: Optional[int] = dpg.get_item_width(self.primary_window)
    parent_height: Optional[int] = dpg.get_item_height(self.primary_window)
    render = self._initial_render if self._sim_loop.simulation_state is SimulationState.INITIAL else self._start_simulation
    with dpg.window(tag=self._ui_components.sim_window_ref, 
      label=self._title, 
      width=parent_width, 
      height=parent_height, 
      on_close=self._handle_sim_closed):
      self._setup_menu_bar()
      self._create_performance_panel(cast(int, parent_width))
      render()

  def _load_scene(self):
    """Load the scene data from a TOML file."""
    logger.info('Simulation: Loading Scene')
    scene_path = os.path.abspath(self._scene_toml)
    scene_data:SimpleNamespace = self._scene_reader.load(scene_path)

    # Setup UI
    self._title = scene_data.simulation.ui.title
    self._sim_description = scene_data.simulation.ui.description
    self._sim_instructions = scene_data.simulation.ui.instructions

    scene_builder: SceneBuilder = self._init_scene_builder()
    self._context.scene = scene_builder.build(scene_data)

  def _setup_console(self) -> None:
    """Setup the engine console."""
    # Add a render layer. This will always be rendered on top of everything else
    # when it is toggled on.
    renderer: Any | None = RENDERERS_REGISTRY.get('engine_console_renderer')
    self._context.scene.add_layer(
      RenderLayer(
        id        = self._ui_components.console_layer, 
        label     = 'Console',
        menu_item = self._ui_components.console_menu_item,
        layer     = renderer,
        show      = False
      )
    )

  def handle_keyboard_events(self, key_code) -> None:
    if not dpg.does_item_exist(self._ui_components.console_layer):
      return

    # Just stop is the console isn't visible.
    layer_config = dpg.get_item_configuration(self._ui_components.console_layer)
    if not layer_config['show']:
      return

    char = select_displayable_char(key_code)

    if char:
      match char:
        case 'ESC': # Close the terminal
          # dpg.configure_item(self._ui_components.console_layer, show = False)
          dpg.set_value(self._ui_components.console_menu_item, False)
        case '\b': # Delete a character
          self._console_active_input = self._console_active_input[:-1]
        case _: # Type a character
          self._console_active_input = self._console_active_input + char


      display = f'> {self._console_active_input}|'
      dpg.configure_item(self._ui_components.console_input, text = display)

    """
    - Add a > and a block for the cursor. 
    - Get typing working.
    - Figure out the background scaling issue on the console.
    - Use an ASCII block for the cursor.
      Write a loop that outputs all the chr codes from 128 to 258 to find the right code.
    """

  def _start_simulation(self):
    logger.info('Simulation: Starting simulation')
    self._establish_context()
    self._run_pre_simulation_routines()
    self._initialize_layers()
    self._start_perf_monitor()
    self._sim_loop.start(self._context)

  @require_root
  def _start_perf_monitor(self):
    self.__perf_receive_pipe = self.__perf_monitor.start(os.getpid())

  def _establish_context(self) -> None:
    '''Setups the variables used by the simulation.'''
    logger.info('Simulation: Establishing simulation context.')
    self._context.parent_window.width = dpg.get_item_width(self.primary_window)
    self._context.parent_window.height = dpg.get_item_height(self.primary_window)

    # The canvas size can optionally be driven by the scene file under scene.width and scene.height.
    if self._context.scene.canvas_size.width:
       self._context.canvas.width = self._context.scene.canvas_size.width
    elif self._context.parent_window.width:
      self._context.canvas.width = self._context.parent_window.width
    else:
      self._context.canvas.width = SimulationDefaults.PARENT_WINDOW_WIDTH_NOT_SET

    if self._context.scene.canvas_size.height:
       self._context.canvas.height = self._context.scene.canvas_size.height
    elif self._context.parent_window.height:
      self._context.canvas.height = self._context.parent_window.height - SimulationDefaults.CANVAS_HEIGHT_BUFFER
    else:
      self._context.canvas.height = SimulationDefaults.PARENT_WINDOW_HEIGHT_NOT_SET

    # Assign the widget Tags for the console.
    self._context.console = ConsoleComponents(
      input_widget  = self._ui_components.console_input, 
      output_widget = self._ui_components.console_output)

  def _initialize_layers(self) -> None:
    """Initializes the rendering code for each registered layer."""
    logger.info('Simulation: Initializing Layers')
    with dpg.item_handler_registry(tag=self._ui_components.sim_action_handler):
      dpg.add_item_clicked_handler(callback=self._clicked_callback)

    with dpg.drawlist(
      tag='sim_draw_list',
      parent=self._ui_components.sim_window_ref,
      width=self._context.canvas.width, 
      height=self._context.canvas.height):
      rl: RenderLayer
      for rl in self._context.scene.layers():
        with dpg.draw_layer(tag=rl.id, show = rl.show):
          CallableUtility.invoke(rl.layer, {'context': self._context})
  
    dpg.bind_item_handler_registry(item = 'sim_draw_list', handler_registry=self._ui_components.sim_action_handler)
  
  def _clicked_callback(self, sender, app_data):
    if not self._sim_loop.running:
      self._handle_left_mouse_click()
      self._handle_right_mouse_click()

  def _handle_left_mouse_click(self) -> None:
    if dpg.is_item_left_clicked(item = 'sim_draw_list'):
      clicked_canvas_location: CanvasLocation = dpg.get_drawing_mouse_pos()
      clicked_coordinate: Coordinate = canvas_location_to_coord(clicked_canvas_location)
    
      # Deselect any existing selected agent.
      possible_agent_already_selected: Agent = self._context.scene.agents.get(self._selected_agent_id, NoAgent())
      possible_agent_already_selected.deselect()
      render_deselected_agent(
        possible_agent_already_selected.identity.render_id, 
        possible_agent_already_selected.style.fill_color
      )
      self._selected_agent_id = None

      # Was any agents selected?
      # Brute force. Find agents by checking their AABBs. Stop on the first one.
      agent_id: Tag
      agent: Agent
      for agent_id, agent in self._context.scene.agents.items():
        if agent.physicality.aabb.point_in(clicked_coordinate):
          self._selected_agent_id = agent_id
          agent.select()        
          render_selected_agent(agent.identity.render_id, ColorUtilities.invert(agent.style.fill_color))
          break

  def _handle_right_mouse_click(self) -> None:
    if dpg.is_item_right_clicked(item = 'sim_draw_list') \
      and self._selected_agent_id is not None:
      clicked_canvas_location: CanvasLocation = dpg.get_drawing_mouse_pos()
      parent_window_pos: List[int] = dpg.get_item_pos(self._ui_components.sim_window_ref)
      x_scroll = dpg.get_x_scroll(item = self._ui_components.sim_window_ref)
      y_scroll = dpg.get_y_scroll(item = self._ui_components.sim_window_ref)

      # Note: The canvas can be shifted down if the performance panel is visible.
      perf_panel_size = dpg.get_item_rect_size(item = self._ui_components.performance_panel_id)
      perf_panel_vertical_offset = perf_panel_size[1] if self._show_perf_panel else 0
      
      num_top_menu_items    = 2 # Note: Increase this when adding top level menu items.
      height_of_menu_items  = 21
      
      sim_window_title_bar_height = 20 # Can't seem to programmatically detect this.
      sim_window_menu_bar_height  = dpg.get_item_height(item = self._ui_components.sim_menu_bar_ref)
      menu_vertical_shift         = sim_window_title_bar_height + sim_window_menu_bar_height

      with dpg.window(
        popup     = True,
        autosize  = True,
        min_size  =(160, num_top_menu_items * height_of_menu_items), # Autosize doesn't seem to handle the vertical axis.
        pos       = (
          clicked_canvas_location[0] + parent_window_pos[0] - x_scroll, 
          clicked_canvas_location[1] + parent_window_pos[1] \
            + menu_vertical_shift \
            - y_scroll \
            + perf_panel_vertical_offset
        )
      ):
        with dpg.menu(label="Agent"):
          with dpg.menu(label = 'Inspect'):
            dpg.add_menu_item(
              label     = 'Agent Properties', 
              callback  =self._handle_agent_properties_inspection,
              user_data = self._selected_agent_id
            )

        with dpg.menu(label="Scene"):
          with dpg.menu(label = 'Inspect'):
            dpg.add_menu_item(label = 'Context Viewer', callback = self._handle_launch_context_viewer)

  def _handle_sim_closed(self):
    logger.info('Simulation: Closing the simulation.')
    self.shutdown()

    # 3. Notify the parent window that this simulation has been closed.
    super().notify(SimulationEvents.WINDOW_CLOSED.value)

  def shutdown(self) -> None:
    logger.info('Simulation: Shutting down the simulation.')
    # 1. Stop the simulation thread and task scheduler.
    self.simulation_state = SimulationState.ENDED 
    self._task_scheduler.stop()

    # 2. Stop the performance monitor process if it's going.
    if self.__perf_monitor is not None:
      self.__perf_monitor.stop()
      self.__perf_monitor = None

    # 3. Kill the simulation thread.
    if self._sim_loop is not None:
      self._sim_loop.end()
      self._sim_loop = None 

    # 4. Remove dpg items that have bound callbacks to the sim instance.
    if dpg.does_item_exist(item = self._ui_components.sim_window_ref):
      dpg.delete_item(item = self._ui_components.sim_window_ref)

    # 5. Remove the reference to the simulations key components.
    self._task_scheduler.purge()
    self._pre_sim_task_scheduler.purge()

    # 5. Purge the Context Object
    self._context.purge()

  def _setup_menu_bar(self):
    logger.info('Simulation: Setting up the menu bar.')
    with dpg.menu_bar(tag=self._ui_components.sim_menu_bar_ref):
      dpg.add_button(
        label=SimulationStateToLabelMap[self._sim_loop.simulation_state], 
        tag=self._ui_components.buttons['sim']['run_sim_toggle_btn'], 
        callback=self._run_sim_toggle_btn_clicked
      )
      self._setup_layers_menu()
      dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda:dpg.toggle_viewport_fullscreen())
      dpg.add_menu_item(label='utility', callback=self._toggle_utility_graph)

  def _toggle_utility_graph(self) -> None:
    self._show_perf_panel = not self._show_perf_panel
    dpg.configure_item(self._ui_components.performance_panel_id, show=self._show_perf_panel)

  def _create_performance_panel(self, plot_width: int) -> None:
    TOOL_TIP_WIDTH = 350
    with dpg.group(tag=self._ui_components.performance_panel_id, show=self._show_perf_panel):
      with dpg.group(horizontal=True):
        dpg.add_button(tag=self._ui_components.fps_widget_id, label="FPS", width=100, height=50)
        with dpg.tooltip(parent=self._ui_components.fps_widget_id):
          dpg.add_text("Frames Per Second averaged over 120 frames.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self._ui_components.time_running_widget_id, label="Uptime", width=120, height=50)
        with dpg.tooltip(parent=self._ui_components.time_running_widget_id):
          dpg.add_text("The amount of time the simulation has been running.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("Format: dd:hh:mm:ss", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self._ui_components.cpu_util_widget_id, label="CPU", width=120, height=50)
        with dpg.tooltip(parent=self._ui_components.cpu_util_widget_id):
          dpg.add_simple_plot(tag=self._ui_components.cpu_util_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("The CPU utilization represented as a percentage.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("Can be greater than 100% in the case of the simulation utilizing multiple cores.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The utilization calculation is performed by comparing the amount of idle time reported against the amount of clock time reported.", wrap=TOOL_TIP_WIDTH)
      
        dpg.add_button(tag=self._ui_components.process_memory_used_widget_id, label="Process Memory",  width=180, height=50)
        with dpg.tooltip(parent=self._ui_components.process_memory_used_widget_id):
          dpg.add_simple_plot(tag=self._ui_components.process_memory_used_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("Unique Set Size (USS)", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The amount of memory that would be freed if the process was terminated right now.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self._ui_components.physical_memory_used_widget_id, label="Memory",  width=180, height=50)
        with dpg.tooltip(parent=self._ui_components.physical_memory_used_widget_id):
          dpg.add_simple_plot(tag=self._ui_components.physical_memory_used_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("Resident Set Size (RSS)", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The non-swapped physical memory the simulation has used.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self._ui_components.virtual_memory_used_widget_id, label="Virtual",  width=180, height=50)
        with dpg.tooltip(parent=self._ui_components.virtual_memory_used_widget_id):
          dpg.add_simple_plot(tag=self._ui_components.virtual_memory_used_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("Virtual Memory Size (VMS)", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The total amount of virtual memory used by the process.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self._ui_components.page_faults_widget_id, label="Page Faults",  width=180, height=50)
        with dpg.tooltip(parent=self._ui_components.page_faults_widget_id):
          dpg.add_simple_plot(tag=self._ui_components.page_faults_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("The number of page faults.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("Page faults are requests for more memory.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self._ui_components.pageins_widget_id, label="Pageins",  width=180, height=50)
        with dpg.tooltip(parent=self._ui_components.pageins_widget_id):
          dpg.add_simple_plot(tag=self._ui_components.pageins_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("The total number of requests for pages from a pager.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("https://www.unix.com/man-page/osx/1/vm_stat", wrap=TOOL_TIP_WIDTH)

      dpg.add_simple_plot(
        tag=self._ui_components.utility_bar_plot_id, 
        overlay='Frame Task Utility (%)',
        height=40, 
        width = plot_width,
        min_scale = 0,
        max_scale = 100
      )
      
      dpg.add_simple_plot(
        tag=self._ui_components.utility_percentiles_plot_id, 
        overlay='Frame Task Utility % Percentiles',
        height=40, 
        width = plot_width,
        histogram=True
      )
      
      dpg.add_simple_plot(
        tag=self._ui_components.time_spent_rendering_plot_id, 
        overlay='Time Spent Rendering (ms)',
        height=40, 
        width = plot_width,
      )
      
      dpg.add_simple_plot(
        tag=self._ui_components.time_spent_running_tasks_plot_id, 
        overlay='Time Spent Running Tasks (ms)',
        height=40, 
        width = plot_width,
      )

  def update(self, msg:str) -> None:
    """Receives a notification message from an observable object."""
    match msg:
      case SimLoopEvent.UTILITY_SAMPLES_COLLECTED.value:   
        if self._show_perf_panel:   
          self._update_frame_performance_metrics()
      case SimLoopEvent.TIME_TO_MONITOR_HARDWARE.value:
        self._update_fps()
        self._update_hardware_metrics()
      case SimLoopEvent.SIMULATION_STARTED.value:
        pass
      case SimLoopEvent.SIMULATION_STOPPED.value:
        pass
      case _:
        logger.error(f'Simulation.update received unexpected message: {msg}')

  def _setup_layers_menu(self) -> None:
    logger.info('Simulation: Setting up layer\'s menu.')
    with dpg.menu(label="Layers"):
      rl: RenderLayer
      for rl in self._context.scene.layers():
        dpg.add_menu_item(
          label=rl.label, 
          callback=self._toggle_layer, 
          tag=rl.menu_item, 
          check=True, 
          default_value=rl.show, 
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
      if dpg.does_item_exist(self._ui_components.sim_initial_state_dl_ref):
        dpg.delete_item(self._ui_components.sim_initial_state_dl_ref) 
      self._start_simulation()
  
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

    with dpg.drawlist(
      tag=self._ui_components.sim_initial_state_dl_ref, 
      parent=self._ui_components.sim_window_ref, 
      width=canvas_width, height=canvas_height): 
      dpg.draw_text(pos=(20,20), text=self._sim_description,  size = DEFAULT_FONT_SIZE)
      dpg.draw_text(pos=(20,40), text=self._sim_instructions, size = DEFAULT_FONT_SIZE)

  def _init_scene_builder(self) -> SceneBuilder:
    return SceneBuilder(
      id_generator = dpg.generate_uuid, 
      task_scheduler = self._task_scheduler, 
      pre_sim_scheduler = self._pre_sim_task_scheduler,
      render_map = RENDERERS_REGISTRY, 
      task_map = TASKS_REGISTRY,
      entities_map = ENTITIES_REGISTRY
    )

  def _run_pre_simulation_routines(self) -> None:
    """Runs all of the pre-simulation routines defined in the scene TOML file."""
    logger.info('Simulation: Running pre-simulation tasks.')
    self._pre_sim_task_scheduler.consume()
    logger.info('Simulation: Done running pre-simulation tasks.')

  def _update_frame_performance_metrics(self) -> None:
    per_frame_samples         = self._context.stats.per_frame_samples
    task_samples              = per_frame_samples['running-tasks'].samples
    task_utilization_samples  = list(map(calculate_task_utilization, task_samples))
  
    avg_utility = round(statistics.fmean(task_utilization_samples), 2)
    min_utility = min(task_utilization_samples)
    max_utility = max(task_utilization_samples)
    percentiles = statistics.quantiles(task_utilization_samples, n=100, method='inclusive')
    
    avg_rendering_time = round(statistics.fmean(per_frame_samples['rendering'].samples), 2)
    min_rendering_time = round(min(per_frame_samples['rendering'].samples), 2)
    max_rendering_time = round(max(per_frame_samples['rendering'].samples), 2)
    
    avg_task_time = round(statistics.fmean(task_utilization_samples), 2)
    min_task_time = round(min(task_utilization_samples), 2)
    max_task_time = round(max(task_utilization_samples), 2)
    
    dpg.set_value(
      item = self._ui_components.utility_bar_plot_id, 
      value = task_utilization_samples
    )
    
    dpg.set_value(
      item = self._ui_components.utility_percentiles_plot_id, 
      value = percentiles
    )
    
    dpg.set_value(
      item = self._ui_components.time_spent_rendering_plot_id, 
      value = per_frame_samples['rendering'].samples
    )
    
    dpg.set_value(
      item = self._ui_components.time_spent_running_tasks_plot_id, 
      value = task_samples
    )
    
    dpg.configure_item(
      self._ui_components.utility_bar_plot_id, 
      overlay=f'Frame Utility % (avg/min/max): {avg_utility}/{min_utility}/{max_utility}'
    )
    
    dpg.configure_item(
      self._ui_components.time_spent_rendering_plot_id, 
      overlay=f'Time Spent Rendering (avg/min/max): {avg_rendering_time}/{min_rendering_time}/{max_rendering_time}'
    )

    dpg.configure_item(
      self._ui_components.time_spent_running_tasks_plot_id, 
      overlay=f'Time Spent Running Tasks (avg/min/max): {avg_task_time}/{min_task_time}/{max_task_time}'
    )

  def _update_fps(self) -> None:
    if dpg.does_item_exist(self._ui_components.fps_widget_id):
      dpg.configure_item(
        self._ui_components.fps_widget_id, 
        label = f"FPS: {dpg.get_frame_rate()}"
      )

  @require_root
  def _update_hardware_metrics(self) -> None:
    # Note: Not providing a value to Pipe.poll makes it return immediately.
    try:
      if self.__perf_receive_pipe is not None and \
        self.__perf_receive_pipe.readable and \
        self.__perf_receive_pipe.poll():
        metrics: PerformanceMetrics = self.__perf_receive_pipe.recv()
        
        uptime = TimeUtilities.display_seconds(metrics.sim_running_time)
        dpg.configure_item(
          self._ui_components.time_running_widget_id,
          label = uptime
        )

        dpg.configure_item(
          self._ui_components.cpu_util_widget_id,
          label = f"CPU:{metrics.cpu_utilization.latest:.2f}"
        )

        dpg.set_value(
          item = self._ui_components.cpu_util_plot_id, 
          value = metrics.cpu_utilization.samples
        )
        
        dpg.configure_item(
          self._ui_components.process_memory_used_widget_id,
          label = f"USS: {metrics.memory_unique_to_process.latest:.2f} MB"
        )

        dpg.set_value(
          item = self._ui_components.process_memory_used_plot_id, 
          value = metrics.memory_unique_to_process.samples
        )
        
        dpg.configure_item(
          self._ui_components.physical_memory_used_widget_id,
          label = f"RSS: {metrics.non_swapped_physical_memory_used.latest:.2f} MB"
        )

        dpg.set_value(
          item = self._ui_components.physical_memory_used_plot_id, 
          value = metrics.non_swapped_physical_memory_used.samples
        )
        
        dpg.configure_item(
          self._ui_components.virtual_memory_used_widget_id,
          label = f"VMS: {metrics.virtual_memory_used.latest:.2f} MB"
        )

        dpg.set_value(
          item = self._ui_components.virtual_memory_used_plot_id, 
          value = metrics.virtual_memory_used.samples
        )
               
        dpg.configure_item(
          self._ui_components.page_faults_widget_id,
          label = f"Page Faults: {metrics.page_faults.latest}"
        )

        dpg.set_value(
          item = self._ui_components.page_faults_plot_id, 
          value = metrics.page_faults.samples
        )
        
        dpg.configure_item(
          self._ui_components.pageins_widget_id,
          label = f"Pageins: {metrics.pageins.latest}"
        )

        dpg.set_value(
          item = self._ui_components.pageins_plot_id, 
          value = metrics.pageins.samples
        )
    except EOFError as e:
      logger.error('The Performance Monitor sent an EOFError. The process may have crashed.')
      logger.error(e)
      traceback.print_exception(e)

  def _handle_agent_properties_inspection(self, sender, item_data, user_data) -> None:
    """Launches a window that provides a UI to inspect a specific agent.
    The agent is specified by setting the user_data = agent.identity.id.
    """
    selected_agent = self._context.scene.agents.get(user_data)
    assert selected_agent is not None, "Selected agent should never be none if this method is called."

    with dpg.window(label = 'Agent Inspector', width = 660, height=self._context.parent_window.height):
      self._add_tree_table(label = 'Identity', data = selected_agent.identity)
      self._add_tree_table(label = 'State', data = selected_agent.state)
      self._add_tree_table(label = 'Style', data = selected_agent.style)
      self._add_tree_table(label = 'Physicality', data = selected_agent.physicality)
      self._add_tree_table(label = 'Position', data = selected_agent.position)
      self._add_tree_table(label = 'Movement', data = selected_agent.movement)

  def _handle_launch_context_viewer(self) -> None:
    with dpg.window(label = 'Context Viewer', width = 660, height=self._context.parent_window.height):
      self._add_tree_table(
        label = 'General',
        data = { 
          'Parent Window Size': self._context.parent_window,
          'Canvas Size': self._context.canvas
        }
      )
      self._add_tree_table(label = 'Details', data = self._context.details)
      
      with dpg.tree_node(label = 'Scene'):
        self._add_tree_table(
          label = 'General', 
          data = { 
            'Cell Size': self._context.scene.cell_size,
            'Cell Center X Offset': self._context.scene.cell_center_x_offset,
            'Cell Center Y Offset': self._context.scene.cell_center_y_offset,
          }
        )

        with dpg.tree_node(label = 'Agents'):
          with dpg.table(
            header_row=True, 
            policy=dpg.mvTable_SizingFixedFit,
            row_background=True, 
            borders_innerH=True, 
            borders_outerH=True, 
            borders_innerV=True,
            borders_outerV=True
          ):
            dpg.add_table_column(label='Actions', width_fixed=True)
            dpg.add_table_column(label='Id', width_fixed=True)
            dpg.add_table_column(label='Render ID', width_fixed=True)
            dpg.add_table_column(label='TOML ID', width_fixed=True)
            dpg.add_table_column(label='AABB ID', width_fixed=True)
            dpg.add_table_column(label='Selected', width_fixed=True)
            dpg.add_table_column(label='Visible', width_fixed=True)
            dpg.add_table_column(label='Current Action State', width_fixed=True)
            dpg.add_table_column(label='Location', width_fixed=True)
            agent: Agent
            for agent in self._context.scene.agents.values():
              selected_color  = BasicColors.green.value if agent.state.selected else BasicColors.red.value
              visible_color   = BasicColors.green.value if agent.state.visible  else BasicColors.red.value
              with dpg.table_row():
                dpg.add_button(
                  label     = 'inspect', 
                  callback  =self._handle_agent_properties_inspection, 
                  user_data = agent.identity.id
                )
                dpg.add_text(agent.identity.id)
                dpg.add_text(agent.identity.render_id)
                dpg.add_text(agent.identity.toml_id)
                dpg.add_text(agent.identity.aabb_id)
                dpg.add_text(agent.state.selected, color = selected_color)
                dpg.add_text(agent.state.visible, color = visible_color)
                dpg.add_text(agent.state.current_action_state)
                dpg.add_text(agent.position.location)

        with dpg.tree_node(label = 'Entities'):
          for group_name, entity_grouping in self._context.scene.entities.items():
            rows: List[SimpleNamespace] = list(entity_grouping.values())
            self._add_table_of_namespaces(
              label = group_name, 
              columns = list(rows[0].__dict__.keys()),
              rows = rows
            )        
        
        if len(self._context.scene.nav_mesh._junctions) > 0:
          with dpg.tree_node(label = 'Navigation Mesh'):
            junction_rows: List[SimpleNamespace] = list(self._context.scene.nav_mesh.junctions())
            self._add_table_of_namespaces(
              label = 'Junctions', 
              columns = list(junction_rows[0].__dict__.keys()),
              rows = junction_rows
            )        

        self._add_tree_table(label = 'Paths',  data = self._context.scene.paths)
        self._add_tree_table(label = 'Layers', data = self._context.scene.layers)
      
  def _add_tree_table(self, label:str, data: Any) -> None:
    with dpg.tree_node(label = label):
      with dpg.table(
        header_row=True, 
        policy=dpg.mvTable_SizingFixedFit,
        row_background=True, 
        borders_innerH=True, 
        borders_outerH=True, 
        borders_innerV=True,
        borders_outerV=True
      ):
        dpg.add_table_column(label="Field", width_fixed=True)
        dpg.add_table_column(label="Value", width_stretch=True, init_width_or_weight=0.0)
        items_dict = data if isinstance(data, dict) else data.__dict__
        for k, v in items_dict.items():
          with dpg.table_row():
            dpg.add_text(k)
            match v:
              case Color():
                dpg.add_color_button(v)
              case bool():
                if v:
                  dpg.add_text(v, color=BasicColors.green.value)
                else:
                  dpg.add_text(v, color=BasicColors.red.value)
              case _ :
                dpg.add_text(v, wrap = 500)

  def _add_table_of_namespaces(
    self, 
    label:str, 
    columns: List[str], 
    rows: List[SimpleNamespace]
  ) -> None:
    with dpg.tree_node(label = label):
      with dpg.table(
        header_row=True, 
        policy=dpg.mvTable_SizingFixedFit,
        row_background=True, 
        borders_innerH=True, 
        borders_outerH=True, 
        borders_innerV=True,
        borders_outerV=True
      ):
        for col in columns:
          dpg.add_table_column(label=col, width_fixed=True)

        for row in rows: 
          with dpg.table_row():
            for v in row.__dict__.values():
              match v:
                case Color():
                  dpg.add_color_button(v)
                case bool():
                  if v:
                    dpg.add_text(v, color=BasicColors.green.value)
                  else:
                    dpg.add_text(v, color=BasicColors.red.value)
                case MethodType():
                  dpg.add_text('bound method')
                case _ :
                  dpg.add_text(v, wrap=500)