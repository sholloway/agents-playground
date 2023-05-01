from enum import Enum
from agents_playground.agents.spec.agent_spec import AgentMovementAttributes
from agents_playground.counter.counter import Counter
from agents_playground.paths.interpolated_path import InterpolatedPath

# An enumeration to simplify referring to the states defined in the scene.toml file.
class AgentStateNames(Enum):
  IDLE_STATE      = 'IDLE_STATE'
  RESTING_STATE   = 'RESTING_STATE'
  PLANNING_STATE  = 'PLANNING_STATE'
  ROUTING_STATE   = 'ROUTING_STATE'
  TRAVELING_STATE = 'TRAVELING_STATE'

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