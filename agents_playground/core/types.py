"""
Module for defining types used by the core classes.
"""

# Time based Types
from typing import List, Tuple


TimeInSecs = float
TimeInMS = float

# Units of Measure
MegaBytes = float
Percentage = float
Count = int

# Performance Related
Sample = int | float

# Coordinates
# Note the definition of DrawingLocation is driven by DPGs annoying 
# habit of inconsistent return types.
CanvasLocation = List[int] | Tuple[int, ...]