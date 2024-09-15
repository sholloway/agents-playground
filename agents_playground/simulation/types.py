from typing import Protocol
import wx


class SimulationError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SimulationLike(Protocol):
    def bind_event_listeners(self, frame: wx.Panel) -> None: ...
    def launch(self) -> None: ...
    def shutdown(self) -> None: ...
