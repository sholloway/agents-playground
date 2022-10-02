"""
A independent spike on getting two processes to communicate.

Todo
- 1. The main process needs to fire up a thread that serves as the "primary".
- 2. The primary thread should spawn a child process.
- 2. In the child process perform a task, then sleep for a bit.
- 3. Have the main process access the task result and print it out.
- After the above works, have the child process do the psutil stuff.
"""

import threading
from time import sleep
from enum import Enum
from typing import Callable

def main() -> None:
  app_a = ThreadedApp(lambda: print('App A'), 0.5, 'app_a')
  app_b = ThreadedApp(lambda: print('App B'), 1, 'app_b')

  app_a.launch()
  app_b.launch()

  while True:
    # Simulate having the UI around that prevents the Main function from finishing.
    sleep(1)

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
  main()