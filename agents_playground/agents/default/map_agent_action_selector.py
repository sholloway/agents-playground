from agents_playground.agents.default.map_agent_action_selector_exception import MapAgentActionSelectorException
from agents_playground.agents.spec.agent_action_selector_spec import AgentActionSelector
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.agents.spec.agent_state_spec import AgentActionStateLike
from agents_playground.funcs import map_get_or_raise


class MapAgentActionSelector(AgentActionSelector):
  def __init__(
    self, 
    state_map: dict[AgentActionStateLike, AgentActionStateLike]
  ) -> None:
    self._state_map: dict[AgentActionStateLike, AgentActionStateLike] = state_map

  def next_action(
    self,
    agent_characteristics: AgentCharacteristics, 
    current_action: AgentActionStateLike
  ) -> AgentActionStateLike:
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
    for k,v in self._state_map.items():
      model_rep = model_rep + f'{k} -> {v}\n'
    return f'{self.__class__.__name__}\n{model_rep}'