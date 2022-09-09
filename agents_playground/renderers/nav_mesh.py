from enum import Enum
from typing import Tuple
import dearpygui.dearpygui as dpg
from agents_playground.agents.direction import Vector2D
from agents_playground.agents.structures import Point, Size
from agents_playground.navigation.navigation_mesh import Junction
from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext

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
  cell_size:Size = context.scene.cell_size
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

  start_point = Point(
    start_junction.location[X] * cell_size.width + cell_center_x_offset, 
    start_junction.location[Y] * cell_size.height + cell_center_y_offset
  )

  end_point = Point(
    end_junction.location[X] * cell_size.width + cell_center_x_offset, 
    end_junction.location[Y] * cell_size.height + cell_center_y_offset
  )

  # Calculate the line between the junction points.
  segment_vector: Vector2D = Vector2D.from_points(start_point, end_point)
  direction_v: Vector2D = segment_vector.unit()
  segment_start: Point = direction_v.scale(JUNCTION_SIZE).to_point(start_point)
  segment_length: float = segment_vector.length() - (2 * JUNCTION_SIZE)
  segment_end: Point = direction_v.scale(segment_length).to_point(segment_start)

  dpg.draw_arrow(
    p1=segment_end, 
    p2=segment_start, 
    color=(204,0,0), 
    thickness=1,
    size=4 
  )