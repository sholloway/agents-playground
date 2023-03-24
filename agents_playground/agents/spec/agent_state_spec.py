from abc import abstractmethod
from typing import Protocol

from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics

class AgentStateLike(Protocol):
  current_action_state: AgentActionStateLike     
  last_action_state: AgentActionStateLike | None 
  action_selector: AgentActionSelector            
  selected: bool                         
  require_scene_graph_update: bool       
  require_render: bool                   
  visible: bool                          

  @abstractmethod
  def reset(self) -> None:
    ...

  @abstractmethod
  def transition_to_next_action(self, agent_characteristics: AgentCharacteristics) -> None:
    ...

  @abstractmethod
  def assign_action_state(self, next_state: AgentActionStateLike) -> None:
    ...

  def set_visibility(self, is_visible: bool) -> None:
    self.visible = is_visible
    self.require_render = True