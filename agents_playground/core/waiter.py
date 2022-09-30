from time import sleep
from agents_playground.core.constants import MS_PER_SEC

from agents_playground.core.time_utilities import TimeUtilities
from agents_playground.core.types import TimeInMS, TimeInSecs

class Waiter:
  def wait(self, time_to_wait: TimeInSecs) -> None:
    sleep(time_to_wait)

  def wait_until_deadline(self, time_to_deadline:TimeInMS) -> None:
    wait_time: TimeInSecs = (time_to_deadline - TimeUtilities.now())/MS_PER_SEC
    if wait_time > 0:
      self.wait(wait_time)