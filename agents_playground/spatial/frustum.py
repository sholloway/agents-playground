from __future__ import annotations

from abc import abstractmethod
from math import cos, tan, radians
from typing import Protocol
from agents_playground.core.types import Size

from agents_playground.spatial.types import Coordinate, Degrees, Line2d
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector2d import Vector2d

class Frustum(Protocol):
  """
  Represents a view frustum for an agent.
  """
  depth_of_field: int 
  field_of_view: Degrees # In degrees
  t1: Coordinate
  t2: Coordinate
  t3: Coordinate

  @abstractmethod
  def update(self, grid_location: Coordinate, direction: Vector, cell_size: Size) -> None:
    """Recalculate the location of the frustum."""
    ...  

class Frustum2d(Frustum):
  """
  A 2D frustum is just an Isosceles trapezoid. 
  https://en.wikipedia.org/wiki/Isosceles_trapezoid

  The depth of the frustum is the height of the 2D trapezoid.

  The trapezoid is defined by the four sides:
  - near
  - far
  - right
  - left

  Where sides near and far are parallel and right and left intersect at point p.
  The distance between the near and far sides is the depth_of_field.

  The field of view is the angle between the left and right side. 
  
  The location of Frustum is where the right and left sides intersect. 
  In a traditional View Frustum this is location of the camera. 
  It is intended to map an agent's location.

  """

  def __init__(
    self, 
    depth_of_field: int = 500, 
    field_of_view: Degrees = 120
  ) -> None:
    """
    Create a 2D frustum. 

    Args:
      - location: Where the right and left sides intersect. 
        In a traditional View Frustum this is location of the camera. 
      - direction: The direction vector of the frustum. From the location, where the frustum is pointing.

      - depth_of_field
      - field_of_view
    """
    self.depth_of_field = depth_of_field
    self.field_of_view = field_of_view

    # TODO: I may not need to declare these here to make the type checker happy.
    self.near_plane:Line2d
    self.far_plane:Line2d
    self.left_plane: Line2d
    self.right_plane: Line2d

  @staticmethod
  def create_empty() -> Frustum2d:
    return Frustum2d()

  def update(self, grid_location: Coordinate, direction: Vector, cell_size: Size) -> None:
    """Recalculate the location of the frustum."""
    # print(f"grid loc: {grid_location}, direction: {direction}, cell_size: {cell_size}")

    cell_half_width         = cell_size.width  / 2.0
    cell_half_height        = cell_size.height / 2.0

    # 1. Convert the agent's location from grid cells to canvas coordinates.
    canvas_loc: Coordinate = grid_location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. Agent's are shifted to be drawn at the center of a grid cell, 
    #    the frustum's origin should be there as well.
    canvas_loc = canvas_loc.shift(Coordinate(cell_half_width, cell_half_height))


    # 3. Create an Isosceles Triangle (t1, t2, t3) from the agent's location in canvas space
    #    that is facing the direction vector provided.
    self.t1: Coordinate = canvas_loc

    # find the length of the two identical sides.
    theta = radians(self.field_of_view/2.0)
    tri_side_length = self.depth_of_field * tan(theta)

    # rotate the direction vector by theta/-theta and project a point down it to 
    # find t2 and t3.
    dir_unit: Vector = direction.unit()
    t2_vector: Vector = dir_unit.rotate(theta)
    t3_vector: Vector = dir_unit.rotate(-theta)

    self.t2: Coordinate = t2_vector.scale(tri_side_length).to_point(self.t1)
    self.t3: Coordinate = t3_vector.scale(tri_side_length).to_point(self.t1)
    # print(f'Updated Frustum(t1={self.t1}, t2={self.t2}, t3={self.t3})')


"""
How to generate an Isosceles Trapezoid from depth_of_field and field_of_view?

1. Create an Isosceles triangle. 
  The triangle's three points are t1, t2, t3.
  Point t1 is at that centroid of the agent. Rather this is the center of a cell.
  Points t2 and t3 are perpendicular to the Agent's facing vector.
  The angle between t1t2 and t1t3 is field_of_view
  The triangle's length is the depth_of_field

  t2 is counter clockwise to t1.
  t3 is clockwise to t1

  
2. Points t2 and t3 form the far_plane of the Isosceles Trapezoid
If we divide the Isosceles triangle in half using the direction we get a right triangle
of sides a, b, c.
We can use the Right Triangle Laws to find sides a and c.
https://en.wikipedia.org/wiki/Triangle#Computing_the_sides_and_angles

Side b is the depth of field.
side a = depth_of_field * tan(fov/2)
side c = depth_of_field/cos(fov/2)



3. The near plane is created by...


"""

