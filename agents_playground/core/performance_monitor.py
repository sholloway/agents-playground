"""
Module that runs in its own process and collects metrics about the running 
simulation's hardware utilization. Communication between the processes is 
done via a shared uni-directional pipe.
"""

from multiprocessing import Event, Pipe, Process
from multiprocessing.connection import Connection
import os
from time import sleep
from typing import Optional

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
  while not stop.is_set():
    print(f'Monitoring process {monitor_pid}')
    sleep(1)
  else:
    print('Asked to stop.')