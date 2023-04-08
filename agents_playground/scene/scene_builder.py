from __future__ import annotations

from types import SimpleNamespace
from typing import Callable, Dict, List
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics

from agents_playground.core.task_scheduler import TaskScheduler
from agents_playground.likelihood.coin import Coin
from agents_playground.scene.id_map import IdMap
from agents_playground.scene.parsers.agent_state_transition_maps_parser import AgentStateTransitionMapsParser
from agents_playground.scene.parsers.agent_states_parser import AgentStatesParser
from agents_playground.scene.parsers.default_agent_states_parser import( 
  DefaultAgentStatesParser
)
from agents_playground.scene.parsers.paths_parser import PathsParser
from agents_playground.scene.parsers.tasks_parser import TasksParser
from agents_playground.scene.parsers.entities_parser import EntitiesParser
from agents_playground.scene.parsers.nav_mesh_junction_parser import NavMeshJunctionParser
from agents_playground.scene.parsers.agents_parser import AgentsParser
from agents_playground.scene.parsers.scene_layers_parser import SceneLayersParser
from agents_playground.scene.parsers.canvas_size_parser import CanvasSizeParser
from agents_playground.scene.parsers.cell_size_parser import CellSizeParser
from agents_playground.scene.parsers.types import (
  AgentStateName, 
  AgentStateTransitionMapName,
  DefaultAgentStateMap
)
from agents_playground.scene.scene import Scene
from agents_playground.scene.parsers.scene_parser import SceneParser
from agents_playground.simulation.tag import Tag
from agents_playground.sys.dict_with_default import DictWithDefault

class SceneBuilder:
  def __init__(
    self, 
    id_generator: Callable[..., Tag],
    task_scheduler: TaskScheduler,
    pre_sim_scheduler: TaskScheduler,
    id_map: IdMap = IdMap(), 
    render_map: Dict[str, Callable] = {}, 
    task_map: Dict[str, Callable] = {},
    entities_map: Dict[str, Callable] = {},
    likelihood_map:  Dict[str, Coin] = {},
    transition_conditions_map: Dict[str, Callable[[AgentCharacteristics],bool]] = {}
  ) -> None:
    self._id_map = id_map
    self._entities_map = entities_map
    self._likelihood_map = likelihood_map
    self._transition_conditions_map = transition_conditions_map
    self._agent_state_definitions: Dict[AgentStateName, AgentActionStateLike] = {}
    self._agent_transition_maps: Dict[AgentStateTransitionMapName, AgentActionSelector] = {}
    self._default_agent_states: DefaultAgentStateMap = DictWithDefault()
    
    self._parsers: List[SceneParser] = [
      CellSizeParser(),
      CanvasSizeParser(),
      SceneLayersParser(id_generator, render_map),
      AgentStatesParser(self._agent_state_definitions),
      DefaultAgentStatesParser(
        self._default_agent_states,
        self._agent_state_definitions
      ),
      AgentStateTransitionMapsParser(
        self._agent_state_definitions, 
        self._agent_transition_maps,
        self._default_agent_states,
        self._likelihood_map,
        self._transition_conditions_map
      ),
      AgentsParser(id_generator, id_map, self._agent_transition_maps, self._agent_state_definitions),
      PathsParser(id_generator, id_map, render_map),
      TasksParser(task_map, id_map, task_scheduler, pre_sim_scheduler),
      EntitiesParser(id_generator, render_map, entities_map, id_map),
      NavMeshJunctionParser(id_generator, render_map)
    ]

  def build(self, scene_data:SimpleNamespace) -> Scene:
    scene = Scene()

    for parser in self._parsers:
      parser.parse(scene_data, scene) 

    return scene