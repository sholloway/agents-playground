"""
Module for defining types used by the core classes.
"""
from __future__ import annotations
from dataclasses import dataclass

from typing import List, NamedTuple, Tuple

# Time based Types
TimeInSecs = float
TimeInMS = float

# Units of Measure
MegaBytes = float
Percentage = float
Count = int

# Performance Related
Sample = int | float

# Coordinates
# Note the definition of CanvasLocation is driven by DPGs annoying 
# habit of inconsistent return types.
CanvasLocation = List[int] | Tuple[int, ...]
CellLocation = Tuple[int, int]

# Handling Size
Dimension = int | float

@dataclass(init=False)
class Size:
  width: Dimension
  height: Dimension

  def __init__(self, w: Dimension = -1, h: Dimension = -1) -> None:
    self.width = w
    self.height = h

  def scale(self, amount: float) -> Size:
    return Size(self.width * amount, self.height * amount)