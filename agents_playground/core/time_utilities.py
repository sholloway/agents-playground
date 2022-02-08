from time import process_time

TimeInSecs = float
TimeInMS = float
MS_PER_SEC: int = 1000
TIME_PRECISION: int = 3
TARGET_FRAMES_PER_SEC: float = 60
TIME_PER_FRAME: TimeInMS = round(1/TARGET_FRAMES_PER_SEC * MS_PER_SEC, TIME_PRECISION)

# This is the budget (ms) for how much time can be spent performing updates in a 
# Single cycle.
UPDATE_BUDGET: TimeInMS = 10

class TimeUtilities:
  @staticmethod
  def now() -> TimeInMS:
    """Finds the current time in milliseconds."""
    return process_time() * MS_PER_SEC