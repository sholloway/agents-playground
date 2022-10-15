from __future__ import annotations

from types import SimpleNamespace, MethodType
from typing import Any, Callable, Dict, List, Tuple, Union
from copy import deepcopy

from agents_playground.agents.agent import Agent, AgentState
from agents_playground.agents.direction import Vector2D
from agents_playground.agents.path import CirclePath, LinearPath
from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.core.types import Coordinate, Size
from agents_playground.renderers.color import Colors
from agents_playground.scene.id_map import IdMap

from agents_playground.scene.scene import NavigationMesh, Scene
from agents_playground.simulation.render_layer import RenderLayer
from agents_playground.simulation.tag import Tag


class SceneBuilder:
  def __init__(
    self, 
    id_generator: Callable,
    task_scheduler: TaskScheduler,
    pre_sim_scheduler: TaskScheduler,
    id_map: IdMap = IdMap(), 
    render_map: Dict[str, Callable] = {}, 
    task_map: Dict[str, Callable] = {},
    entities_map: Dict[str, Callable] = {}) -> None:
    self._id_generator = id_generator
    self._task_scheduler = task_scheduler
    self._pre_simulation_tasks = pre_sim_scheduler 
    self._id_map = id_map
    self._render_map = render_map
    self._task_map = task_map
    self._entities_map = entities_map

  def build(self, scene_data:SimpleNamespace) -> Scene:
    scene = Scene()

    # Establish the cell size on the 2D grid.
    scene.cell_size = Size(*scene_data.scene.cell_size) if hasattr(scene_data.scene, 'cell_size') else Size(20,20)
    
    # Set the canvas size if present.
    canvas_width = scene_data.scene.width if hasattr(scene_data.scene, 'width') else None
    canvas_height = scene_data.scene.height if hasattr(scene_data.scene, 'height') else None
    scene.canvas_size = Size(canvas_width, canvas_height)

    # Create render-able Layers
    if hasattr(scene_data.scene, 'layers'):
      for layer_def in scene_data.scene.layers:
        scene.add_layer(LayerBuilder.build(self._id_generator, self._render_map, layer_def))

    # Create Agents
    if hasattr(scene_data.scene, 'agents'):
      for agent_def in scene_data.scene.agents:
        scene.add_agent(AgentBuilder.build(self._id_generator, self._id_map, agent_def))

    if hasattr(scene_data.scene, 'paths'):
      # Create Linear Paths
      if hasattr(scene_data.scene.paths, 'linear'):
        for linear_path_def in scene_data.scene.paths.linear:  
          scene.add_path(PathBuilder.build_linear_path(self._id_generator, self._render_map, self._id_map, linear_path_def))

      # Create Circular Paths
      if hasattr(scene_data.scene.paths, 'circular'):
        for circular_path_def in scene_data.scene.paths.circular:
          scene.add_path(PathBuilder.build_circular_path(self._id_generator, self._render_map, self._id_map, circular_path_def))
      
    # Schedule Tasks
    if hasattr(scene_data.scene, 'schedule'):
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

    # Each item is an instance of Namespace. No logic (i.e. functions) is associated
    # with an entity. For Example:
    #   [[scene.entities.circles]]
    #   [[scene.entities.structures.buildings]]
    #   [[scene.entities.structures.portals]]
    # 
    # Using the scene instance entities can be interacted with like
    if hasattr(scene_data.scene, 'entities'):
      for grouping_name, entity_grouping in vars(scene_data.scene.entities).items():
        for entity in entity_grouping:
          scene.add_entity(grouping_name, EntityBuilder.build(self._id_generator, self._render_map, entity, self._entities_map))

    if hasattr(scene_data.scene, 'nav_mesh'):
      nav_mesh = NavigationMesh()

      if hasattr(scene_data.scene.nav_mesh, 'junctions'):
        for junction_def in scene_data.scene.nav_mesh.junctions:
          nav_mesh.add_junction(NavMeshJunctionBuilder.build(self._id_generator, self._render_map, junction_def))
      
      scene.nav_mesh = nav_mesh
    return scene

class AgentBuilder:
  @staticmethod
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
      agent.move_to(Coordinate(*agent_def.location))

    if hasattr(agent_def, 'facing'):
      agent.face(Vector2D(*agent_def.facing))
    
    if hasattr(agent_def, 'state'):
      agent.state = AgentState[agent_def.state]

    return agent

class PathBuilder:
  @staticmethod
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

  @staticmethod
  def build_circular_path(id_generator: Callable, render_map: dict, id_map: IdMap, circular_path_def: SimpleNamespace) -> CirclePath:
    path_id: Tag = id_generator()
    id_map.register_circular_path(path_id, circular_path_def.id)
    cp = CirclePath(
      id =path_id,
      center = (float(circular_path_def.center[0]), float(circular_path_def.center[1])),
      radius = circular_path_def.radius,
      renderer = render_map[circular_path_def.renderer],
      toml_id = circular_path_def.id
    )
    return cp

class TaskOptionsBuilder:
  @staticmethod
  def build(id_map: IdMap, task_def: SimpleNamespace) -> Dict[str, Any]:
    options: dict[str, Tag | Tuple[Union[float, str, None], ...]] = {}

    for k,v in vars(task_def).items():
      match k:
        case 'coroutine':
          pass
        case 'linear_path_id':
          options['path_id'] = id_map.lookup_linear_path_by_toml(v)
        case 'circular_path_id':
          options['path_id'] = id_map.lookup_circular_path_by_toml(v)
        case 'agent_id':
          options[k] = id_map.lookup_agent_by_toml(v)
        case 'agent_ids':
          options[k] = tuple(map(id_map.lookup_agent_by_toml, v))
        case _ if k.endswith('_color'):
          options[k] = Colors[v].value
        case _:
          # Include the k/v in the bundle
          options[k] = v
    return options

class EntityBuilder:
  @staticmethod
  def build(id_generator: Callable, 
    renderer_map: dict, 
    entity_def: SimpleNamespace, 
    entities_map: Dict[str, Callable]) -> SimpleNamespace:
    """
    Builds an entity object by cloning the definition from the TOML file and 
    assigning attributes needed for rendering.
    """
    entity = deepcopy(entity_def)
    entity.toml_id = entity.id
    entity.id = id_generator()
    if hasattr(entity_def,'renderer'):
      entity.render = MethodType(renderer_map[entity_def.renderer], entity)
    else:
      entity.render = MethodType(renderer_map['do_nothing_render'], entity)

    if hasattr(entity_def, 'update_method'):
      entity.update = MethodType(entities_map[entity_def.update_method], entity)
    else:
      entity.update = MethodType(entities_map['do_nothing_update_method'], entity)

    if hasattr(entity_def, 'location'):
      entity.location = Coordinate(*entity_def.location)
      
    return entity

class LayerBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    renderer_map: dict, 
    layer_def: SimpleNamespace) -> RenderLayer:
    renderer: Union[Any, None] = renderer_map.get(layer_def.renderer)
    if renderer:
      rl: RenderLayer = RenderLayer(
        id = id_generator(), 
        label= layer_def.label,
        menu_item=id_generator(),
        layer=renderer
      )
      return rl
    else:
      raise Exception(f'Error Loading the scene. No registered layer renderer named {layer_def.renderer}.')

class NavMeshJunctionBuilder:
  @staticmethod
  def build(
    id_generator: Callable, 
    renderer_map: dict, 
    junction_def: SimpleNamespace) -> SimpleNamespace:
    junction = deepcopy(junction_def)
    junction.toml_id = junction_def.id
    junction.id = id_generator()

    if hasattr(junction_def, 'location'):
      junction.location = Coordinate(*junction_def.location)
      
    if hasattr(junction_def,'renderer'):
      junction.render = MethodType(renderer_map[junction_def.renderer], junction)
    else:
      junction_def.render = MethodType(renderer_map['do_nothing_render'], junction_def)

    return junction