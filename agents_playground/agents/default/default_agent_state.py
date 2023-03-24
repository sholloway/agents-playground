from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_spec import AgentLike
from agents_playground.agents.spec.agent_state_spec import AgentActionStateLike, AgentStateLike

class DefaultAgentState(AgentStateLike):
  def __init__(
    self, 
    initial_state: AgentActionStateLike, 
    action_selector: AgentActionSelector,
    agent_is_selected: bool = False,
    initially_requires_scene_graph_update: bool = False,
    initially_requires_render: bool             = False,
    is_visible: bool                            = True
  ) -> None:
    self.current_action_state: AgentActionStateLike     = initial_state   
    self.last_action_state: AgentActionStateLike | None = None
    self.action_selector: AgentActionSelector           = action_selector        
    self.selected: bool                                 = agent_is_selected                      
    self.require_scene_graph_update: bool               = initially_requires_scene_graph_update      
    self.require_render: bool                           = initially_requires_render                   
    self.visible: bool                                  = is_visible  

  def reset(self) -> None:
    self.require_scene_graph_update = False
    self.require_render = False

  def transition_to_next_action(self, agent_characteristics: AgentCharacteristics) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = self.action_selector.next_action(
      agent_characteristics, 
      self.current_action_state
    )

  def assign_action_state(self, next_state: AgentActionStateLike) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = next_state