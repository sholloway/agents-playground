from collections import deque
from dataclasses import dataclass
from typing import Sequence, Tuple

from agents_playground.core.types import Sample
from agents_playground.counter.counter import Counter, CounterBuilder


class SamplesWindow:
    """
    Represents a stream of numerical measurements.
    """
    def __init__(self, length: int, baseline: float) -> None:
        self._fifo = deque([baseline] * length, maxlen=length)
        self._collected: Counter[int] = CounterBuilder.count_up_from_zero()

    def collected(self) -> int:
        """Returns the number of samples collected in the current window."""
        return self._collected.value()
    
    def collect(self, sample: Sample) -> None:
        """Record a sample."""
        self._fifo.append(sample)
        self._collected.increment()

    def reset_count(self) -> None:
        """Reset the counter for the number of samples collected in the current window."""
        self._collected.reset()

    @property
    def samples(self) -> Tuple[Sample, ...]:
        return tuple(self._fifo)

    @property
    def latest(self) -> Sample:
        return self._fifo[-1]


@dataclass
class SamplesDistribution:
    collected_per_window: int
    size: int
    avg: float
    min: Sample
    p25: Sample
    p50: Sample
    p75: Sample
    max: Sample
    samples: Tuple[Sample, ...]
    
    def stats_as_list(self, precision: int=2) -> list:
        return [
            self.collected_per_window, 
            self.size, 
            round(self.avg, precision), 
            round(self.min, precision), 
            round(self.p25, precision), 
            round(self.p50, precision), 
            round(self.p75, precision), 
            round(self.max, precision)
        ]