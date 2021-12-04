from enum import Enum
from typing import Union
from observe import Observable

class SimulationEvents(Enum):
  WINDOW_CLOSED = 'WINDOW_CLOSED'

class Simulation(Observable):
  _primary_window_ref: Union[int, str]

  def __init__(self) -> None:
    super().__init__()

  def set_primary_window(self, primary_window_ref: Union[int, str]) -> None:
    self._primary_window_ref = primary_window_ref

  def primary_window(self) -> Union[int, str]:
    return self._primary_window_ref