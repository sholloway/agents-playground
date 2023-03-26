from typing import Callable
from agents_playground.agents.spec.agent_characteristics import AgentCharacteristics
from agents_playground.scene.parsers.default_agent_states_parser import DefaultAgentStates


AgentStateName = str
AgentStateTransitionMapName = str
DefaultAgentStatesDict = DefaultAgentStates[AgentStateTransitionMapName, AgentStateTransitionMapName]
TransitionCondition = Callable[[AgentCharacteristics],bool]