import dearpygui.dearpygui as dpg
from agents_playground.agents.direction import Vector2D
from agents_playground.agents.structures import Point, Size
from agents_playground.renderers.color import Colors
from agents_playground.simulation.context import SimulationContext

from agents_playground.sys.logger import get_default_logger
logger = get_default_logger()

def render_mesh(**data) -> None:
  logger.info('Renderer: render_mesh')
  context: SimulationContext = data['context']

  #render junctions
  for junction in context.scene.nav_mesh.junctions():
    junction.render(context)
  
  for segment in context.scene.nav_mesh.segments():
    segment.render(context)

JUNCTION_SIZE = 5
X=0
Y=1

def draw_junction_node(self, context: SimulationContext) -> None:
  cell_size:Size = context.scene.cell_size
  cell_center_x_offset:float = context.scene.cell_center_x_offset
  cell_center_y_offset:float = context.scene.cell_center_y_offset
  dpg.draw_circle(
    center = (
      self.location[X] * cell_size.width + cell_center_x_offset, 
      self.location[Y]* cell_size.height + cell_center_y_offset
    ), 
    radius=JUNCTION_SIZE,
    color=Colors.black.value, 
    fill = self.fill
  )

def draw_nav_mesh_segment(self, context: SimulationContext) -> None:
  """ Renders line segments of the navigation mesh.

  Given the navigation mesh is structured as an adjacency list,
  a single mesh segment is of the form { start, targets=[t1, t2, t3, ...]}.

  Each segment of start -> tX is rendered as a line that is offset by 
  the size of junction nodes. This is to help with visual debugging.

  An arrow is on the end.
  """
  cell_size:Size = context.scene.cell_size
  cell_center_x_offset:float = context.scene.cell_center_x_offset
  cell_center_y_offset:float = context.scene.cell_center_y_offset
  start_junction = context.scene.nav_mesh.get_junction(self.junction)

  start_point = Point(
    start_junction.location[X] * cell_size.width + cell_center_x_offset, 
    start_junction.location[Y] * cell_size.height + cell_center_y_offset
  )

  for end_junction_id in self.maps_to:
    end_junction = context.scene.nav_mesh.get_junction(end_junction_id)
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
      color=self.color, 
      thickness=1,
      size=4 
    )