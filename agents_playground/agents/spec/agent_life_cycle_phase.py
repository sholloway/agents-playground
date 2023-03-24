from enum import Enum, auto


class AgentLifeCyclePhase(Enum):
  PRE_STATE_CHANGE  = auto()
  POST_STATE_CHANGE = auto()