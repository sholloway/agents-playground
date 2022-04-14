"""
Single file rewrite of coroutine based simulation.
Prototyping the class design. Will break into modules if this pans out.
"""
from __future__ import annotations
from collections import OrderedDict

from math import copysign, radians
import os
import threading
from time import sleep
from types import SimpleNamespace
from typing import Any, Callable, Dict, Generator, Optional, Tuple, Union, cast

import dearpygui.dearpygui as dpg
from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Vector2D
from agents_playground.agents.path import CirclePath, LinearPath
from agents_playground.agents.structures import Point, Size
from agents_playground.agents.utilities import update_agent_in_scene_graph

from agents_playground.core.observe import Observable
from agents_playground.core.task_scheduler import ScheduleTraps, TaskScheduler
from agents_playground.core.time_utilities import (
  MS_PER_SEC,
  UPDATE_BUDGET, 
  TimeInMS,
  TimeInSecs, 
  TimeUtilities
)
from agents_playground.core.callable_utils import CallableUtility
from agents_playground.renderers.agent import render_agents_scene
from agents_playground.renderers.color import Color, Colors
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import circle_renderer, line_segment_renderer, render_interpolated_paths
from agents_playground.renderers.stats import render_stats
from agents_playground.scene.scene import Scene
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.scene_builder import SceneBuilder
from agents_playground.sims.multiple_agents_sim import agents_spinning
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


from agents_playground.scene.scene_reader import SceneReader
from agents_playground.tasks.agent_movement import (
  agent_pacing, 
  agents_spinning, 
  agent_traverse_linear_path,
  agent_traverse_circular_path 
)

logger = get_default_logger()

"""
Current class stats:
- fields: 18
- Properties: 3
- Public Methods: 2
- Private Methods: 20

Possible Refactors
- Use SimulationStatistics to encapsulate _fps_rate and _utilization_rate
- Move _cell_size, _cell_center_x_offset, _cell_center_y_offset to be part
  of Scene object or part of TOML file?
- Merge _sim_window_ref, _sim_menu_bar_ref, _sim_initial_state_dl_ref, _buttons into 
  a dedicated structure? NamedTuple?
- _context needs to be better defined. Passing a dict around sucks. Do we even need
  it? Can the scene object be responsible for passing everything around?
- The logic around simulation state could possibly be encapsulated better.
- _sim_loop, _process_sim_cycle, _update_statistics, _sim_loop_tick,
  _update_render, _update_scene_graph can be in it's own encapsulation.
"""
class SimulationRewrite(Observable):
  """This class may potentially replace Simulation."""
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
    self._cell_size = Size(20, 20)
    self._cell_center_x_offset: float = self._cell_size.width/2
    self._cell_center_y_offset: float = self._cell_size.height/2
    self._sim_stopped_check_time: float = 0.5
    self._fps_rate: float = 0
    self._utilization_rate: float = 0
    self._task_scheduler = TaskScheduler()

    # TODO: These need to be extracted.
    self._render_map = {
      'line_segment_renderer': line_segment_renderer,
      'circular_path_renderer': circle_renderer
    }

    self._task_map = {
      'agent_traverse_linear_path' : agent_traverse_linear_path,
      'agent_traverse_circular_path' : agent_traverse_circular_path,
      'agent_pacing': agent_pacing,
      'agents_spinning' : agents_spinning
    }

    # TODO These need to be extracted and configuration driven.
    self.add_layer(render_stats, "Statistics")
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_interpolated_paths, 'Path')
    self.add_layer(render_agents_scene, 'Agents')

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

  def _load_scene(self):
    """Load the scene data from a TOML file."""
    logger.info('Simulation: Loading Scene')
    scene_reader = SceneReader()
    scene_path = os.path.abspath('agents_playground/sims/simple_movement.toml')
    scene_data:SimpleNamespace = scene_reader.load(scene_path)

    # Setup UI
    self._title = scene_data.simulation.ui.title
    self._sim_description = scene_data.simulation.ui.description
    self._sim_instructions = scene_data.simulation.ui.instructions

    scene_builder = SceneBuilder(
      id_generator = dpg.generate_uuid, 
      task_scheduler = self._task_scheduler,
      render_map = self._render_map, 
      task_map = self._task_map
    )

    self._scene: Scene = scene_builder.build(scene_data)

  def launch(self):
    """Opens the Simulation Window"""
    logger.info('Simulation: Launching')
    self._load_scene()
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
    
    Using the definitions in agents_playground.core.time_utilities, this ensures
    a fixed time for scheduled events to be ran. Rendering is handled automatically
    via DataPyUI (note: VSync is turned on when the Viewport is created.)

    For 60 FPS, TIME_PER_UPDATE is 5.556 ms.
    """
    while self.simulation_state is not SimulationState.ENDED:
      if self.simulation_state is SimulationState.RUNNING:
        self._process_sim_cycle(**data)        
      else:
        # The sim isn't running so don't keep checking it.
        sleep(self._sim_stopped_check_time) 

  def _process_sim_cycle(self, **data) -> None:
    loop_stats = {}
    loop_stats['start_of_cycle'] = TimeUtilities.now()
    time_to_render:TimeInMS = loop_stats['start_of_cycle'] + UPDATE_BUDGET

    # Are there any tasks to do in this cycle? If so, do them.
    # task_time_window: TimeInMS = time_to_render - loop_stats['start_of_cycle']
    loop_stats['time_started_running_tasks'] = TimeUtilities.now()
    self._task_scheduler.queue_holding_tasks()
    self._task_scheduler.consume()
    loop_stats['time_finished_running_tasks'] = TimeUtilities.now()

    # Is there any time until we need to render?
    # If so, then sleep until then.
    break_time: TimeInSecs = (time_to_render - TimeUtilities.now())/MS_PER_SEC
    if break_time > 0:
      sleep(break_time) 

    self._update_statistics(loop_stats)
    self._sim_loop_tick(**data) # Update the scene graph and force a render.

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

  def _bootstrap_simulation_render(self) -> None:
    """Define the render setup for when the render is started."""
    pass

  def _sim_loop_tick(self, **args) -> None:
    """Handles one tick of the simulation."""
    # Force a rerender by updating the scene graph.
    self._update_render(self._scene)
    self._update_scene_graph(self._scene)

  def _update_render(self, scene: Scene) -> None: 
    for agent in filter(lambda a: a.agent_render_changed, scene.agents.values()):
      dpg.configure_item(agent.render_id, fill = agent.crest)
    
  def _update_scene_graph(self, scene: Scene) -> None:
    for agent_id, agent in scene.agents.items():
      update_agent_in_scene_graph(agent, agent_id, self._cell_size)

  def _setup_menu_bar_ext(self) -> None:
    """Setup simulation specific menu items."""
    pass
  
  def _establish_context_ext(self, context: SimulationContext) -> None:
    """Setup simulation specific context variables."""
    logger.info('MultipleAgentsSim: Establishing simulation context.')
    context.details['cell_size'] = self._cell_size
    context.details['offset'] = Size(self._cell_center_x_offset, self._cell_center_y_offset)
    # TODO: Transition to passing a scene around. 
    # Perhaps the Scene or context should be transitioned to 
    # FrameParams type object.
    context.details['scene'] = self._scene

    # TODO: Remove this and just pass the scene around.
    context.details['paths'] = self._scene.paths.values()