from time import process_time

from agents_playground.core.constants import MS_PER_SEC, SECS_PER_DAY, SECS_PER_HOUR, SECS_PER_MINUTE
from agents_playground.core.types import TimeInMS

class TimeUtilities:
  @staticmethod
  def now() -> TimeInMS:
    """Finds the current time in milliseconds."""
    return process_time() * MS_PER_SEC

  @staticmethod
  def display_seconds(total_seconds: int) -> str:
    """
    Number of days = ⌊ n / (24 * 3600) ⌋ 
    Number of Hours = ⌊ (n % (24 * 3600)) / 3600 ⌋ 
    Number of Minutes = ⌊ (n % (24 * 3600 * 3600)) / 60 ⌋ 
    Number of Seconds = ⌊ (n % (24 * 3600 * 3600 * 60)) / 60 ⌋
    """
    days = total_seconds // SECS_PER_DAY

    time_left = total_seconds % SECS_PER_DAY
    hours = time_left // SECS_PER_HOUR

    time_left %= SECS_PER_HOUR
    minutes = time_left // SECS_PER_MINUTE

    seconds = time_left % SECS_PER_MINUTE

    return f"{days:02}:{hours:02}:{minutes:02}:{seconds:02}"