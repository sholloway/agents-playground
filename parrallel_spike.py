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

import os
import multiprocessing as mp
import threading
from random import randrange, uniform, sample
from time import sleep
from enum import Enum
from typing import Callable, NamedTuple


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
  frames_per_second: float
  sim_running_time: int
  cpu_utilization: float
  non_swapped_physical_memory_used: float
  virtual_memory_used: float
  memory_unique_to_process: float
  page_faults: float
  pageins: float

def child_process_work(parent_pid, output_pipe: Connection) -> None:
  print(f'My process id is {os.getpid()} and my parent id is {parent_pid}')

  while True:
    output_pipe.send(Metrics(
      frames_per_second=[randrange(55,59) for _ in range(20)],
      sim_running_time=randrange(1000000, 10000000),
      cpu_utilization=[uniform(33, 120) for _ in range(20)],
      non_swapped_physical_memory_used=[uniform(33, 88) for _ in range(20)],
      virtual_memory_used=[uniform(33, 88) for _ in range(20)],
      memory_unique_to_process=uniform(33, 88),
      page_faults=[randrange(1000, 5000) for _ in range(20)],
      pageins=[randrange(1000, 5000) for _ in range(20)]
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