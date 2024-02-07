from abc import abstractmethod
from string import Template
from typing import Protocol
from agents_playground.spatial.mesh.tesselator import Mesh


class MeshPrinter(Protocol):
  @abstractmethod
  def print(self, mesh: Mesh) -> None:
    """Represents the mesh to STDOUT."""
  
class MeshTablePrinter(MeshPrinter):
  def print(self, mesh: Mesh) -> None:
    """
    Prints the mesh to STDOUT as a series of tables.
    """
    self._vertices_table(mesh)
    print('')
    self._faces_table(mesh)
    print('')
    self._edges_table(mesh)

  def _vertices_table(self, mesh: Mesh) -> None:
    print('Vertices')
    print('{:<10} {:<20} {:<10}'.format('Vertex', 'Coordinate', 'Incident Edge'))
    for k,v in mesh._vertices.items():
      print('{:<10} {:<20} {:<10}'.format(v.vertex_indicator, k.__repr__(), v.edge.edge_indicator )) #type: ignore

  def _faces_table(self, mesh: Mesh) -> None:
    print('Faces')
    print('{:<10} {:<10}'.format('Face', 'Boundary Edge'))
    for k, f in mesh._faces.items():
      print('{:<10} {:<10}'.format(k, f.boundary_edge.edge_indicator)) #type: ignore

  def _edges_table(self, mesh: Mesh) -> None:
    print('Half-edges')
    print('{:<10} {:<20} {:<10} {:<10} {:<10}'.format('Half-edge', 'Origin', 'Face', 'Next', 'Previous'))
    for e in mesh._half_edges.values():
      next_edge_indicator = e.next_edge.edge_indicator if e.next_edge is not None else 'None'
      previous_edge_indicator = e.previous_edge.edge_indicator if e.previous_edge is not None else 'None'
      face_id = e.face.face_id if e.face is not None else 'None'
      print('{:<10} {:<20} {:<10} {:<10} {:<10}'.format(e.edge_indicator, e.origin_vertex.location.__repr__(), face_id, next_edge_indicator, previous_edge_indicator)) #type: ignore

DIAGRAPH_TEMPLATE = """
digraph{
 # Note: Absolute positioning only works with neato and fdp
 # The online editor https://edotor.net/ can be used to render this graph.
 # Set Node defaults
 node [shape=circle]
 
 # Vertex Positions
 ${vertices}
 
 # Half-Edges
 ${inner_half_edges}
 ${outer_half_edges}
}
"""

class MeshGraphVizPrinter(MeshPrinter):
  def print(self, mesh: Mesh) -> None:
    """
    Prints the mesh to STDOUT as a GraphViz digraph.
    
    Note: This prints the x,y coordinate. 
    If dealing with a 3d mesh you've got to decide which plane (XY or XZ) to visualize.

    Example
    To use in a Use in a unit test, set the mesh up and then force pytest to print 
    to STDOUT by making the test fail. 
    # Set the mesh up...

    # Print
    viz = MeshGraphVizPrinter()
    viz.print(mesh)
    assert False
    """
    to_vert_loc = lambda v: f'v{v.vertex_indicator}[pos="{v.location[0]},{v.location[1]}!"]'
    vertices: list[str] = [ to_vert_loc(v) for v in mesh._vertices.values() ]

    to_inner_half_edge = lambda e: f'v{e.origin_vertex.vertex_indicator} -> v{e.pair_edge.origin_vertex.vertex_indicator} [label="1" color="green"]'
    inner_half_edges: list[str] = [ to_inner_half_edge(e) for e in mesh._half_edges.values() if e.face is not None]
    
    to_outer_half_edge = lambda e: f'v{e.origin_vertex.vertex_indicator} -> v{e.pair_edge.origin_vertex.vertex_indicator} [label="1" color="red" style="dashed"]'
    outer_half_edges: list[str] = [ to_outer_half_edge(e) for e in mesh._half_edges.values() if e.face is None]

    data: dict[str, str] = {
      'vertices': '\n '.join(vertices),
      'inner_half_edges': '\n '.join(inner_half_edges),
      'outer_half_edges': '\n '.join(outer_half_edges),
    }
    graph_viz: str = Template(DIAGRAPH_TEMPLATE).substitute(data)
    print(graph_viz)