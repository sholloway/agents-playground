

import os

import dearpygui.dearpygui as dpg
import psutil
from agents_playground.core.constants import BYTES_IN_MB, MS_PER_SEC

from agents_playground.core.performance_metrics import PerformanceMetrics
from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import TimeInMS, TimeInSecs


# https://landley.net/writing/memory-faq.txt
class SimulationPerformance:
  @staticmethod
  def collect(started_time: TimeInSecs) -> PerformanceMetrics:
    metrics = dict()
    # 0. Identify the operating system level process the simulation is running in.
    pid = os.getpid()
    ps = psutil.Process(pid)

    # 1. Collect any dpg specific metrics.
    metrics['sim_running_time'] = TimeUtilities.now_sec() - started_time # UOM is seconds.
    metrics['frames_per_second'] = dpg.get_frame_rate() #Note: Average over 120 frames.

    with ps.oneshot():
      cpu_percent = 0
      memory_info = ps.memory_full_info()

    # 2. Is there anything about the GPU we care about?
    # Note: I don't currently have a recipe for monitoring the GPU. Everything 
    # Appears to be specific to Nvidia cards which don't apply to my Mac hardware.

    # 3. How is the simulation consuming memory?
    # “Resident Set Size” is the non-swapped physical memory a process has used.
    # Convert Bytes into MB
    metrics['non_swapped_physical_memory_used'] = memory_info.rss / BYTES_IN_MB

    # Virtual Memory Size is the total amount of virtual memory used by the process.
    metrics['virtual_memory_used'] = memory_info.vms / BYTES_IN_MB

    # How is the sim retrieving memory?
    # Page Faults are requests for more memory.
    metrics['page_faults'] = memory_info.pfaults
    
    # The total number of requests for pages from a pager.
    # https://www.unix.com/man-page/osx/1/vm_stat
    # Manually view this on the CLI with vm_stat
    metrics['pageins'] = memory_info.pageins

    # “Unique Set Size” is the memory which is unique to a process and which 
    # would be freed if the process was terminated right now.
    # uss is probably the most representative metric for determining how much 
    # memory is actually being used by a process. It represents the amount of 
    # memory that would be freed if the process was terminated right now.
    metrics['memory_unique_to_process'] = memory_info.uss / BYTES_IN_MB
    
    # 4. How is the simulation utilizing the CPU? (Utilization, Caches?)
    # Return a float representing the process CPU utilization as a percentage 
    # which can also be > 100.0 in case of a process running multiple threads on 
    # different CPUs.
    metrics['cpu_utilization'] = cpu_percent
    
    return PerformanceMetrics(**metrics)