
from agents_playground.agents.agent_spec import (
  AgentActionSelector,
  AgentActionStateLike,
  AgentActionableState,
  AgentIdentityLike, 
  AgentLike, 
  AgentMovementController, 
  AgentPhysicalityLike, 
  AgentPositionLike, 
  AgentStateLike, 
  AgentStyleLike
)
from agents_playground.funcs import map_get_or_raise

class NamedAgentState(AgentActionStateLike):
  def __init__(self, name: str) -> None:
    self.name = name

class MapAgentActionSelectorException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class MapAgentActionSelector(AgentActionSelector):
  def __init__(
    self, 
    state_map: dict[AgentActionStateLike, AgentActionStateLike]
  ) -> None:
    self._state_map: dict[AgentActionStateLike, AgentActionStateLike] = state_map

  def next_action(self, current_action: AgentActionStateLike) -> AgentActionStateLike:
    return map_get_or_raise(
      self._state_map, 
      current_action, 
      MapAgentActionSelectorException(
        f'The Agent state map does not have a registered state named {current_action}'
      )
    ) 

  def __repr__(self) -> str:
    """An implementation of the dunder __repr__ method. Used for debugging."""
    model_rep = ''
    for k,v in self.model.items():
      model_rep = model_rep + f'{k} -> {v}\n'
    return f'{self.__class__.__name__}\n{model_rep}' 

class DefaultAgentState(AgentStateLike):
  def __init__(
    self, 
    initial_state: AgentActionableState, 
    action_selector: AgentActionSelector,
    agent_is_selected: bool = False,
    initially_requires_scene_graph_update: bool = False,
    initially_requires_render: bool             = False,
    is_visible: bool                            = True
  ) -> None:
    self.current_action_state: AgentActionableState     = initial_state   
    self.last_action_state: AgentActionableState | None = None
    self.action_selector: AgentActionSelector           = action_selector        
    self.selected: bool                                 = agent_is_selected                      
    self.require_scene_graph_update: bool               = initially_requires_scene_graph_update      
    self.require_render: bool                           = initially_requires_render                   
    self.visible: bool                                  = is_visible  

  def reset(self) -> None:
    self.require_scene_graph_update = False
    self.require_render = False

  def transition_to_next_action(self) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = self.action_selector.next_action(self.current_action_state)

  def assign_action_state(self, next_state: AgentActionableState) -> None:
    self.last_action_state    = self.current_action_state
    self.current_action_state = next_state

class DefaultAgentStyle(AgentStyleLike):
  ...

class DefaultAgentIdentity(AgentIdentityLike):
  ...

class DefaultAgentPhysicality(AgentPhysicalityLike):
  ...

class DefaultAgentPosition(AgentPositionLike):
  ...

class DefaultAgentMovementController(AgentMovementController):
  ...

class DefaultAgent(AgentLike):
  ...