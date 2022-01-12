from dataclasses import dataclass
from typing import Callable, Union

from agents_playground.simulation.tag import Tag

@dataclass
class Statistic:
  id: Tag
  value: Union[int, float]

@dataclass
class SimulationStatistics:
  fps: Statistic
  utilization: Statistic

  def __init__(self, id_generator: Callable) -> None:
    self.fps = Statistic(id_generator(), 0)
    self.utilization = Statistic(id_generator(), 0)