from dataclasses import dataclass
from typing import Callable, Dict, List, Union

from attr import field
from agents_playground.core.performance_metrics import PerformanceMetrics

from agents_playground.simulation.tag import Tag

Sample = Union[int, float]

@dataclass
class SimulationStatistics:
  samples: Dict[str, List[Sample]]  
  hardware_metrics: PerformanceMetrics = field(init=False)

  def consume_samples(self, sample_name) -> List[Sample]:
    consume = self.samples[sample_name]
    self.samples[sample_name] = []
    return consume