from dataclasses import dataclass
from agents_playground.loaders import JSONFileLoader
from agents_playground.spatial.vector import vector
from agents_playground.spatial.frustum import Frustum
from agents_playground.spatial.vector.vector import Vector

AGENT_DEF_SCHEMA_PATH = 'agents_playground/agents/file/agent_def.schema.json'

@dataclass
class ModelTransformation:
  translation: Vector
  rotation: Vector
  scale: Vector

@dataclass
class FsmAgentStateModel:
  agent_states: list[str]
  state_transition_map: dict #Note: I think I've already got a class built for this...
  initial_agent_state: str

@dataclass 
class AgentDefinition:
  agent_model: str # TODO: Figure out where/when to load the model.
  model_transformation: ModelTransformation
  view_frustum: Frustum
  agent_state_model: FsmAgentStateModel

  def __post_init__(self) -> None:
    """
    Handle converting from JSON populated members to their correct objects.
    """
    if isinstance(self.model_transformation, dict):
      self.model_transformation = ModelTransformation(
        translation = vector(*self.model_transformation['translation']),
        rotation = vector(*self.model_transformation['rotation']),
        scale = vector(*self.model_transformation['scale'])
      )

class AgentDefinitionLoader:
  def __init__(self):
    self._json_loader = JSONFileLoader()

  def load(self, agent_def_path: str) -> AgentDefinition:
    loader_context = {}
    self._json_loader.load(
      context     = loader_context, 
      schema_path = AGENT_DEF_SCHEMA_PATH, 
      file_path   = agent_def_path
    )
    json_obj: dict = loader_context['json_content']
    return AgentDefinition(**json_obj)