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
from agents_playground.renderers.entities import render_entities
from agents_playground.renderers.renderers_registry import RENDERERS_REGISTRY
from agents_playground.renderers.agent import render_agents_scene
from agents_playground.renderers.grid import render_grid
from agents_playground.renderers.path import render_interpolated_paths
from agents_playground.renderers.stats import render_stats
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

"""
https://app.diagrams.net/?src=about#G1UgUgEILyWFRzwlZu0GIsVdS7WhzqWH3G
Current class stats:
- fields: 18 -> 10
- Properties: 3 -> 2
- Public Methods: 2 -> 2
- Private Methods: 20 -> 11

Possible Refactors
- Make SimLoop something that can be passed in to enable other looping types.
  How to make this more generic? 
    - The update_statistics is very specific. 
    - The task_scheduler is passed in.
- Should _establish_context be 100% in TOML files. Perhaps there should be a 
  default TOML file to keep things like font, that can be overridden?


TODO
- Remove the other sims.
  - Replace Simulation with SimRewrite
- Check Typing
- Unit Tests
- Diagram
- Update the module imports
- PyDoc
"""
class SimulationRewrite(Observable):
  """This class may potentially replace Simulation."""
  _primary_window_ref: Union[int, str]

  def __init__(self, scene_toml: str) -> None:
    super().__init__()
    logger.info('Simulation: Initializing')
    self._scene_toml = scene_toml
    self._context: SimulationContext = SimulationContext(dpg.generate_uuid)
    self._ui_components = SimulationUIComponents(
      dpg.generate_uuid(), 
      dpg.generate_uuid(), 
      dpg.generate_uuid(), 
      {
        'sim': {
          'run_sim_toggle_btn': dpg.generate_uuid()
        }
      }
    )
    self._layers: OrderedDict[Tag, RenderLayer] = OrderedDict()
    self._title: str = "Set the Simulation Title"
    self._sim_description = 'Set the Simulation Description'
    self._sim_instructions = 'Set the Simulation Instructions'
    self._task_scheduler = TaskScheduler()
    self._sim_loop = SimLoop(scheduler = self._task_scheduler)
    
    """
    TODO: This appears to be short sighted. Needs to be configurable somehow.

    I need a better way to register render functions to be called. 
    The render_interpolated_paths is looping through the list of paths and 
    calling the associated render function. Where in contrast the Agents don't 
    have a render method, there is just the centralized render_agents_scene function
    that renders all the agents in a single batch. 

    The render_interpolated_paths approach seems more flexible. The simplest 
    thing I can think of is to have a Renderable interface that exposes a render() 
    method and a renderer field. Then things that can be rendered simply have 
    implement that interface and add themselves to a list of renderable entities.

    I need a way to void adding a one off function for every new simulation use case.
    """
    self.add_layer(render_stats, 'Statistics')
    self.add_layer(render_grid, 'Terrain')
    self.add_layer(render_entities, 'Entities')
    self.add_layer(render_interpolated_paths, 'Path')
    self.add_layer(render_agents_scene, 'Agents') 

  @property
  def simulation_state(self) -> SimulationState:
    return self._sim_loop.simulation_state

  @simulation_state.setter
  def simulation_state(self, next_state: SimulationState) -> None:
    self._sim_loop.simulation_state = next_state

  @property
  def primary_window(self) -> Union[int, str]:
    """Returns the primary window."""
    return self._primary_window_ref

  @primary_window.setter
  def primary_window(self, primary_window_ref: Union[int, str]) -> None:
    """Assigns the primary window to the simulation window."""
    self._primary_window_ref = primary_window_ref

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
    self._load_scene()
    parent_width: Optional[int] = dpg.get_item_width(self.primary_window)
    parent_height: Optional[int] = dpg.get_item_height(self.primary_window)

    with dpg.window(tag=self._ui_components.sim_window_ref, 
      label=self._title, 
      width=parent_width, 
      height=parent_height, 
      on_close=self._handle_sim_closed):
      self._setup_menu_bar()
      if self._sim_loop.simulation_state is SimulationState.INITIAL:
        self._initial_render()
      else:
        self._start_simulation()

  def _load_scene(self):
    """Load the scene data from a TOML file."""
    logger.info('Simulation: Loading Scene')
    scene_reader = SceneReader()
    scene_path = os.path.abspath(self._scene_toml)
    scene_data:SimpleNamespace = scene_reader.load(scene_path)

    # Setup UI
    self._title = scene_data.simulation.ui.title
    self._sim_description = scene_data.simulation.ui.description
    self._sim_instructions = scene_data.simulation.ui.instructions

    scene_builder = SceneBuilder(
      id_generator = dpg.generate_uuid, 
      task_scheduler = self._task_scheduler,
      render_map = RENDERERS_REGISTRY, 
      task_map = TASKS_REGISTRY,
      entities_map = ENTITIES_REGISTRY
    )

    self._context.scene = scene_builder.build(scene_data)

  def _start_simulation(self):
    logger.info('Simulation: Starting simulation')
    self._establish_context()
    self._initialize_layers()
    self._sim_loop.start(self._context)

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

  def _initialize_layers(self) -> None:
    """Initializes the rendering code for each registered layer."""
    logger.info('Simulation: Initializing Layers')
    with dpg.drawlist(
      parent=self._ui_components.sim_window_ref, 
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