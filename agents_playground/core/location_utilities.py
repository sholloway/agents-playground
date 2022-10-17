"""
Module for working with the various coordinate systems.
"""

from agents_playground.core.types import CanvasLocation, CellLocation, Coordinate, Size

def canvas_to_cell(loc: CanvasLocation, cell: Size) -> CellLocation:
  """Find the cell coordinates that a pixel on the canvas is in."""
  return (int(loc[0]//cell.width), int(loc[1]//cell.height))

def location_to_cell(loc: Coordinate) -> CellLocation:
  """Find the cell coordinates that an agent is in. 
  Agent's are already in the grid coordinate space, but they're in floating point.
  """
  return (int(loc.x), int(loc.y))