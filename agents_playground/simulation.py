from enum import Enum
from observe import Observable

class SimulationEvents(Enum):
  WINDOW_CLOSED = 'WINDOW_CLOSED'

class Simulation(Observable):
  def __init__(self) -> None:
    super().__init__()