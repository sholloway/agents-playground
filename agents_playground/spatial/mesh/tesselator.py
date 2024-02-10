from __future__ import annotations
from abc import abstractmethod
import math
from typing import Protocol

from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.mesh import MeshBuffer, MeshFaceLike, MeshLike, MeshVertexLike
from agents_playground.spatial.vector import vector_from_points
from agents_playground.spatial.vector.vector3d import Vector3d

"""
Steps:
1. Build up an internal data structure that represents the triangles.
  What Data Structure?
    - Winged-edge
      https://en.wikipedia.org/wiki/Winged_edge
    - Quad-edge
      https://en.wikipedia.org/wiki/Quad-edge
    - Half-edge/Doubly linked face list (DLFL)
      https://en.wikipedia.org/wiki/Doubly_connected_edge_list
      http://www.sccg.sk/%7Esamuelcik/dgs/half_edge.pdf
      Explanation Video: https://www.youtube.com/watch?v=w5KOFgfx0CA 
      Tutorial for EdgeFlip: https://jerryyin.info/geometry-processing-algorithms/half-edge/
      Rust Implementation: https://github.com/setzer22/blackjack/blob/main/blackjack_engine/src/mesh/halfedge.rs
      Hal-Edge Mesh Operations: https://docs.google.com/presentation/d/1U_uiZ3Jbc_ltHMhWBAvBDe4o0YKAAD3RNLXI3WwGmnE/edit#slide=id.g2704aba97d_0_201
      OpenMesh (C++): https://www.graphics.rwth-aachen.de/software/openmesh/intro/
      Implementation Tutorial: https://kaba.hilvi.org/homepage/blog/halfedge/halfedge.htm
      Paper: https://www.graphics.rwth-aachen.de/media/papers/directed.pdf

      A decent fit for path finding across triangles.
      This is promising, however, I need to represent, disconnected graphs.
      Let's try doing this with the half-edge data structure to get started.

  Consider different tesselation approaches.
    - Naïve
      Just split a tile into two triangles with no regard to the larger mesh.
    - Treat the landscape as an unstructured grid, and tesselate the grid as a whole.
      https://en.wikipedia.org/wiki/Unstructured_grid
      - Ruppert's algorithm
        https://en.wikipedia.org/wiki/Ruppert%27s_algorithm

2. Use this data structure to calculate the vertex normals.
  This is ultimately the problem I'm trying to solve. I need a data structure 
  that enables fast and easy traversal of the mesh to enable calculating the 
  normals of the connected faces per vertex.

  Additionally, the data structure selected for the internal traversal could 
  aid in future efforts to procedurally generate meshes, both landscape and otherwise.
3. Pack the vertex data and normal data while building an index.
4. Profit!
"""
class Tesselator(Protocol):
  """Given a spatial object, tesselates the object into triangles."""
  
  @abstractmethod
  def tesselate(self, mesh: MeshLike):
    """Tesselates a mesh in place.
    
    Args:
      - mesh: The mesh to tesselate.

    Returns:
    A new mesh composed entirely of triangles.
    """

class TesselationException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class FanTesselator(Tesselator):
  """
  Implements a simple fan tesselation scheme. 
  https://en.wikipedia.org/wiki/Fan_triangulation

  For each face, with N number of vertices, it picks the first 
  vertex and then breaks the face into triangles by creating a 
  fan with the first vertex as the fan origin.

  This is only appropriate for convex polygons and throws a TesselationException
  if the the polygon is not convex.
  """
  def tesselate(self, mesh: MeshLike):
    """Tesselates a mesh in place.
    
    Args:
      - mesh: The mesh to tesselate.

    Returns:
    A new mesh composed entirely of triangles.
    """
    face: MeshFaceLike
    for face in mesh.faces:
      # Is the face a triangle? If so, skip. Otherwise break into a fan.
      if face.count_boundary_edges() == 3:
        continue 
      
      vertices: list[MeshVertexLike] = face.vertices()

      # Can a fan be constructed? 
      # A fan can only be constructed on convex polygons.
      if not is_convex(vertices):
        raise TesselationException(f'A fan cannot be produced from the vertices:\n{vertices}')
      
      fan_point = vertices[0]

      mesh.remove_face(face)

      # Loop over the vertices in the range [1:N-1]
      # Skipping the first and last vertices.
      for current_vert_index in range(1, len(vertices) - 1):
        mesh.add_polygon([ 
          fan_point.location, 
          vertices[current_vert_index].location, 
          vertices[current_vert_index + 1].location
        ])

def is_convex(vertices: list[MeshVertexLike]) -> bool:
  """
  A convex polygon is a polygon that  has all its interior angles 
  less than 180 degrees. 

  To find the angle θ between two vectors u and v that intersect at their tails, 
  you can use the dot product formula:
  u • v = |u| * |v| * cos(θ)

  Rearrange the formula to solve for θ:
  θ = arc_cos((u • v) / (|u| * |v|))

  Additionally, the cross product can be used.
  | u X v | = |u|*|v|*sin(θ)
  θ = arc_sign [ |u X v| / (|u| |v|) ]

  We can use the sign of the... to determine the direction of the angle. If the 
  direction changes on any of the angles, then we know that polygon is not convex.
  """
  dim = vertices[0].location.dimensions()
  match dim:
    case 2:
      return is_2d_polygon_convex(vertices)
    case 3:
      return is_3d_polygon_convex(vertices)
    case _:
      raise TesselationException(f'Attempted to tesselate a polygon with a vertex with {dim} dimensions.')


def is_2d_polygon_convex(vertices: list[MeshVertexLike]) -> bool:
  num_verts = len(vertices)
  last_vert = num_verts - 1
  direction: float = 1.0
  current_direction: float = 1.0
  for current_vert in range(num_verts):
    previous_vert = last_vert if current_vert == 0 else current_vert - 1
    next_vert = (current_vert + 1) % num_verts 
    vert_a = vertices[previous_vert]
    vert_b = vertices[current_vert]
    vert_c = vertices[next_vert]
    vector_a = vector_from_points(vert_b.location, vert_a.location) # vert_b -> vert_a
    vector_b = vector_from_points(vert_b.location, vert_c.location) # vert_b -> vert_c
    det = vector_a.i*vector_b.j - vector_a.j*vector_b.i
    current_direction = math.copysign(1.0, det)
    if current_vert == 0:
      direction = math.copysign(1.0, det)
    elif current_direction != direction:
      return False
    
  return True 

def is_3d_polygon_convex(vertices: list[MeshVertexLike]) -> bool:
  return False
    



