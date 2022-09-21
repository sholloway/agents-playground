"""
Single file rewrite of coroutine based simulation.
Prototyping the class design. Will break into modules if this pans out.
"""
from __future__ import annotations
from collections import OrderedDict
import os
from types import SimpleNamespace
from typing import Callable, NamedTuple, Optional, Union

import dearpygui.dearpygui as dpg

from agents_playground.core.observe import Observable
from agents_playground.core.sim_loop import SimLoop
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.callable_utils import CallableUtility
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
  AGENT_STYLE_STROKE_THICKNESS: float = 1.0
  AGENT_STYLE_STROKE_COLOR: Color = BasicColors.white.value
  AGENT_STYLE_FILL_COLOR: Color = BasicColors.blue.value
  AGENT_STYLE_SIZE_WIDTH: int = 20
  AGENT_STYLE_SIZE_HEIGHT: int = 20

class Simulation(Observable):
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
          'run_sim_toggle_btn': dpg.generate_uuid()
        }
      }
    )
    # self._layers: OrderedDict[Tag, RenderLayer] = OrderedDict()
    self._title: str = "Set the Simulation Title"
    self._sim_description = 'Set the Simulation Description'
    self._sim_instructions = 'Set the Simulation Instructions'
    self._task_scheduler = TaskScheduler()
    self._pre_sim_task_scheduler = TaskScheduler()
    self._sim_loop = SimLoop(scheduler = self._task_scheduler)
    self._scene_reader = scene_reader
    

  @property
  def simulation_state(self) -> SimulationState:
    return self._sim_loop.simulation_state

  @simulation_state.setter
  def simulation_state(self, next_state: SimulationState) -> None:
    self._sim_loop.simulation_state = next_state

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
  
  def _handle_sim_closed(self, sender, app_data, user_data):
    logger.info('Simulation: Closing the simulation.')
    #1. Kill the simulation thread.
    self.simulation_state = SimulationState.ENDED

    # 2. Notify the parent window that this simulation has been closed.
    super().notify(SimulationEvents.WINDOW_CLOSED.value)

  def _setup_menu_bar(self):
    logger.info('Simulation: Setting up the menu bar.')
    with dpg.menu_bar(tag=self._ui_components.sim_menu_bar_ref):
      dpg.add_button(
        label=SimulationStateToLabelMap[self._sim_loop.simulation_state], 
        tag=self._ui_components.buttons['sim']['run_sim_toggle_btn'], 
        callback=self._run_sim_toggle_btn_clicked
      )
      self._setup_layers_menu()

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