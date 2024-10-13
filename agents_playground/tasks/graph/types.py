from enum import StrEnum


class TaskGraphPhase(StrEnum):
    INITIALIZATION = "INITIALIZATION"
    FRAME_DRAW = "FRAME_DRAW"
    SHUTDOWN = "SHUTDOWN"


class TaskGraphError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)
