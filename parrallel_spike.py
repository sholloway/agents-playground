"""
A independent spike on getting two processes to communicate.

Todo
- 1. The main process needs to fire up a thread that serves as the "primary".
- 2. The primary thread should spawn a child process.
- 2. In the child process perform a task, then sleep for a bit.
- 3. Have the main process access the task result and print it out.
- After the above works, have the child process do the psutil stuff.


Questions
- Is there anyway to make consuming from a pipe be event driven rather than 
  polling the pipe?
"""
from __future__ import annotations
from multiprocessing.connection import Connection

from collections import deque
import os
import multiprocessing as mp
import threading
from random import randrange, uniform, sample
from time import sleep
from enum import Enum
from typing import Callable, NamedTuple, Tuple, Union


def run_two_threads() -> None:
  """An example of how to spin up two threads in the same process."""
  app_a = ThreadedApp(lambda: print('App A'), 0.5, 'app_a')
  app_b = ThreadedApp(lambda: print('App B'), 1, 'app_b')

  app_a.launch()
  app_b.launch()

  while True:
    # Simulate having the UI around that prevents the Main function from finishing.
    sleep(1)

def spawn_a_process() -> None:
  """Spin up thread and a child process that work together."""
  # 1. Create a one way pipe for the process to send the metrics.
  pipe_receive, pipe_send = mp.Pipe(duplex=False)

  # 2. Create the separate process that is responsible for collecting the metrics.
  child_process = mp.Process(
    target=child_process_work, 
    name='child-process', 
    args=(os.getpid(), pipe_send),
    daemon=True
  )

  child_process.start()

  #3. Create a thread that will be doing work on a loop. This represents 
  #  the SimLoop thread.
  app = ThreadedApp(lambda: print('App A'), 0.5, 'app')
  app.launch()

  # 4. On the main thread poll the process connection to get the metrics to display.
  #  This represents the Simulation class.
  # This is also keeping the main thread from ending. 
  while True:
    # Simulate having the UI around that prevents the Main function from finishing.
    if pipe_receive.poll(0.01):
      msg = pipe_receive.recv()
      print(f'Received: {msg}')
    sleep(1)

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

  def collect(self, sample: int | float) -> None:
    self.__filo.append(sample)

  def samples(self) -> Tuple[int | float, ...]:
    return tuple(self.__filo)

def child_process_work(parent_pid, output_pipe: Connection) -> None:
  print(f'My process id is {os.getpid()} and my parent id is {parent_pid}')

  SAMPLES_WINDOW = 20
  frames_per_second = Samples(SAMPLES_WINDOW, 0)
  cpu_utilization = Samples(SAMPLES_WINDOW, 0)
  non_swapped_physical_memory_used = Samples(SAMPLES_WINDOW, 0)
  virtual_memory_used = Samples(SAMPLES_WINDOW, 0)
  memory_unique_to_process = Samples(SAMPLES_WINDOW, 0)
  page_faults = Samples(SAMPLES_WINDOW, 0)
  pageins = Samples(SAMPLES_WINDOW, 0)

  while True:
    frames_per_second.collect(randrange(55,60))
    cpu_utilization.collect(uniform(33,88))
    non_swapped_physical_memory_used.collect(uniform(33,88))
    virtual_memory_used.collect(uniform(33,88))
    memory_unique_to_process.collect(uniform(33,88))
    page_faults.collect(randrange(1000,5000))
    pageins.collect(randrange(1000,5000))

    output_pipe.send(Metrics(
      frames_per_second=frames_per_second.samples(),
      sim_running_time=23456781,
      cpu_utilization=cpu_utilization.samples(),
      non_swapped_physical_memory_used=non_swapped_physical_memory_used.samples(),
      virtual_memory_used=virtual_memory_used.samples(),
      memory_unique_to_process=memory_unique_to_process.samples(),
      page_faults=page_faults.samples(),
      pageins=pageins.samples()
    ))
    sleep(2)


class AppState(Enum):
  INITIALIZED = 0
  RUNNING = 1
  STOPPED = 2

TimeInSecs = int

class ThreadedApp:
  def __init__(self, work: Callable, frequency: TimeInSecs, id: str) -> None:
    self.__thread = None
    self.__state = AppState.INITIALIZED
    self.__work = work
    self.__frequency = frequency
    self.__id = id

  def launch(self) -> None:
    self.__state = AppState.RUNNING
    self.__thread = threading.Thread( 
      name=self.__id, 
      target=self.__app_loop, 
      args=(), 
      daemon=True
    )
    self.__thread.start()

  def __app_loop(self) -> None:
    while self.__state == AppState.RUNNING:    
      self.__work()
      sleep(self.__frequency)

  def end(self) -> None:
    self.__state = AppState.STOPPED
    self.__thread.join()

if __name__ == "__main__":
  spawn_a_process()
