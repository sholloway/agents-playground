from types import SimpleNamespace
from typing import Any, Dict, Tuple, Union
from agents_playground.renderers.color import Colors
from agents_playground.scene.id_map import IdMap
from agents_playground.simulation.tag import Tag


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