from dataclasses import dataclass
from typing import Callable, List, Union

from agents_playground.simulation.tag import Tag

Sample = Union[int, float]

@dataclass
class Statistic:
  id: Tag
  value: Sample

@dataclass
class SimulationStatistics:
  fps: Statistic
  __utilization: Statistic
  __utilization_samples: List[Sample]

  def __init__(self, id_generator: Callable) -> None:
    self.fps = Statistic(id_generator(), 0)
    self.__utilization = Statistic(id_generator(), 0)
    self.__utilization_samples = []

  @property
  def utilization(self) -> Statistic:
    return self.__utilization

  @utilization.setter
  def utilization(self, sample: Sample) -> None:
    self.__utilization.value = sample
    self.__utilization_samples.append(sample)

  def consume_samples(self) -> List[Sample]:
    consume = self.__utilization_samples
    self.__utilization_samples = []
    return consume