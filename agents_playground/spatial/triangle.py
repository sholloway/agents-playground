
from math import radians, tan
from typing import List, Protocol
from agents_playground.spatial.polygon import Polygon
from agents_playground.spatial.polygon2d import Polygon2d
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector import Vector
from agents_playground.spatial.vertex import Vertex


class Triangle(Polygon, Protocol):
  """
  The base definition of a triangle in canvas space. 
  """
  vertices: List[Vertex]

class Triangle2d(Polygon2d, Triangle):
  def __init__(self, t1: Vertex, t2: Vertex, t3: Vertex) -> None:
    self.vertices = [t1, t2, t3]

  @staticmethod
  def create_isosceles_triangle(
    angle: Degrees,
    height: int,
    location: Vertex, 
    direction: Vector
  ) -> Triangle:
    """
    Create an Isosceles Triangle (t1, t2, t3) from a location in canvas space
    that is facing the direction vector provided.

    Args:
      - angle: The angle in degrees between the two legs of the triangle.
      - height: The distance between t1 and the line formed by t2 and t3.
      - location: The location where t1 should be.
      - direction: The vector that the triangle will face towards.
    """

    # Find the length of the two identical sides.
    # This is done using the Right Triangle Laws
    # https://en.wikipedia.org/wiki/Triangle#Computing_the_sides_and_angles
    # The hypotenuse = depth_of_field * tan(fov/2)
    theta = radians(angle/2.0)
    tri_side_length = height * tan(theta)

    # rotate the direction vector by theta/-theta and project a point down it to 
    # find t2 and t3.
    dir_unit: Vector = direction.unit()
    t2: Vertex = dir_unit.rotate(theta).scale(tri_side_length).to_vertex(location)
    t3: Vertex = dir_unit.rotate(-theta).scale(tri_side_length).to_vertex(location)
    return Triangle2d(location, t2, t3)