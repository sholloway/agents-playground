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

  SAMPLES_WINDOW = 20 #TODO: Pull into core constants module.
  MONITOR_FREQUENCY = 1 #TODO: Pull into core constants module.
  frames_per_second = Samples(SAMPLES_WINDOW, 0)
  cpu_utilization = Samples(SAMPLES_WINDOW, 0)
  non_swapped_physical_memory_used = Samples(SAMPLES_WINDOW, 0)
  virtual_memory_used = Samples(SAMPLES_WINDOW, 0)
  memory_unique_to_process = Samples(SAMPLES_WINDOW, 0)
  page_faults = Samples(SAMPLES_WINDOW, 0)
  pageins = Samples(SAMPLES_WINDOW, 0)

  while not stop.is_set():
    frames_per_second.collect(randrange(55,60))
    cpu_utilization.collect(uniform(33,88))
    non_swapped_physical_memory_used.collect(uniform(33,88))
    virtual_memory_used.collect(uniform(33,88))
    memory_unique_to_process.collect(uniform(33,88))
    page_faults.collect(randrange(1000,5000))
    pageins.collect(randrange(1000,5000))
   
    output_pipe.send(Metrics(
      frames_per_second=frames_per_second,
      sim_running_time=23456781,
      cpu_utilization=cpu_utilization,
      non_swapped_physical_memory_used=non_swapped_physical_memory_used,
      virtual_memory_used=virtual_memory_used,
      memory_unique_to_process=memory_unique_to_process,
      page_faults=page_faults,
      pageins=pageins
    ))
    
    sleep(MONITOR_FREQUENCY)
  else:
    print('Asked to stop.')

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
- [ ] Potentially have sim_running time be separate from this entire thing. Might want to different freqency.
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