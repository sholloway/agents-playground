"""
Module for working with the various coordinate systems.
"""

from agents_playground.core.types import CanvasLocation, CellLocation, Size

def canvas_to_cell(loc: CanvasLocation, cell: Size) -> CellLocation:
  """Find the cell coordinates that a pixel on the canvas is in."""
  return (int(loc[0]//cell.width), int(loc[1]//cell.height))