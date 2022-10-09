from collections import deque
from typing import Tuple

from agents_playground.core.types import Sample


class Samples:
  def __init__(self, length: int, baseline: float) -> None:
    self.__filo = deque([baseline]*length, maxlen=length)
    self.__latest_sample: Sample = 0

  def collect(self, sample: Sample) -> None:
    self.__latest_sample = sample
    self.__filo.append(sample)

  @property
  def samples(self) -> Tuple[Sample, ...]:
    return tuple(self.__filo)

  @property
  def latest(self) -> Sample:
    return self.__latest_sample