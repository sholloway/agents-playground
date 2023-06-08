

from abc import abstractmethod
from typing import Protocol

from agents_playground.spatial.types import Coordinate, Degrees, Line2d
from agents_playground.spatial.vector import Vector

class Frustum(Protocol):
  """
  Represents a view frustum for an agent.
  """
  depth_of_field: int 
  field_of_view: Degrees # In degrees
  location: Coordinate
  direction: Vector

  @abstractmethod
  def update(self, location: Coordinate, direction: Vector) -> None:
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
    location: Coordinate, 
    direction: Vector, 
    depth_of_field: int = 200, 
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
    self.location: Coordinate
    self.direction: Vector
    self.near_plane:Line2d
    self.far_plane:Line2d
    self.left_plane: Line2d
    self.right_plane: Line2d
    
    self.update(location, direction)

  def update(self, location: Coordinate, direction: Vector) -> None:
    """Recalculate the location of the frustum."""
    self.location = location
    self.direction = direction 

    # TODO Using the fov, location, and direction, calculate the 4 sides.


"""
How to generate an Isosceles Trapezoid from depth_of_field and field_of_view?

1. Create an Isosceles triangle. 
  The triangle's three points are t1, t2, t3.
  Point t1 is at that centroid of the agent. Rather this is the center of a cell.
  Points t2 and t3 are perpendicular to the Agent's facing vector.
  The angle between t1t2 and t1t3 is field_of_view
  The triangle's length is the depth_of_field

  


2. Points t2 and t3 form the far_plane of the Isosceles Trapezoid

3. The near plane is created by...


"""

