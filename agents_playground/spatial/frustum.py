from __future__ import annotations

from abc import abstractmethod
from math import cos, tan, radians
from typing import Protocol, Tuple
from agents_playground.core.types import Size

from agents_playground.spatial.types import Coordinate, Degrees, Line2d
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vector2d import Vector2d

class Frustum(Protocol):
  """
  Represents a view frustum for an agent.
  """
  near_plane_depth: int
  depth_of_field: int 
  field_of_view: Degrees # In degrees

  # These are all in canvas space and are defined clockwise 
  p1: Coordinate # Near Plane
  p4: Coordinate # Near Plane
  p2: Coordinate # Far Plane
  p3: Coordinate # Far Plane

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
    near_plane_depth: int = 10,
    depth_of_field: int = 500, 
    field_of_view: Degrees = 120
  ) -> None:
    """
    Create a 2D frustum. 

    Args:
      - near_plane_depth: The distance from the camera to the near plane.
      - depth_of_field: The distance from the camera to the far plane.
      - field_of_view: The angle of vision. 
    """
    self.near_plane_depth = near_plane_depth
    self.depth_of_field   = depth_of_field
    self.field_of_view    = field_of_view


  @staticmethod
  def create_empty() -> Frustum2d:
    return Frustum2d()

  def update(self, grid_location: Coordinate, direction: Vector, cell_size: Size) -> None:
    """Recalculate the location of the frustum.
    
    Args:
      - location: Where the right and left sides intersect. 
        In a traditional View Frustum this is the location of the camera. 
      - direction: The direction vector of the frustum. From the location, where the frustum is pointing.
    """
    small_triangle = self._create_isosceles_triangle(
      angle     = self.field_of_view, 
      height    = self.near_plane_depth, 
      location  = grid_location, 
      direction = direction, 
      cell_size = cell_size
    )

    # Assign the near plane
    self.p1 = small_triangle[1]
    self.p4 = small_triangle[2]

    large_triangle = self._create_isosceles_triangle(
      angle     = self.field_of_view, 
      height    = self.depth_of_field, 
      location  = grid_location, 
      direction = direction, 
      cell_size = cell_size
    )

    # Assign the far plane
    self.p2 = large_triangle[1]
    self.p3 = large_triangle[2]

  def _create_isosceles_triangle(
    self, 
    angle: Degrees,
    height: int,
    location: Coordinate, 
    direction: Vector, 
    cell_size: Size
  ) -> Tuple[Coordinate, Coordinate, Coordinate]:
    """
    Create an Isosceles Triangle (t1, t2, t3) from the agent's location in canvas space
    that is facing the direction vector provided.

    Args:
      - angle: The angle in degrees between the two legs of the triangle.
      - height: The distance between t1 and the line formed by t2 and t3.
      - location: The grid cell location where t1 should be.
      - direction: The vector that the triangle will face towards.
    """
    cell_half_width  = cell_size.width  / 2.0
    cell_half_height = cell_size.height / 2.0
    # 1. Convert the agent's location from grid cells to canvas coordinates.
    canvas_loc: Coordinate = location.multiply(Coordinate(cell_size.width, cell_size.height))

    # 2. 
    #    Agent's are shifted to be drawn at the center of a grid cell, 
    #    the frustum's origin should be there as well.
    t1: Coordinate = canvas_loc.shift(Coordinate(cell_half_width, cell_half_height))

    # 3. Find the length of the two identical sides.
    theta = radians(angle/2.0)
    tri_side_length = height * tan(theta)

    # 4. rotate the direction vector by theta/-theta and project a point down it to 
    # find t2 and t3.
    dir_unit: Vector = direction.unit()
    t2: Coordinate = dir_unit.rotate(theta).scale(tri_side_length).to_point(t1)
    t3: Coordinate = dir_unit.rotate(-theta).scale(tri_side_length).to_point(t1)
    return (t1, t2, t3)
    

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



3. The near plane is created by defining a second 


"""

