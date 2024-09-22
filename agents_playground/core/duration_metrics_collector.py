from functools import wraps
from math import floor
import statistics
from typing import Any, Callable
from agents_playground.core.samples import SamplesWindow, SamplesDistribution
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import Sample, TimeInMS


class DurationMetricsCollector:
    def __init__(self) -> None:
        self._samples: dict[str, SamplesWindow] = dict()

    def collect(self, metric_name, sample: Sample, count: int) -> None:
        """Collect samples as a series.

        Args:
          - metric_name: The name to record the sample as.
          - Sample: The sample to save.
          - count: How many samples to track. Older samples roll off.
        """
        if metric_name not in self._samples:
            self._samples[metric_name] = SamplesWindow(count, 0)
        self._samples[metric_name].collect(sample)

    @property
    def samples(self) -> dict[str, SamplesWindow]:
        return self._samples

    def clear(self) -> None:
        self._samples.clear()

    def reset_sample_window_counters(self) -> None:
        """Resets the window on all sample windows."""
        for samples_window in self._samples.values():
            samples_window.reset_count()

    def aggregate(self) -> dict[str, SamplesDistribution]:
        """
        Calculates the aggregated metrics for all of the Samples.
        """
        distributions: dict[str, SamplesDistribution] = {}
        for metric_name, samples_window in self._samples.items():
            sorted_samples: list[Sample] = sorted(samples_window.samples)
            count = len(sorted_samples)
            distributions[metric_name] = SamplesDistribution(
                collected_per_window=samples_window.collected(),
                size=count,
                avg=statistics.fmean(sorted_samples),
                min=sorted_samples[0],
                p25=sorted_samples[floor(count * 0.25)],
                p50=sorted_samples[floor(count * 0.50)],
                p75=sorted_samples[floor(count * 0.75)],
                max=sorted_samples[count - 1],
                samples=samples_window.samples,
            )
        return distributions


_duration_metrics = DurationMetricsCollector()


def sample_duration(sample_name: str, count: int) -> Callable:
    """Take a measurement of a function's duration.

    Args:
      - sample_name: The name to record the sample as.
      - count: How many samples to track. Older samples roll off.
    """

    def decorator_sample(func) -> Callable:
        @wraps(func)
        def wrapper_sample(*args, **kwargs) -> Any:
            start: TimeInMS = TimeUtilities.process_time_now()
            result = func(*args, **kwargs)
            end: TimeInMS = TimeUtilities.process_time_now()
            duration: TimeInMS = end - start
            _duration_metrics.collect(sample_name, duration, count)
            return result

        return wrapper_sample

    return decorator_sample


def collected_duration_metrics() -> DurationMetricsCollector:
    """Use to access the duration metrics outside of this module."""
    return _duration_metrics
