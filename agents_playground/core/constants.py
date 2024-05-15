from agents_playground.core.types import Count, TimeInMS

# UI Related
DEFAULT_FONT_SIZE = 14

BYTES_IN_MB = 1048576

MS_PER_SEC: int = 1000
SECS_PER_MINUTE: int = 60
SECS_PER_HOUR: int = 60 * 60
SECS_PER_DAY: int = SECS_PER_HOUR * 24

TIME_PRECISION: int = 3
TARGET_FRAMES_PER_SEC: float = 60
TIME_PER_FRAME: TimeInMS = round(1 / TARGET_FRAMES_PER_SEC * MS_PER_SEC, TIME_PRECISION)

# This is the budget (ms) for how much time can be spent performing updates in a
# Single cycle.
UPDATE_BUDGET: TimeInMS = 10

# Performance Related
UTILITY_UTILIZATION_WINDOW: Count = 10
HARDWARE_SAMPLING_WINDOW: Count = 120
FRAME_SAMPLING_SERIES_LENGTH: Count = 120
