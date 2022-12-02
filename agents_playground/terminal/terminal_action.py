from enum import Enum, auto

class TerminalAction(Enum):
  DO_NOTHING        = auto()
  CLOSE_TERMINAL    = auto()
  TYPE              = auto()
  DELETE            = auto()
  RUN               = auto()
  DISPLAY_PREVIOUS  = auto()
  DISPLAY_NEXT      = auto()
  MOVE_PROMPT_LEFT  = auto()
  MOVE_PROMPT_RIGHT = auto()