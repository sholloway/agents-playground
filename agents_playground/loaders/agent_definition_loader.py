from dataclasses import dataclass
from agents_playground.loaders import JSONFileLoader

AGENT_DEF_SCHEMA_PATH = 'agents_playground/agents/file/agent_def.schema.json'

@dataclass 
class AgentDefinition:
  pass 

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