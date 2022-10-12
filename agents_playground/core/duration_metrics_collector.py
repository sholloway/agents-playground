from functools import wraps
from typing import Any, Callable, Dict
from agents_playground.core.samples import Samples
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import Sample, TimeInMS

class DurationMetricsCollector:
  def __init__(self) -> None:
    self.__samples: Dict[str, Samples] = dict()

  def collect(self, metric_name, sample: Sample, count: int) -> None:
    """Collect samples as a series.
    
    Args:
      - metric_name: The name to record the sample as.
      - Sample: The sample to save.
      - count: How many samples to track. Older samples roll off.
    """
    if metric_name not in self.__samples:
      self.__samples[metric_name] = Samples(count, 0)
    self.__samples[metric_name].collect(sample)

  @property
  def samples(self) -> Dict[str, Samples]:
    return self.__samples

  def clear(self) -> None:
    self.__samples.clear()

_duration_metrics = DurationMetricsCollector()

def sample_duration(sample_name:str, count:int) -> Callable:
  """ Take a measurement of a function's duration.
  
  Args:
    - sample_name: The name to record the sample as.
    - count: How many samples to track. Older samples roll off.
  """
  def decorator_sample(func) -> Callable:
    @wraps(func)
    def wrapper_sample(*args, **kargs) -> Any:
      start: TimeInMS = TimeUtilities.now()
      result = func(*args, **kargs)
      end: TimeInMS = TimeUtilities.now()
      duration: TimeInMS = end - start
      _duration_metrics.collect(sample_name, duration, count)
      return result
    return wrapper_sample
  return decorator_sample

def collected_duration_metrics() -> DurationMetricsCollector:
  """Use to access the duration metrics outside of this module."""
  return _duration_metrics
