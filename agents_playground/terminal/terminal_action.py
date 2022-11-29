from enum import Enum, auto

class TerminalAction(Enum):
  DO_NOTHING      = auto()
  CLOSE_TERMINAL  = auto()
  TYPE            = auto()
  DELETE          = auto()
  RUN             = auto()