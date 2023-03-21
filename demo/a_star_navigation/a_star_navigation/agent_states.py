from agents_playground.agents.agent_spec import AgentMovementAttributes
from agents_playground.agents.default_agent import NamedAgentState
from agents_playground.counter.counter import Counter
from agents_playground.paths.interpolated_path import InterpolatedPath

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

class PathConstrainedAgentMovement(AgentMovementAttributes):
  resting_counter: Counter 

  # These attributes are initialized by the relevant movement task when needed.
  active_route: InterpolatedPath 
  active_path_segment: int
  walking_speed: float
  active_t: float

  def __init__(self) -> None:
    # If an agent is resting, this counts the number of frames to rest for.
    self.resting_counter = Counter(
      start=60, # The number of frames to rest.
      decrement_step=1, 
      min_value=0
    )