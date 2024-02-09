from __future__ import annotations
from abc import abstractmethod
from typing import Protocol


from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.mesh import MeshBuffer, MeshLike

class Tesselator(Protocol):
  """Given a spatial object, tesselates the object into triangles."""
  
  @abstractmethod
  def tesselate(self, mesh: MeshLike) -> MeshLike:
    """Given a mesh, create a new tesselate mesh.
    
    Args:
      - mesh: The mesh to tesselate.

    Returns:
    A new mesh composed entirely of triangles.
    """
    
  def from_landscape(landscape: Landscape) -> MeshBuffer:
    """
    Tesselates a landscape object into triangles.
    The triangles are returned in the same coordinate space that the landscape is in.

    Args:
      - landscape: The landscape to convert into triangles.

    Returns:
    A a mesh containing the Vertex Buffer with Vertex Normals, and index buffer.
    """
  
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
    return None  # type: ignore



