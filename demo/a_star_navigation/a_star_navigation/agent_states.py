from agents_playground.agents.default_agent import NamedAgentState

IDLE_STATE = NamedAgentState('IDLE')
RESTING_STATE = NamedAgentState('RESTING')
PLANNING_STATE = NamedAgentState('PLANNING')
ROUTING_STATE = NamedAgentState('ROUTING')
TRAVELING_STATE = NamedAgentState('TRAVELING')

AgentStateMap = {
  IDLE_STATE: IDLE_STATE,
  RESTING_STATE: PLANNING_STATE,
  PLANNING_STATE: ROUTING_STATE,
  ROUTING_STATE: TRAVELING_STATE,
  TRAVELING_STATE: RESTING_STATE
}