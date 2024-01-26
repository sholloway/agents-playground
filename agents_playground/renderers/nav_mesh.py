from enum import Enum
from typing import Tuple
import dearpygui.dearpygui as dpg
from agents_playground.core.types import Size
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.renderers.color import BasicColors, Color, Colors
from agents_playground.simulation.context import SimulationContext
from agents_playground.spatial.direction import Direction
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector2d import Vector2d

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

def render_mesh(**data) -> None:
  logger.info('Renderer: render_mesh')
  context: SimulationContext = data['context']

  #render junctions
  for junction in context.scene.nav_mesh.junctions():
    # junction.render(context)
    draw_junction_node(junction, context)
  
    # Render mesh segments
    for junction_toml_id in junction.connects_to:
      destination_junction: Junction = context.scene.nav_mesh.get_junction_by_toml_id(junction_toml_id)
      draw_mesh_segment(junction, destination_junction, context)

JUNCTION_SIZE = 5
X=0
Y=1

JunctionColor = Tuple[int,int, int]
class JunctionColors(Enum):
  ENTRANCE = (0, 204, 0)
  EXIT = (0,0,204)
  NODE = (204,0,0)

def select_junction_color(junction: Junction) -> JunctionColor:
  color: JunctionColor
  match junction.toml_id:
    case entrance if entrance.endswith('entrance'):
      color = JunctionColors.ENTRANCE.value
    case exit if exit.endswith('exit'):
      color = JunctionColors.EXIT.value
    case _:
      color = JunctionColors.NODE.value
  return color
      

def draw_junction_node(junction: Junction, context: SimulationContext) -> None:
  cell_size: Size = context.scene.cell_size
  cell_center_x_offset:float = context.scene.cell_center_x_offset
  cell_center_y_offset:float = context.scene.cell_center_y_offset

  junction_color: JunctionColor = select_junction_color(junction)
  dpg.draw_circle(
    tag=junction.id,
    center = (
      junction.location[X] * cell_size.width + cell_center_x_offset, 
      junction.location[Y] * cell_size.height + cell_center_y_offset
    ), 
    radius=JUNCTION_SIZE,
    color=Colors.black.value, 
    fill = junction_color
  )

def draw_mesh_segment(start_junction: Junction, end_junction: Junction, context: SimulationContext) -> None:
  cell_size:Size = context.scene.cell_size
  cell_center_x_offset:float = context.scene.cell_center_x_offset
  cell_center_y_offset:float = context.scene.cell_center_y_offset

  start_point = Coordinate(
    start_junction.location[X] * cell_size.width + cell_center_x_offset, 
    start_junction.location[Y] * cell_size.height + cell_center_y_offset
  )

  end_point = Coordinate(
    end_junction.location[X] * cell_size.width + cell_center_x_offset, 
    end_junction.location[Y] * cell_size.height + cell_center_y_offset
  )

  # Calculate the line between the junction points.
  segment_vector: Vector = Vector2d.from_points(start_point, end_point)
  direction_v: Vector = segment_vector.unit()
  segment_start: Coordinate = direction_v.scale(JUNCTION_SIZE).to_point(start_point)
  segment_length: float = segment_vector.length() - (2 * JUNCTION_SIZE)
  segment_end: Coordinate = direction_v.scale(segment_length).to_point(segment_start)

  # Calculate the direction of the nav segment (N/S/E/W).
  segment_color: Color
  match direction_v:
    case Direction.NORTH:
      segment_color = BasicColors.blue.value
    case Direction.SOUTH:
      segment_color = BasicColors.yellow.value
    case Direction.EAST:
      segment_color = BasicColors.cyan.value
    case Direction.WEST:
      segment_color = BasicColors.red.value
    case _:
      segment_color = BasicColors.maroon.value

  dpg.draw_arrow(
    p1=segment_end, 
    p2=segment_start, 
    color=segment_color, 
    thickness=1,
    size=4 
  )