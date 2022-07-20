from time import sleep

from agents_playground.core.time_utilities import TimeInSecs

class Waiter:
  def wait(self, time_to_wait: TimeInSecs) -> None:
    sleep(time_to_wait)