"""
Single file rewrite of coroutine based simulation.
Prototyping the class design. Will break into modules if this pans out.
"""
from __future__ import annotations

from multiprocessing.connection import Connection
import os
import statistics
from types import NoneType, SimpleNamespace
from typing import NamedTuple, Optional, cast

import dearpygui.dearpygui as dpg
from agents_playground.core.constants import UPDATE_BUDGET

from agents_playground.core.observe import Observable, Observer
from agents_playground.core.performance_monitor import PerformanceMetrics, PerformanceMonitor
from agents_playground.core.sim_loop import SimLoop, SimLoopEvent, UTILITY_UTILIZATION_WINDOW
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.callable_utils import CallableUtility
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.entities.entities_registry import ENTITIES_REGISTRY
from agents_playground.renderers.color import BasicColors, Color
from agents_playground.renderers.renderers_registry import RENDERERS_REGISTRY
from agents_playground.scene.scene_builder import SceneBuilder
from agents_playground.simulation.context import SimulationContext
from agents_playground.simulation.render_layer import RenderLayer
from agents_playground.simulation.sim_events import SimulationEvents
from agents_playground.simulation.sim_state import (
  SimulationState,
  SimulationStateTable,
  SimulationStateToLabelMap
)
from agents_playground.simulation.tag import Tag
from agents_playground.sys.logger import get_default_logger
from agents_playground.scene.scene_reader import SceneReader
from agents_playground.tasks.tasks_registry import TASKS_REGISTRY

logger = get_default_logger()

class SimulationUIComponents(NamedTuple):
  sim_window_ref: Tag
  sim_menu_bar_ref: Tag
  sim_initial_state_dl_ref: Tag
  buttons: dict

class SimulationDefaults:
  PARENT_WINDOW_WIDTH_NOT_SET: int = 0
  PARENT_WINDOW_HEIGHT_NOT_SET: int = 0
  CANVAS_HEIGHT_BUFFER: int = 40
  AGENT_STYLE_STROKE_THICKNESS: float =2.0
  AGENT_STYLE_STROKE_COLOR: Color = BasicColors.black.value
  AGENT_STYLE_FILL_COLOR: Color = BasicColors.blue.value
  AGENT_STYLE_SIZE_WIDTH: int = 20
  AGENT_STYLE_SIZE_HEIGHT: int = 20

calculate_task_utilization = lambda duration: round((duration/UPDATE_BUDGET) * 100) 

class Simulation(Observable, Observer):
  """This class may potentially replace Simulation."""
  _primary_window_ref: Tag

  def __init__(self, scene_toml: str, scene_reader = SceneReader(), ) -> None:
    super().__init__()
    logger.info('Simulation: Initializing')
    self._scene_toml = scene_toml
    self._context: SimulationContext = SimulationContext(dpg.generate_uuid)
    self._ui_components = SimulationUIComponents(
      sim_window_ref=dpg.generate_uuid(), 
      sim_menu_bar_ref=dpg.generate_uuid(), 
      sim_initial_state_dl_ref=dpg.generate_uuid(), 
      buttons={
        'sim': {
          'run_sim_toggle_btn': dpg.generate_uuid(),
          'toggle_utility_plot_btn': dpg.generate_uuid()
        }
      }
    )
   
    self.__performance_panel_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__fps_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__time_running_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__cpu_util_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__cpu_util_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__process_memory_used_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__process_memory_used_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__physical_memory_used_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__physical_memory_used_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__virtual_memory_used_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__virtual_memory_used_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__page_faults_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__page_faults_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__pageins_widget_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__pageins_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    
    self.__utility_bar_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__utility_percentiles_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__time_spent_rendering_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
    self.__time_spent_running_tasks_plot_id = dpg.generate_uuid() # TODO: Move to SimulationUIComponents
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

  def _start_simulation(self):
    logger.info('Simulation: Starting simulation')
    self._establish_context()
    self._run_pre_simulation_routines()
    self._initialize_layers()
    self.__perf_receive_pipe = self.__perf_monitor.start(os.getpid())
    self._sim_loop.start(self._context)

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
    
    # TODO: This should all be in a defaults file. Not code. Should all be overridable in a scene file.
    self._context.agent_style.stroke_thickness = SimulationDefaults.AGENT_STYLE_STROKE_THICKNESS
    self._context.agent_style.stroke_color = SimulationDefaults.AGENT_STYLE_STROKE_COLOR
    self._context.agent_style.fill_color = SimulationDefaults.AGENT_STYLE_FILL_COLOR
    self._context.agent_style.size.width = SimulationDefaults.AGENT_STYLE_SIZE_WIDTH
    self._context.agent_style.size.height = SimulationDefaults.AGENT_STYLE_SIZE_HEIGHT

  def _initialize_layers(self) -> None:
    """Initializes the rendering code for each registered layer."""
    logger.info('Simulation: Initializing Layers')
    with dpg.drawlist(
      parent=self._ui_components.sim_window_ref, 
      width=self._context.canvas.width, 
      height=self._context.canvas.height):
      for rl in self._context.scene.layers():
        with dpg.draw_layer(tag=rl.id):
          CallableUtility.invoke(rl.layer, {'context': self._context})
  
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
      # dpg.add_menu_item(label="Toggle Fullscreen", callback=lambda:dpg.toggle_viewport_fullscreen())
      dpg.add_menu_item(label='utility', callback=self._toggle_utility_graph)

  def _toggle_utility_graph(self) -> None:
    self._show_perf_panel = not self._show_perf_panel
    dpg.configure_item(self.__performance_panel_id, show=self._show_perf_panel)

  def _create_performance_panel(self, plot_width: int) -> None:
    TOOL_TIP_WIDTH = 350
    with dpg.group(tag=self.__performance_panel_id, show=self._show_perf_panel):
      with dpg.group(horizontal=True):
        dpg.add_button(tag=self.__fps_widget_id, label="FPS", width=100, height=50)
        with dpg.tooltip(parent=self.__fps_widget_id):
          dpg.add_text("Frames Per Second averaged over 120 frames.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self.__time_running_widget_id, label="Uptime", width=120, height=50)
        with dpg.tooltip(parent=self.__time_running_widget_id):
          dpg.add_text("The amount of time the simulation has been running.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("Format: dd:hh:mm:ss", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self.__cpu_util_widget_id, label="CPU", width=120, height=50)
        with dpg.tooltip(parent=self.__cpu_util_widget_id):
          dpg.add_simple_plot(tag=self.__cpu_util_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("The CPU utilization represented as a percentage.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("Can be greater than 100% in the case of the simulation utilizing multiple cores.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The utilization calculation is performed by comparing the amount of idle time reported against the amount of clock time reported.", wrap=TOOL_TIP_WIDTH)
      
        dpg.add_button(tag=self.__process_memory_used_widget_id, label="Process Memory",  width=180, height=50)
        with dpg.tooltip(parent=self.__process_memory_used_widget_id):
          dpg.add_simple_plot(tag=self.__process_memory_used_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("Unique Set Size (USS)", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The amount of memory that would be freed if the process was terminated right now.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self.__physical_memory_used_widget_id, label="Memory",  width=180, height=50)
        with dpg.tooltip(parent=self.__physical_memory_used_widget_id):
          dpg.add_simple_plot(tag=self.__physical_memory_used_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("Resident Set Size (RSS)", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The non-swapped physical memory the simulation has used.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self.__virtual_memory_used_widget_id, label="Virtual",  width=180, height=50)
        with dpg.tooltip(parent=self.__virtual_memory_used_widget_id):
          dpg.add_simple_plot(tag=self.__virtual_memory_used_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("Virtual Memory Size (VMS)", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("The total amount of virtual memory used by the process.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self.__page_faults_widget_id, label="Page Faults",  width=180, height=50)
        with dpg.tooltip(parent=self.__page_faults_widget_id):
          dpg.add_simple_plot(tag=self.__page_faults_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("The number of page faults.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("Page faults are requests for more memory.", wrap=TOOL_TIP_WIDTH)
        
        dpg.add_button(tag=self.__pageins_widget_id, label="Pageins",  width=180, height=50)
        with dpg.tooltip(parent=self.__pageins_widget_id):
          dpg.add_simple_plot(tag=self.__pageins_plot_id, height=40, width=TOOL_TIP_WIDTH)
          dpg.add_text("The total number of requests for pages from a pager.", wrap=TOOL_TIP_WIDTH)
          dpg.add_text("https://www.unix.com/man-page/osx/1/vm_stat", wrap=TOOL_TIP_WIDTH)

      dpg.add_simple_plot(
        tag=self.__utility_bar_plot_id, 
        overlay='Frame Task Utility (%)',
        height=40, 
        width = plot_width,
        min_scale = 0,
        max_scale = 100
      )
      
      dpg.add_simple_plot(
        tag=self.__utility_percentiles_plot_id, 
        overlay='Frame Task Utility % Percentiles',
        height=40, 
        width = plot_width,
        histogram=True
      )
      
      dpg.add_simple_plot(
        tag=self.__time_spent_rendering_plot_id, 
        overlay='Time Spent Rendering (ms)',
        height=40, 
        width = plot_width,
      )
      
      dpg.add_simple_plot(
        tag=self.__time_spent_running_tasks_plot_id, 
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
        self._update_hardware_metrics()
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
      dpg.draw_text(pos=(20,20), text=self._sim_description, size=13)
      dpg.draw_text(pos=(20,40), text=self._sim_instructions, size=13)

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
    per_frame_samples = self._context.stats.per_frame_samples
    task_samples                = per_frame_samples['running-tasks'].samples
    task_utilization_samples    = list(map(calculate_task_utilization, task_samples))
  
    
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
      item = self.__utility_bar_plot_id, 
      value = task_utilization_samples
    )
    
    dpg.set_value(
      item = self.__utility_percentiles_plot_id, 
      value = percentiles
    )
    
    dpg.set_value(
      item = self.__time_spent_rendering_plot_id, 
      value = per_frame_samples['rendering'].samples
    )
    
    dpg.set_value(
      item = self.__time_spent_running_tasks_plot_id, 
      value = task_samples
    )
    
    dpg.configure_item(
      self.__utility_bar_plot_id, 
      overlay=f'Frame Utility % (avg/min/max): {avg_utility}/{min_utility}/{max_utility}'
    )
    
    dpg.configure_item(
      self.__time_spent_rendering_plot_id, 
      overlay=f'Time Spent Rendering (avg/min/max): {avg_rendering_time}/{min_rendering_time}/{max_rendering_time}'
    )

    dpg.configure_item(
      self.__time_spent_running_tasks_plot_id, 
      overlay=f'Time Spent Running Tasks (avg/min/max): {avg_task_time}/{min_task_time}/{max_task_time}'
    )

  def _update_hardware_metrics(self) -> None:
    # Note: Not providing a value to Pipe.poll makes it return immediately.
    try:
      if self.__perf_receive_pipe is not None and \
        self.__perf_receive_pipe.readable and \
        self.__perf_receive_pipe.poll():
        metrics: PerformanceMetrics = self.__perf_receive_pipe.recv()

        dpg.configure_item(
          self.__fps_widget_id, 
          label = f"FPS: {dpg.get_frame_rate()}"
        )
        
        uptime = TimeUtilities.display_seconds(metrics.sim_running_time)
        dpg.configure_item(
          self.__time_running_widget_id,
          label = uptime
        )

        dpg.configure_item(
          self.__cpu_util_widget_id,
          label = f"CPU:{metrics.cpu_utilization.latest:.2f}"
        )

        dpg.set_value(
          item = self.__cpu_util_plot_id, 
          value = metrics.cpu_utilization.samples
        )
        
        dpg.configure_item(
          self.__process_memory_used_widget_id,
          label = f"USS: {metrics.memory_unique_to_process.latest:.2f} MB"
        )

        dpg.set_value(
          item = self.__process_memory_used_plot_id, 
          value = metrics.memory_unique_to_process.samples
        )
        
        dpg.configure_item(
          self.__physical_memory_used_widget_id,
          label = f"RSS: {metrics.non_swapped_physical_memory_used.latest:.2f} MB"
        )

        dpg.set_value(
          item = self.__physical_memory_used_plot_id, 
          value = metrics.non_swapped_physical_memory_used.samples
        )
        
        dpg.configure_item(
          self.__virtual_memory_used_widget_id,
          label = f"VMS: {metrics.virtual_memory_used.latest:.2f} MB"
        )

        dpg.set_value(
          item = self.__virtual_memory_used_plot_id, 
          value = metrics.virtual_memory_used.samples
        )
        
        
        dpg.configure_item(
          self.__page_faults_widget_id,
          label = f"Page Faults: {metrics.page_faults.latest}"
        )

        dpg.set_value(
          item = self.__page_faults_plot_id, 
          value = metrics.page_faults.samples
        )
        
        dpg.configure_item(
          self.__pageins_widget_id,
          label = f"Pageins: {metrics.pageins.latest}"
        )

        dpg.set_value(
          item = self.__pageins_plot_id, 
          value = metrics.pageins.samples
        )
    except EOFError as e:
      print('The Performance Monitor send an EOFError. The process may have crashed.')
      print(e)
    