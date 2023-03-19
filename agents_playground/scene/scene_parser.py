from __future__ import annotations

from abc import abstractmethod
from types import SimpleNamespace
from typing import Callable, Dict, List, Protocol
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.types import Size
from agents_playground.navigation.navigation_mesh import NavigationMesh
from agents_playground.scene.builders.agent_builder import AgentBuilder
from agents_playground.scene.builders.entity_builder import EntityBuilder
from agents_playground.scene.builders.nav_mesh_junction_builder import NavMeshJunctionBuilder
from agents_playground.scene.builders.path_builder import PathBuilder
from agents_playground.scene.builders.task_options_builder import TaskOptionsBuilder
from agents_playground.scene.id_map import IdMap

from agents_playground.scene.scene import Scene
from agents_playground.scene.scene_defaults import SceneDefaults
from agents_playground.scene.builders.layer_builder import LayerBuilder
from agents_playground.simulation.tag import Tag

class SceneParser(Protocol):
  def parse(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    if self.is_fit(scene_data):
      self.process(scene_data, scene)
    else:
      self.default_process(scene_data, scene)
      
    
  @abstractmethod
  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    ...

  @abstractmethod
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    ...

  def default_process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    return

class CellSizeParser(SceneParser):
  """Establish the cell size on the 2D grid."""
  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'cell_size')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    scene.cell_size = Size(*scene_data.scene.cell_size)

  def default_action(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    scene.cell_size = SceneDefaults.CELL_SIZE

class CanvasSizeParser(SceneParser):
  """Set the canvas size if present."""
  def parse(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    canvas_width = scene_data.scene.width if hasattr(scene_data.scene, 'width') else None
    canvas_height = scene_data.scene.height if hasattr(scene_data.scene, 'height') else None
    scene.canvas_size = Size(canvas_width, canvas_height)

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return True

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    pass

class SceneLayersParser(SceneParser):
  def __init__(
    self, 
    id_generator: Callable[..., Tag], 
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._render_map   = render_map

  """Create render-able Layers"""
  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'layers')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for layer_def in scene_data.scene.layers:
      scene.add_layer(LayerBuilder.build(self._id_generator, self._render_map, layer_def))

class AgentsParser(SceneParser):
  """Create agents."""
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap
  ) -> None:
    self._id_generator = id_generator
    self._id_map       = id_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'agents')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for agent_def in scene_data.scene.agents:
        scene.add_agent(
        AgentBuilder.build(
          self._id_generator, 
          self._id_map, 
          agent_def, 
          scene.cell_size
        )
      )

class PathsParser(SceneParser):
  """Create paths."""
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap,
    render_map: Dict[str, Callable]
  ) -> None:
    self._parsers: List[SceneParser] =  [
      LinearPathParser(id_generator, id_map, render_map),
      CircularPathParser(id_generator, id_map, render_map)
    ]

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'paths')

  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for parser in self._parsers:
      parser.parse(scene_data, scene) 

class LinearPathParser(SceneParser):
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap,
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._id_map       = id_map
    self._render_map   = render_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene.paths, 'linear')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for linear_path_def in scene_data.scene.paths.linear:  
      scene.add_path(PathBuilder.build_linear_path(self._id_generator, self._render_map, self._id_map, linear_path_def))

class CircularPathParser(SceneParser):
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    id_map: IdMap,
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._id_map       = id_map
    self._render_map   = render_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene.paths, 'circular')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for circular_path_def in scene_data.scene.paths.circular:
      scene.add_path(PathBuilder.build_circular_path(self._id_generator, self._render_map, self._id_map, circular_path_def))

class TasksParser(SceneParser):
  def __init__(
    self, 
    task_map: Dict[str, Callable],
    id_map: IdMap,
    task_scheduler: TaskScheduler,
    pre_sim_scheduler: TaskScheduler,
  ) -> None:
    self._task_map             = task_map
    self._id_map               = id_map
    self._task_scheduler       = task_scheduler
    self._pre_simulation_tasks = pre_sim_scheduler

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'schedule')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for task_def in scene_data.scene.schedule:
      coroutine = self._task_map[task_def.coroutine]
      options = TaskOptionsBuilder.build(self._id_map, task_def)
      options['scene'] = scene
      if hasattr(task_def, 'phase'):
        match task_def.phase:
          case 'pre_simulation':
            self._pre_simulation_tasks.add_task(coroutine, [], options)
          case 'post_simulation':
            # Reserved for future use.
            pass
          case 'per_frame':
            self._task_scheduler.add_task(coroutine, [], options)
      else:
        self._task_scheduler.add_task(coroutine, [], options)

class EntitiesParser(SceneParser):
  """
  Creates entities. 

  The format for an entity is that each item is an instance of a Namespace. 
  For example:
    [[scene.entities.circles]]
    [[scene.entities.structures.buildings]]
    [[scene.entities.structures.portals]]
  """
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    render_map: Dict[str, Callable],
    entities_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._render_map   = render_map
    self._entities_map = entities_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'entities')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    for grouping_name, entity_grouping in vars(scene_data.scene.entities).items():
      for entity in entity_grouping:
        scene.add_entity(
          grouping_name, 
          EntityBuilder.build(
            self._id_generator, 
            self._render_map, 
            entity, 
            self._entities_map
          )
        )

class NavMeshJunctionParser(SceneParser):
  def __init__(
    self,
    id_generator: Callable[..., Tag],
    render_map: Dict[str, Callable]
  ) -> None:
    self._id_generator = id_generator
    self._render_map   = render_map

  def is_fit(self, scene_data:SimpleNamespace) -> bool:
    return hasattr(scene_data.scene, 'nav_mesh')
  
  def process(self, scene_data:SimpleNamespace, scene: Scene) -> None:
    nav_mesh = NavigationMesh()

    if hasattr(scene_data.scene.nav_mesh, 'junctions'):
      for junction_def in scene_data.scene.nav_mesh.junctions:
        nav_mesh.add_junction(
          NavMeshJunctionBuilder.build(
            self._id_generator, 
            self._render_map, 
            junction_def
          )
        )
    
    scene.nav_mesh = nav_mesh