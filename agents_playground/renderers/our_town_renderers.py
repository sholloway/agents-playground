"""
Module that contains renderers for the Out Town simulation.
"""
from typing import List
import dearpygui.dearpygui as dpg
from agents_playground.agents.structures import Size

from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext


def building_renderer(self, context: SimulationContext) -> None:
  # Need to convert the building's width, height, and location values into pmin/pmax.
  # Location on a building is the upper left corner. DPG has the origin of [0,0]
  # at the upper left corner of the screen.

  with dpg.draw_node():  
    dpg.draw_rectangle(
      tag=self.id, 
      pmin=self.location,
      pmax=(self.location[0] + self.width, self.location[1] + self.height),
      color=self.color, 
      fill=self.fill
    )
    
    dpg.draw_text(
      pos = self.location, 
      text = self.title, 
      size=14,
      color = Colors.black
    )

PointPath = List[List[float]]
X:int = 0
Y:int = 1

def interstate_renderer(self, context: SimulationContext) -> None:
  # An interstate is 4 cells wide. The traffic is in lanes.
  # A lane is a cell width.
  # There are two lanes of traffic going in each direction.
  # The start/end is in cell coordinates and indicate the midline.
  cell_size:Size = context.scene.cell_size
  street_cells_wide:int = 4
  street_width:float = cell_size.width * street_cells_wide
  interstate_median_width = 2
  interstate_lane_median_width = 2

  # Draw the street base.
  draw_street_line(self.start, self.end, cell_size, 0,0, street_width, self.color)

  # # Draw the interstate median line
  draw_street_line(self.start, self.end, cell_size, 0, 0, interstate_median_width, Colors.goldenrod.value)

  # Draw the lane dividers (white lines, ideally stripped)
  south_median_starting_point = [self.start[X] - 1, self.start[Y]]
  south_median_ending_point = [self.end[X] - 1, self.end[Y]]
  draw_street_line(south_median_starting_point, south_median_ending_point, cell_size, 0, 0, interstate_lane_median_width, Colors.white.value)
  
  north_median_starting_point = [self.start[X] + 1, self.start[Y]]
  north_median_ending_point = [self.end[X] + 1, self.end[Y]]
  draw_street_line(north_median_starting_point, north_median_ending_point, cell_size, 0, 0, interstate_lane_median_width, Colors.white.value)

def draw_street_line(
  start_point, 
  end_point, 
  cell_size, 
  cell_center_x_offset, 
  cell_center_y_offset, 
  thickness,
  line_color
) -> None:
# Transform the path of cells into canvas coordinates.
  lane_start_point = [
    start_point[X] * cell_size.width + cell_center_x_offset, 
    start_point[Y] * cell_size.height + cell_center_y_offset
  ]

  lane_end_point = [
    end_point[X] * cell_size.width + cell_center_x_offset, 
    end_point[Y] * cell_size.height + cell_center_y_offset
  ]

  street_points: PointPath = [lane_start_point, lane_end_point]
  
  dpg.draw_polyline(
    points=street_points,
    closed=False,
    thickness=thickness,
    color=line_color
  )