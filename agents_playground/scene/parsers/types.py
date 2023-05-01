from typing import Callable
from agents_playground.agents.spec.agent_action_state_spec import AgentActionStateLike
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.sys.dict_with_default import DictWithDefault

AgentStateName = str
AgentStateTransitionMapName = str
DefaultAgentStateMap = DictWithDefault[AgentStateTransitionMapName, AgentActionStateLike]
TransitionCondition = Callable[[AgentCharacteristics],bool]