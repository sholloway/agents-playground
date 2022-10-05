"""
Module that runs in its own process and collects metrics about the running 
simulation's hardware utilization. Communication between the processes is 
done via a shared uni-directional pipe.
"""
from __future__ import annotations

from collections import deque
from multiprocessing import Event, Pipe, Process
from multiprocessing.connection import Connection
import os
from random import randrange, uniform
from time import sleep
from typing import NamedTuple, Optional, Tuple

import dearpygui.dearpygui as dpg
import psutil
from agents_playground.core.constants import BYTES_IN_MB

from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import TimeInSecs

class PerformanceMonitor:
  def __init__(self) -> None:
    self.__process: Optional[Process] = None
    self.__stop = Event()

  def __del__(self):
    print("PerformanceMonitor deleted.")

  def start(self, monitor_pid: int) -> Connection:
    """Starts the monitor process.
    
    Args
      - monitor_pid: The process ID of the process that will be monitored.

    Returns
      The output connection of the process.
    """
    pipe_receive, pipe_send = Pipe(duplex=False)
  
    self.__process = Process(
      target=monitor, 
      name='child-process', 
      args=(monitor_pid, pipe_send, self.__stop),
      daemon=False
    )

    self.__process.start()
    return pipe_receive

  def stop(self) -> None:
    """Terminates the monitor process."""
    self.__stop.set()
    self.__process.join()
    print(f'Monitor Process Exit Code: {self.__process.exitcode}')
    self.__process.close()

def monitor(
  monitor_pid:int, 
  output_pipe: Connection, 
  stop: Event) -> None:
  print(f'Process Monitor started. {os.getpid()}')

  simulation_start_time: TimeInSecs = TimeUtilities.now_sec()

  SAMPLES_WINDOW = 20 #TODO: Pull into core constants module.
  MONITOR_FREQUENCY = 1 #TODO: Pull into core constants module.
  sim_running_time = Samples(SAMPLES_WINDOW, 0)
  frames_per_second = Samples(SAMPLES_WINDOW, 0)
  cpu_utilization = Samples(SAMPLES_WINDOW, 0)
  non_swapped_physical_memory_used = Samples(SAMPLES_WINDOW, 0)
  virtual_memory_used = Samples(SAMPLES_WINDOW, 0)
  memory_unique_to_process = Samples(SAMPLES_WINDOW, 0)
  page_faults = Samples(SAMPLES_WINDOW, 0)
  pageins = Samples(SAMPLES_WINDOW, 0)

  ps = psutil.Process(monitor_pid)

  try:
    while not stop.is_set():
      # 1. How long has the simulation been running?
      sim_running_time.collect(TimeUtilities.now_sec() - simulation_start_time) 

      # 2. What's the frame rate?
      #Note: This is the average over 120 frames.
      frames_per_second.collect(0) # dpg.get_frame_rate() This is making the process crash.    
      
      # 3. How heavy is the CPU(s) being taxed?
      # The CPU utilization for 1 second.
      cpu_utilization.collect(ps.cpu_percent(interval=1))     
      
      # 4. How much memory is being used?
      # memory_info = ps.memory_full_info()
      
      # “Resident Set Size” is the non-swapped physical memory a process has used.
      # Convert Bytes into MB
      non_swapped_physical_memory_used.collect(0) #memory_info.rss/BYTES_IN_MB 
      
      # Virtual Memory Size is the total amount of virtual memory used by the process.
      virtual_memory_used.collect(0) # memory_info.vms / BYTES_IN_MB

      # “Unique Set Size” is the memory which is unique to a process and which 
      # would be freed if the process was terminated right now.
      # uss is probably the most representative metric for determining how much 
      # memory is actually being used by a process. It represents the amount of 
      # memory that would be freed if the process was terminated right now.
      memory_unique_to_process.collect(0) #memory_info.uss / BYTES_IN_MB
      
      # How is the sim retrieving memory?
      # Page Faults are requests for more memory.
      page_faults.collect(0) #memory_info.pfaults

      # The total number of requests for pages from a pager.
      # https://www.unix.com/man-page/osx/1/vm_stat
      # Manually view this on the CLI with vm_stat
      pageins.collect(0) #memory_info.pageins
    
      metrics = Metrics(
        sim_running_time=sim_running_time,
        frames_per_second=frames_per_second,
        cpu_utilization=cpu_utilization,
        non_swapped_physical_memory_used=non_swapped_physical_memory_used,
        virtual_memory_used=virtual_memory_used,
        memory_unique_to_process=memory_unique_to_process,
        page_faults=page_faults,
        pageins=pageins
      )

      print('Performance Monitor Sending:')
      print(metrics)
      output_pipe.send(metrics)
      
      sleep(MONITOR_FREQUENCY)
    else:
      print('Asked to stop.')
  except Exception as e:
    print('The Performance Monitor threw an exception and stopped.')
    print(e)

class Metrics(NamedTuple):
  frames_per_second: Samples
  sim_running_time: int
  cpu_utilization: Samples
  non_swapped_physical_memory_used: Samples
  virtual_memory_used: Samples
  memory_unique_to_process: Samples
  page_faults: Samples
  pageins: Samples

class Samples:
  def __init__(self, length: int, baseline: float) -> None:
    self.__filo = deque([baseline]*length, maxlen=length)
    self.__latest_sample: int | float = 0

  def collect(self, sample: int | float) -> None:
    self.__latest_sample = sample
    self.__filo.append(sample)

  @property
  def samples(self) -> Tuple[int | float, ...]:
    return tuple(self.__filo)

  @property
  def latest(self) -> int | float:
    return self.__latest_sample


"""
Next Steps
- [ ] Potentially have sim_running time be separate from this entire thing. Might want to have a different freq.
- [X] Remove the existing hardware metrics collection from SimLoop.
- [X] Decide where to hook into for polling the outbound Pipe connection.
- [X] Wire up the latest sample values.
- [ ] Actually take the hardware samples.
- [ ] Add ToolTip plots for the sample trends.
- [ ] Replace the frame level metrics with the deque approach.
- [ ] Fix Tests
- [ ] Fix any typing errors.
- [ ] Write a short blog post about how this works.
"""