from __future__ import annotations

from abc import abstractmethod
from math import cos, tan, radians
from typing import List, Protocol, Tuple, cast
from agents_playground.core.types import Size
from agents_playground.spatial.polygon.polygon import Polygon
from agents_playground.spatial.polygon.polygon2d import Polygon2d
from agents_playground.spatial.polygon.polygon3d import Polygon3d
from agents_playground.spatial.triangle import Triangle2d

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector2d import Vector2d
from agents_playground.spatial.vertex import Vertex, Vertex2d


class Frustum(Polygon, Protocol):
    """
    Represents a view frustum for an agent.
    """

    near_plane_depth: int
    depth_of_field: int
    field_of_view: Degrees
    vertices: List[Vertex]  # Used to draw the frustum in .

    @abstractmethod
    def update(
        self, grid_location: Coordinate, direction: Vector, cell_size: Size
    ) -> None:
        """Recalculate the location of the frustum."""


class Frustum2d(Frustum, Polygon2d):
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
    It is intended to map to an agent's location.

    The frustum is created by generating two overlapping Isosceles triangles.
    """

    def __init__(
        self,
        near_plane_depth: int = 10,
        depth_of_field: int = 500,
        field_of_view: Degrees = 120,
    ) -> None:
        """
        Create a 2D frustum.

        Args:
          - near_plane_depth: The distance from the camera to the near plane.
          - depth_of_field: The distance from the camera to the far plane.
          - field_of_view: The angle of vision.


        P4               P3
        -----------------
        \\               /
          \\            /
            -----------
            P0         P1

        The near plane is P0 -> P1
        The far plane is P3 -> P4
        """
        self.near_plane_depth = near_plane_depth
        self.depth_of_field = depth_of_field
        self.field_of_view = field_of_view
        self.vertices: List[Vertex] = []

    @staticmethod
    def create_empty() -> Frustum2d:
        return Frustum2d()

    def update(
        self, grid_location: Coordinate, direction: Vector, cell_size: Size
    ) -> None:
        """Recalculate the location of the frustum.

        Args:
          - location: Where the right and left sides intersect.
            In a traditional View Frustum this is the location of the camera.
          - direction: The direction vector of the frustum. From the location, where the frustum is pointing.
        """
        cell_half_width = cell_size.width / 2.0
        cell_half_height = cell_size.height / 2.0

        # Convert the agent's location from grid cells to canvas coordinates.
        canvas_loc: Coordinate[float] = grid_location.multiply(
            Coordinate(cell_size.width, cell_size.height)
        )

        # Agent's are shifted to be drawn at the center of a grid cell,
        # the frustum's origin should be there as well.
        agent_loc: Coordinate[float] = canvas_loc.shift(
            Coordinate(cell_half_width, cell_half_height)
        )
        triangle_loc = Vertex2d(
            x=cast(float, agent_loc[0]), y=cast(float, agent_loc[1])
        )
        small_triangle = Triangle2d.create_isosceles_triangle(
            angle=self.field_of_view,
            height=self.near_plane_depth,
            location=triangle_loc,
            direction=direction,
        )

        large_triangle = Triangle2d.create_isosceles_triangle(
            angle=self.field_of_view,
            height=self.depth_of_field,
            location=triangle_loc,
            direction=direction,
        )

        self.vertices = [
            # Near Plane
            small_triangle.vertices[2],  # P0
            small_triangle.vertices[1],  # P1
            # Far Plane
            large_triangle.vertices[1],  # P3
            large_triangle.vertices[2],  # P4
        ]


class Frustum3d(Frustum, Polygon3d):
    def __init__(
        self,
        near_plane_depth: int = 10,
        depth_of_field: int = 500,
        field_of_view: Degrees = 120,
    ) -> None:
        self.near_plane_depth = near_plane_depth
        self.depth_of_field = depth_of_field
        self.field_of_view = field_of_view
        self.vertices: List[Vertex] = []

    def update(
        self, grid_location: Coordinate, direction: Vector, cell_size: Size
    ) -> None:
        """Recalculate the location of the frustum."""
        raise NotImplementedError()


"""
There are a few intersection tests that are going to be required.
1. An agent's view frustum (convex polygon) and other Agent's AABB.
2. An agent's view frustum and entities' AABB.
3. Collision between agents (AABB vs AABB).
4. Collision between agent and entities. (AABB and AABB)
5. Ray vs AABB

These use case can be simplified down to:
1. AABB vs AABB
2. Convex Polygon vs AABB
"""

"""
Use Case: AABB vs AABB
This one is simple in 2D. From Real-Time Rendering 3rd Edition by Akenine-Mooler, Haines, Hoffman

def does_intersect(a: aabb, b: aabb) -> bool:
  # Check the X-axis
  if (a.min.x > b.max.x or b.min.x > a.max.x):
    return false

  # Check the Y-axis
  if (a.min.y > b.max.y or b.min.y > a.max.y):
    return false

  return true
"""

"""
Use Case Convex Polygon vs AABB

Approach: Leverage the Separating Axis Test.
Technique: Projection
The basic idea is to move the objects out of penetration using the smallest 
possible displacement. Solving the collision then becomes equivalent to finding 
the vector v which moves the two objects out of penetration by the shortest 
distance possible.

Technique: Separating Axis Test (SAT)
Resource: Eberly, David. Intersection of Convex Objects: The Method of Separating Axes.
https://www.geometrictools.com/Documentation/MethodOfSeparatingAxes.pdf
Resource: http://www.metanetsoftware.com/technique/tutorialA.html

The separating axis theorem tells us that, given two convex shapes, if we can 
find an axis along which the projection of the two shapes does not overlap, then
the shapes don't overlap.

In 2D, each of these potential separating axes is perpendicular to one of the 
faces (edges) of each shape.

So in general, the 2D overlap query is solved using using a series of 1D queries.
Each query tests if the two shapes overlap along a given axis. 
If we find an axis along which the objects don't overlap, we don't have to 
continue testing the rest of the axes: thanks to the SAT we know that the objects 
don't overlap.

The SAT can be applied for concave polygons of arbitrary size so it can be made to 
work with Polygon/triangle, Polygon AABB, for example.

If the objects overlap along all of the possible separating axes, then they are 
definitely overlapping each other. That means there is a collision. In this 
case we need to determine the projection vector which will push the two objects apart.

At this point, most of the work is done. Each axis is a potential direction along
which we can project the objects. So, all we need to do is find the axis with 
the smallest amount of overlap between the two objects, and we're done.
The direction of the projection vector is the same as the axis direction, and 
the length of the projection vector is equal to the size of the overlap along that axis.

This is summarized as:
For a pair of objects: 
1. Test each potential separating axis, stopping if we find separation. 
2. If none of the axes are separating, find the axis of the smallest overlap.
3. Use the axis of the smallest overlap to generate a projection vector.
"""

"""
Use Case: Ray vs AABB
"""
