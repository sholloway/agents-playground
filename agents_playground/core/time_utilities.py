from time import time as current_time_sec

TimeInMS = float
MS_PER_SEC: int = 1000
TIME_PRECISION: int = 3
TARGET_FRAMES_PER_SEC: float = 60
TIME_PER_FRAME: TimeInMS = round(1/TARGET_FRAMES_PER_SEC * 1000, TIME_PRECISION)
UPDATES_PER_FRAME_TARGET = 3
TIME_PER_UPDATE: TimeInMS = round(TIME_PER_FRAME/UPDATES_PER_FRAME_TARGET, 3)

class TimeUtilities:
  @staticmethod
  def now() -> TimeInMS:
    """Finds the current time in milliseconds."""
    return current_time_sec() * MS_PER_SEC