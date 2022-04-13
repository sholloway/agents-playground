"""
Single file rewrite of coroutine based simulation.
Prototyping the class design. Will break into modules if this pans out.
"""
from __future__ import annotations
from collections import OrderedDict

from math import copysign, floor, radians
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
  TIME_PER_FRAME,
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
from agents_playground.renderers.scene import Scene
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

import os
from agents_playground.core.sim_loader import SimLoader

logger = get_default_logger()

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
    self._scene = Scene()
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
    self._id_map = IdMap()

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

  # TODO: This needs to be it's own class and probably a series of classes.
  def _load_scene(self):
    """Load the scene data from a TOML file."""
    logger.info('Simulation: Loading Scene')
    breakpoint
    sim_loader = SimLoader()
    scene_path = os.path.abspath('agents_playground/sims/simple_movement.toml')
    self._scene_data:SimpleNamespace = sim_loader.load(scene_path)

    # Setup UI
    self._title = self._scene_data.simulation.ui.title
    self._sim_description = self._scene_data.simulation.ui.description
    self._sim_instructions = self._scene_data.simulation.ui.instructions

    # Create Agents
    for agent_def in self._scene_data.scene.agents:
      self._scene.add_agent(build_agent(self._id_map, agent_def))

    # Create Linear Paths
    for linear_path_def in self._scene_data.scene.paths.linear:  
      self._scene.add_path(build_linear_path(self._render_map, self._id_map, linear_path_def))

    # Create Circular Paths
    for circular_path_def in self._scene_data.scene.paths.circular:
      self._scene.add_path(build_circular_path(self._render_map, self._id_map, circular_path_def))
      
    # Schedule Tasks
    for task_def in self._scene_data.scene.schedule:
      coroutine = self._task_map[task_def.coroutine]
      options = build_task_options(self._id_map, task_def)
      options['scene'] = self._scene
      self._task_scheduler.add_task(coroutine, [], options)

    print(f"Scheduled: {self._task_scheduler._pending_tasks.value()}")

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

def build_agent(id_map: IdMap, agent_def: SimpleNamespace) -> Agent:
  agent_id: Tag = dpg.generate_uuid()
  id_map.register_agent(agent_id, agent_def.id)
  """Create an agent instance from the TOML definition."""
  agent = Agent(
    id = agent_id, 
    render_id = dpg.generate_uuid(), 
    toml_id = agent_def.id)

  if hasattr(agent_def, 'crest'):
    agent.crest = Colors[agent_def.crest].value 

  if hasattr(agent_def, 'location'):
    agent.move_to(Point(*agent_def.location))

  if hasattr(agent_def, 'facing'):
    agent.face(Vector2D(*agent_def.facing))

  agent.reset()
  return agent

def build_linear_path(render_map: dict, id_map: IdMap, linear_path_def: SimpleNamespace) -> LinearPath:
  path_id: Tag = dpg.generate_uuid()
  id_map.register_linear_path(path_id, linear_path_def.id)
  lp = LinearPath(
    id = path_id, 
    control_points = tuple(linear_path_def.steps), 
    renderer = render_map[linear_path_def.renderer],
    toml_id = linear_path_def.id
  )

  if hasattr(linear_path_def, 'closed'):
    lp.closed = linear_path_def.closed

  return lp

def build_circular_path(render_map: dict, id_map: IdMap, circular_path_def: SimpleNamespace) -> CirclePath:
  path_id: Tag = dpg.generate_uuid()
  id_map.register_circular_path(path_id, circular_path_def.id)
  cp = CirclePath(
    id =path_id,
    center = tuple(circular_path_def.center),
    radius = circular_path_def.radius,
    renderer = render_map[circular_path_def.renderer],
    toml_id = circular_path_def.id
  )
  return cp

def build_task_options(id_map: IdMap, task_def: SimpleNamespace) -> Dict[str, Any]:
  options = {}

  # What is the correct way to iterate over a SimpleNamespace's fields?
  # I can do task_def.__dict__.items() but that may be bad form.
  for k,v in vars(task_def).items():
    if k == 'coroutine':
      pass
    elif k == 'linear_path_id':
      options['path_id'] = id_map.lookup_linear_path_by_toml(v)
    elif k == 'circular_path_id':
      options['path_id'] = id_map.lookup_circular_path_by_toml(v)
    elif k == 'agent_id':
      options[k] = id_map.lookup_agent_by_toml(v)
    elif k == 'agent_ids':
      options[k] = tuple(map(id_map.lookup_agent_by_toml, v))
    elif str(k).endswith('_color'):
      options[k] = Colors[v].value
    else:
      # Include the k/v in the bundle
      options[k] = v
  return options
  
# TODO: Need to find a way to organize the coroutines.
def agent_traverse_linear_path(*args, **kwargs) -> Generator:
  """A task that moves an agent along a path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - step_index: The starting point on the path.
  """
  logger.info('agent_traverse_linear_path: Starting task.')
  scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  scene = kwargs['scene']
  speed: float = kwargs['speed'] 

  agent = scene.agents[agent_id]
  path: LinearPath = scene.paths[path_id]
  segments_count = path.segments_count()
  active_path_segment: int = kwargs['step_index']
  active_t: float = 0 # In the range of [0,1]
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_path_segment, active_t)
      agent.move_to(Point(pt[0], pt[1]))
      direction: Vector2D = path.direction(active_path_segment)
      agent.face(direction)

      active_t += speed
      if active_t > 1:
        active_t = 0
        active_path_segment = active_path_segment + 1 if active_path_segment < segments_count else 1
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_linear_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_linear_path - Task Completed')

def agent_traverse_circular_path(*args, **kwargs) -> Generator:
  """A task that moves an agent along a circular path.

  Args:
    - scene: The scene to take action on.
    - agent_id: The agent to move along the path.
    - path_id: The path the agent must traverse.
    - starting_degree: Where on the circle to start the animation.
  """
  logger.info('agent_traverse_circular_path: Starting task.')
  scene = kwargs['scene']
  agent_id = kwargs['agent_id']
  path_id = kwargs['path_id']
  scene = kwargs['scene']
  active_t: float = kwargs['starting_degree'] # In the range of [0, 2*pi]
  speed: float = kwargs['speed'] 
  direction = int(copysign(1, speed))

  agent: Agent = scene.agents[agent_id]
  path: CirclePath = scene.paths[path_id]

  
  max_degree = 360
  try:
    while True:
      pt: Tuple[float, float] = path.interpolate(active_t)
      agent.move_to(Point(pt[0], pt[1]))
      tangent_vector: Vector2D = path.tangent(pt, direction)
      agent.face(tangent_vector)

      active_t += speed
      if active_t > max_degree:
        active_t = 0
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_traverse_circular_path - GeneratorExit')
  finally:
    logger.info('Task: agent_traverse_circular_path - Task Completed')
    
def agent_pacing(*args, **kwargs) -> Generator:
  logger.info('agent_pacing: Starting task.')
  scene: Scene = kwargs['scene']      
  agent_ids: Tuple[Tag, ...] = kwargs['agent_ids']
  path_id: Tag = kwargs['path_id']
  starting_segments: Tuple[int, ...] = kwargs['starting_segments']
  speeds: Tuple[float, ...] = kwargs['speeds']
  path: LinearPath = cast(LinearPath, scene.paths[path_id])
  segments_count = path.segments_count()
  explore_color: Color =  kwargs['explore_color']
  return_color: Color = kwargs['return_color']

  direction_color = { 1: explore_color, -1: return_color }

  # build a structure of the form: want = { 'id' : {'speed': 0.3, 'segment': 4}}
  values = list(map(lambda i: {'speed': i[0], 'segment': i[1], 'active_t': 0}, list(zip(speeds, starting_segments))))
  group_motion = dict(zip(agent_ids, values))

  try:
    while True:
      # Update each agent's location.
      for agent_id in group_motion:
        pt: Tuple[float, float] = path.interpolate(int(group_motion[agent_id]['segment']), group_motion[agent_id]['active_t'])
        scene.agents[agent_id].move_to(Point(pt[0], pt[1]))
        group_motion[agent_id]['active_t'] += group_motion[agent_id]['speed']

        direction = int(copysign(1, group_motion[agent_id]['speed']))
        direction_vector: Vector2D = path.direction(int(group_motion[agent_id]['segment']))
        direction_vector = direction_vector.scale(direction)
        scene.agents[agent_id].face(direction_vector)
        
        # Handle moving an agent to the next line segment.
        """
        TODO: This is a good candidate for using polymorphism for handling 
        switching direction.
        Scenarios:
          - Going Forward, Reverse Required
          - Going Forward, Keep Going
          - Going Back, Reverse Required
          - Going Back, Keep Going
        """

        if group_motion[agent_id]['active_t'] < 0 or group_motion[agent_id]['active_t'] > 1:
          # End of the Line: The segment the agent is on has been exceeded. 
          # Need to go to the next segment or reverse direction.
          
          if direction == -1:
            if group_motion[agent_id]['segment'] <= 1:
              # Reverse Direction
              group_motion[agent_id]['active_t'] = 0
              group_motion[agent_id]['speed'] *= -1
              scene.agents[agent_id].crest = direction_color[-direction]
            else:
              # Keep Going
              group_motion[agent_id]['active_t'] = 1
              group_motion[agent_id]['segment'] += direction
          else: 
            if group_motion[agent_id]['segment'] < segments_count:
              # Keep Going
              group_motion[agent_id]['active_t'] = 0
              group_motion[agent_id]['segment'] += direction
            else:
              # Reverse Direction
              group_motion[agent_id]['active_t'] = 1
              group_motion[agent_id]['speed'] *= -1
              scene.agents[agent_id].crest = direction_color[-direction]
        
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agent_pacing - GeneratorExit')
  finally:
    logger.info('Task: agent_pacing - Task Completed')
    
def agents_spinning(*args, **kwargs) -> Generator:
  """ Rotate a group of agents individually in place. 
        
  Rotation is done by updating the agent's facing direction at a given speed
  per frame.
  """  
  logger.info('agents_spinning: Starting task.')
  scene: Scene = kwargs['scene']      
  agent_ids: Tuple[Tag, ...] = kwargs['agent_ids']
  speeds: Tuple[float, ...] = kwargs['speeds']

  # build a structure of the form: want = { 'id' : {'speed': 0.3}
  values = list(map(lambda i: {'speed': i[0]}, list(zip(speeds))))
  group_motion = dict(zip(agent_ids, values))
  rotation_amount = radians(5)

  try:
    while True:
      for agent_id in agent_ids:
        rot_dir = int(copysign(1, group_motion[agent_id]['speed']))
        agent: Agent = scene.agents[agent_id]
        new_orientation = agent.facing.rotate(rotation_amount * rot_dir)
        agent.face(new_orientation)
      yield ScheduleTraps.NEXT_FRAME
  except GeneratorExit:
    logger.info('Task: agents_spinning - GeneratorExit')
  finally:
    logger.info('Task: agents_spinning - Task Completed')

class IdMap:
  def __init__(self) -> None:
    self._agents_toml_to_dpg = {}
    self._agents_dpg_to_toml = {}
    self._linear_paths_toml_to_dpg = {}
    self._linear_paths_dpg_to_toml = {}
    self._circular_paths_toml_to_dpg = {}
    self._circular_paths_dpg_to_toml = {}

  def register_agent(self, agent_id: Tag, toml_id: Tag) -> None:
    self._agents_toml_to_dpg[toml_id] = agent_id
    self._agents_dpg_to_toml[agent_id] = toml_id

  def register_linear_path(self, path_id: Tag, toml_id: Tag) -> None:
    self._linear_paths_toml_to_dpg[toml_id] = path_id
    self._linear_paths_dpg_to_toml[path_id] = toml_id

  def register_circular_path(self, path_id: Tag, toml_id: Tag) -> None:
    self._circular_paths_toml_to_dpg[toml_id] = path_id
    self._circular_paths_dpg_to_toml[path_id] = toml_id

  def lookup_agent_by_toml(self, toml_id: Tag) -> Tag:
    return self._agents_toml_to_dpg[toml_id]

  def lookup_agent_by_dpg(self, agent_id: Tag) -> Tag:
    return self._agents_dpg_to_toml[agent_id]
  
  def lookup_linear_path_by_toml(self, toml_id: Tag) -> Tag:
    return self._linear_paths_toml_to_dpg[toml_id]

  def lookup_linear_path_by_dpg(self, path_id: Tag) -> Tag:
    return self._linear_paths_dpg_to_toml[path_id]
  
  def lookup_circular_path_by_toml(self, toml_id: Tag) -> Tag:
    return self._circular_paths_toml_to_dpg[toml_id]

  def lookup_circular_path_by_dpg(self, path_id: Tag) -> Tag:
    return self._circular_paths_dpg_to_toml[path_id]