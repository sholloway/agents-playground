from dataclasses import dataclass
from typing import Callable, Dict, List, Union

from agents_playground.simulation.tag import Tag

Sample = Union[int, float]

@dataclass
class Statistic:
  id: Tag
  value: Sample

@dataclass
class SimulationStatistics:
  fps: Statistic
  samples: Dict[str, List[Sample]]
  __utilization: Statistic
  __utilization_samples: List[Sample]

  def __init__(self, id_generator: Callable) -> None:
    self.fps = Statistic(id_generator(), 0)
    self.__utilization = Statistic(id_generator(), 0)
    self.__utilization_samples = []

  @property
  def utilization(self) -> Statistic:
    return self.__utilization

  @property
  def utilization_sample(self) -> Sample:
    return self.__utilization.value  

  @utilization_sample.setter
  def utilization_sample(self, sample: Sample) -> None:
    self.__utilization.value = sample
    self.__utilization_samples.append(sample)

  def consume_utility_samples(self) -> List[Sample]:
    consume = self.__utilization_samples
    self.__utilization_samples = []
    return consume
  
  def consume_samples(self, sample_name) -> List[Sample]:
    consume = self.samples[sample_name]
    self.samples[sample_name] = []
    return consume