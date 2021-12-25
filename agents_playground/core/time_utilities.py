from time import time as current_time_sec

MS_PER_SEC = 1000
TimeInMS = float

class TimeUtilities:
  @staticmethod
  def now() -> TimeInMS:
    """Finds the current time in milliseconds."""
    return current_time_sec() * MS_PER_SEC