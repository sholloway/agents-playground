
from types import SimpleNamespace
from typing import Any, Callable, Dict

from agents_playground.agents.agent import Agent
from agents_playground.agents.direction import Vector2D
from agents_playground.agents.path import CirclePath, LinearPath
from agents_playground.agents.structures import Point, Size
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.renderers.color import Colors
from agents_playground.scene.id_map import IdMap

from agents_playground.scene.scene import Scene
from agents_playground.simulation.tag import Tag


class SceneBuilder:
  def __init__(
    self, 
    id_generator: Callable,
    task_scheduler: TaskScheduler,
    id_map: IdMap = IdMap(), 
    render_map: Dict[str, Callable] = {}, 
    task_map: Dict[str, Callable] = {}) -> None:
    self._id_generator = id_generator
    self._task_scheduler = task_scheduler
    self._id_map = id_map
    self._render_map = render_map
    self._task_map = task_map

  def build(self, scene_data:SimpleNamespace) -> Scene:
    scene = Scene()

    # Establish the cell size on the 2D grid.
    scene.cell_size = Size(*scene_data.scene.cell_size)

    # Create Agents
    for agent_def in scene_data.scene.agents:
      scene.add_agent(AgentBuilder.build(self._id_generator, self._id_map, agent_def))

    # Create Linear Paths
    for linear_path_def in scene_data.scene.paths.linear:  
      scene.add_path(PathBuilder.build_linear_path(self._id_generator, self._render_map, self._id_map, linear_path_def))

    # Create Circular Paths
    for circular_path_def in scene_data.scene.paths.circular:
      scene.add_path(PathBuilder.build_circular_path(self._id_generator, self._render_map, self._id_map, circular_path_def))
      
    # Schedule Tasks
    for task_def in scene_data.scene.schedule:
      coroutine = self._task_map[task_def.coroutine]
      options = TaskOptionsBuilder.build(self._id_map, task_def)
      options['scene'] = scene
      self._task_scheduler.add_task(coroutine, [], options)

    return scene

class AgentBuilder:
  def build(id_generator: Callable, id_map: IdMap, agent_def: SimpleNamespace) -> Agent:
    agent_id: Tag = id_generator()
    id_map.register_agent(agent_id, agent_def.id)
    """Create an agent instance from the TOML definition."""
    agent = Agent(
      id = agent_id, 
      render_id = id_generator(), 
      toml_id = agent_def.id)

    if hasattr(agent_def, 'crest'):
      agent.crest = Colors[agent_def.crest].value 

    if hasattr(agent_def, 'location'):
      agent.move_to(Point(*agent_def.location))

    if hasattr(agent_def, 'facing'):
      agent.face(Vector2D(*agent_def.facing))

    agent.reset()
    return agent

class PathBuilder:
  def build_linear_path(id_generator: Callable, render_map: dict, id_map: IdMap, linear_path_def: SimpleNamespace) -> LinearPath:
    path_id: Tag = id_generator()
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

  def build_circular_path(id_generator: Callable, render_map: dict, id_map: IdMap, circular_path_def: SimpleNamespace) -> CirclePath:
    path_id: Tag = id_generator()
    id_map.register_circular_path(path_id, circular_path_def.id)
    cp = CirclePath(
      id =path_id,
      center = tuple(circular_path_def.center),
      radius = circular_path_def.radius,
      renderer = render_map[circular_path_def.renderer],
      toml_id = circular_path_def.id
    )
    return cp

class TaskOptionsBuilder:
  def build(id_map: IdMap, task_def: SimpleNamespace) -> Dict[str, Any]:
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
