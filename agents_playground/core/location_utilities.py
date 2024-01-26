"""
Module for working with the various coordinate systems.
"""

from agents_playground.core.types import CanvasLocation, CellLocation, Size
from agents_playground.spatial.coordinate import Coordinate

def canvas_to_cell(loc: CanvasLocation, cell: Size) -> CellLocation:
  """Find the cell coordinates that a pixel on the canvas is in."""
  return (int(loc[0]//cell.width), int(loc[1]//cell.height))

def location_to_cell(loc: Coordinate) -> CellLocation:
  """Find the cell coordinates that an agent is in. 
  Agent's are already in the grid coordinate space, but they're in floating point.
  """
  return (int(loc.x), int(loc.y))

def cell_to_canvas(loc: Coordinate, cell: Size) -> Coordinate:
  """Converts from the grid's coordinate space to the canvas' coordinate space."""
  return Coordinate(loc.x * cell.width, loc.y * cell.height)

def canvas_location_to_coord(loc: CanvasLocation) -> Coordinate:
  """Converts a CanvasLocation to a Coordinate."""
  return Coordinate(loc[0], loc[1])