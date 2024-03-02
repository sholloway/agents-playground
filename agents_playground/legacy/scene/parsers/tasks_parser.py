from types import SimpleNamespace
from typing import Callable, Dict

from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.legacy.scene.builders.task_options_builder import TaskOptionsBuilder
from agents_playground.legacy.scene.id_map import IdMap
from agents_playground.legacy.scene.parsers.scene_parser import SceneParser
from agents_playground.legacy.scene.scene import Scene

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