from typing import NamedTuple

from agents_playground.core.types import Count, MegaBytes, Percentage, TimeInSecs


class PerformanceMetrics(NamedTuple):
  frames_per_second: float
  sim_running_time: TimeInSecs
  non_swapped_physical_memory_used: MegaBytes
  virtual_memory_used: MegaBytes
  page_faults: Count
  pageins: Count
  memory_unique_to_process: MegaBytes
  cpu_utilization: Percentage