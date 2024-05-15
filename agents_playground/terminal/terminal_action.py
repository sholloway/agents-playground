from enum import Enum, auto


class TerminalAction(Enum):
    DO_NOTHING = auto()
    CLOSE_TERMINAL = auto()
    TYPE = auto()
    DELETE = auto()
    RUN = auto()
    NEW_LINE = auto()
    DISPLAY_PREVIOUS = auto()
    DISPLAY_NEXT = auto()
    MOVE_PROMPT_LEFT = auto()
    MOVE_PROMPT_RIGHT = auto()
    MOVE_PROMPT_DOWN = auto()
    MOVE_PROMPT_UP = auto()
