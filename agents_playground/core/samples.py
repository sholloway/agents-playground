from collections import deque
from dataclasses import dataclass
from typing import Sequence, Tuple

from agents_playground.core.types import Sample


class SamplesWindow:
    """
    Represents a stream of numerical measurements.
    """
    def __init__(self, length: int, baseline: float) -> None:
        self.__fifo = deque([baseline] * length, maxlen=length)

    def collect(self, sample: Sample) -> None:
        self.__fifo.append(sample)

    @property
    def samples(self) -> Tuple[Sample, ...]:
        return tuple(self.__fifo)

    @property
    def latest(self) -> Sample:
        return self.__fifo[-1]


@dataclass
class SamplesDistribution:
    size: int
    avg: float
    min: Sample
    p25: Sample
    p50: Sample
    p75: Sample
    max: Sample

    def to_list(self, precision: int=2) -> list:
        return [
            self.size, 
            round(self.avg, 2), 
            round(self.min, 2), 
            round(self.p25, 2), 
            round(self.p50, 2), 
            round(self.p75, 2), 
            round(self.max, 2)
        ]