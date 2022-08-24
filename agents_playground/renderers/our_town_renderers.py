"""
Module that contains renderers for the Out Town simulation.
"""
from enum import Enum
from typing import List, Tuple
import dearpygui.dearpygui as dpg
from agents_playground.agents.structures import Size

from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext

PointInPixels = Tuple[int,int]
PointPath = List[List[float]]
X:int = 0
Y:int = 1

class StreetOrientation(Enum):
  NORTH_SOUTH:int = 1
  EAST_WEST:int = 2

def building_renderer(self, context: SimulationContext) -> None:
  # Need to convert the building's width, height, and location values into pmin/pmax.
  # Location on a building is the upper left corner. DPG has the origin of [0,0]
  # at the upper left corner of the screen.
  cell_size:Size = context.scene.cell_size
  min_point: PointInPixels = (
    self.location[X] * cell_size.width, 
    self.location[Y]*cell_size.height
  )
  
  max_point: PointInPixels = (
    self.location[X] * cell_size.width + self.width * cell_size.height, 
    self.location[Y] * cell_size.height + self.height * cell_size.height
  )
  
  with dpg.draw_node():  
    dpg.draw_rectangle(
      tag=self.id, 
      pmin=min_point,
      pmax=max_point,
      color=self.color, 
      fill=self.fill
    )
    
    dpg.draw_text(
      pos = min_point,
      text = self.title, 
      size=14,
      color = Colors.black
    )

def interstate_renderer(self, context: SimulationContext) -> None:
  # Determine if the street is running N/S or E/W.
  street_type = StreetOrientation.NORTH_SOUTH if self.start[X] == self.end[X] else StreetOrientation.EAST_WEST

  # The start/end is in cell coordinates and indicate the midline.
  cell_size:Size = context.scene.cell_size
  street_width:float = cell_size.width * self.lanes
  interstate_median_width = 2
  interstate_lane_median_width = 2

  # Draw the street base.
  draw_street_line(self.start, self.end, cell_size, 0,0, street_width, self.color)

  # Only the interstate has more than 2 lanes.
  
  # Draw the interstate median line
  draw_street_line(self.start, self.end, cell_size, 0, 0, interstate_median_width, Colors.goldenrod.value)

  # Draw the lane dividers (white lines, ideally stripped)
  if street_type == StreetOrientation.NORTH_SOUTH:
    south_median_starting_point = [self.start[X] - 1, self.start[Y]]
    south_median_ending_point = [self.end[X] - 1, self.end[Y]]
    north_median_starting_point = [self.start[X] + 1, self.start[Y]]
    north_median_ending_point = [self.end[X] + 1, self.end[Y]]
  else:
    south_median_starting_point = [self.start[X], self.start[Y] - 1]
    south_median_ending_point = [self.end[X], self.end[Y] - 1]
    north_median_starting_point = [self.start[X], self.start[Y] + 1]
    north_median_ending_point = [self.end[X], self.end[Y] + 1]

  draw_street_line(south_median_starting_point, south_median_ending_point, cell_size, 0, 0, interstate_lane_median_width, Colors.white.value)
  draw_street_line(north_median_starting_point, north_median_ending_point, cell_size, 0, 0, interstate_lane_median_width, Colors.white.value)

def street_renderer(self, context: SimulationContext) -> None:
  # Determine if the street is running N/S or E/W.
  street_type = StreetOrientation.NORTH_SOUTH if self.start[X] == self.end[X] else StreetOrientation.EAST_WEST

  # The start/end is in cell coordinates and indicate the midline.
  cell_size:Size = context.scene.cell_size
  street_width:float = cell_size.width * self.lanes
  lane_median_width = 2

  # Draw the street base.
  draw_street_line(self.start, self.end, cell_size, 0,0, street_width, self.color)

  # Draw the interstate median line
  draw_street_line(self.start, self.end, cell_size, 0, 0, lane_median_width, Colors.white.value)

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

def draw_junction_node(self, context: SimulationContext) -> None:
  cell_size:Size = context.scene.cell_size
  cell_center_x_offset:float = context.scene.cell_center_x_offset
  cell_center_y_offset:float = context.scene.cell_center_y_offset
  dpg.draw_circle(
    center = (
      self.location[X] * cell_size.width + cell_center_x_offset, 
      self.location[Y]* cell_size.height + cell_center_y_offset
    ), 
    radius=5,
    color=Colors.black.value, 
    fill = Colors.royalblue.value
  )

def draw_nav_mesh_segment(self, context: SimulationContext) -> None:
  cell_size:Size = context.scene.cell_size
  cell_center_x_offset:float = context.scene.cell_center_x_offset
  cell_center_y_offset:float = context.scene.cell_center_y_offset

  start_junction = context.scene.entities['junctions'][self.junction]
  start_point = (
    start_junction.location[X] * cell_size.width + cell_center_x_offset, 
    start_junction.location[Y]* cell_size.height + cell_center_y_offset
  )

  for end_junction_id in self.maps_to:
    end_junction = context.scene.entities['junctions'][end_junction_id]
    end_point = (
      end_junction.location[X] * cell_size.width + cell_center_x_offset, 
      end_junction.location[Y]* cell_size.height + cell_center_y_offset
    )
    dpg.draw_line(
      p1=start_point, 
      p2=end_point, 
      color=Colors.blue.value, 
      thickness=1
    )