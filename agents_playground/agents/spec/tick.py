from abc import abstractmethod
from typing import Protocol


class Tick(Protocol):
    """
    Implementations must define a tick method that is invoked once per frame.
    This enables implementations to have a standardized way of capturing
    the passing of frames. This is intended for running code when only N
    number of frames have passed by.
    """

    @abstractmethod
    def tick(self) -> None: ...
