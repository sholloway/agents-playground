from __future__ import annotations

from types import SimpleNamespace
from typing import Callable, Dict, List

from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.parsers.paths_parser import PathsParser
from agents_playground.scene.parsers.tasks_parser import TasksParser
from agents_playground.scene.parsers.entities_parser import EntitiesParser
from agents_playground.scene.parsers.nav_mesh_junction_parser import NavMeshJunctionParser
from agents_playground.scene.parsers.agents_parser import AgentsParser
from agents_playground.scene.parsers.scene_layers_parser import SceneLayersParser
from agents_playground.scene.parsers.canvas_size_parser import CanvasSizeParser
from agents_playground.scene.parsers.cell_size_parser import CellSizeParser
from agents_playground.scene.scene import Scene
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.simulation.tag import Tag

class SceneBuilder:
  def __init__(
    self, 
    id_generator: Callable[..., Tag],
    task_scheduler: TaskScheduler,
    pre_sim_scheduler: TaskScheduler,
    id_map: IdMap = IdMap(), 
    render_map: Dict[str, Callable] = {}, 
    task_map: Dict[str, Callable] = {},
    entities_map: Dict[str, Callable] = {}
  ) -> None:
    self._id_map = id_map
    self._entities_map = entities_map
    self._parsers: List[SceneParser] = [
      CellSizeParser(),
      CanvasSizeParser(),
      SceneLayersParser(id_generator, render_map),
      AgentsParser(id_generator, id_map),
      PathsParser(id_generator, id_map, render_map),
      TasksParser(task_map, id_map, task_scheduler, pre_sim_scheduler),
      EntitiesParser(id_generator, render_map, entities_map),
      NavMeshJunctionParser(id_generator, render_map)
    ]

  def build(self, scene_data:SimpleNamespace) -> Scene:
    scene = Scene()

    for parser in self._parsers:
      parser.parse(scene_data, scene) 

    return scene