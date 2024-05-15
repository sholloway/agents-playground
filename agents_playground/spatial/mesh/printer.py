from abc import abstractmethod
from string import Template
from typing import Protocol

from agents_playground.spatial.mesh import UNSET_MESH_ID, MeshLike


class MeshPrinter(Protocol):
    @abstractmethod
    def print(self, mesh: MeshLike) -> None:
        """Represents the mesh to STDOUT."""


class MeshTablePrinter(MeshPrinter):
    def print(self, mesh: MeshLike) -> None:
        """
        Prints the mesh to STDOUT as a series of tables.
        """
        self._vertices_table(mesh)
        print("")
        self._faces_table(mesh)
        print("")
        self._edges_table(mesh)

    def _vertices_table(self, mesh: MeshLike) -> None:
        print("Vertices")
        table_format = "{:<10} {:<30} {:<10}"
        print(table_format.format("Vertex", "Coordinate", "Incident Edge"))
        for v in mesh.vertices:
            print(table_format.format(v.vertex_indicator, v.location.__repr__(), v.edge(mesh).edge_indicator))  # type: ignore

    def _faces_table(self, mesh: MeshLike) -> None:
        print("Faces")
        print("{:<10} {:<10}".format("Face", "Boundary Edge"))
        for f in mesh.faces:
            print("{:<10} {:<10}".format(f.face_id, f.boundary_edge(mesh).edge_indicator))  # type: ignore

    def _edges_table(self, mesh: MeshLike) -> None:
        print("Half-edges")
        table_format = "{:<10} {:<30} {:<10} {:<10} {:<10}"
        print(table_format.format("Half-edge", "Origin", "Face", "Next", "Previous"))
        for e in mesh.edges:
            next_edge_indicator = (
                e.next_edge(mesh).edge_indicator
                if e.next_edge_id != UNSET_MESH_ID
                else "None"
            )
            previous_edge_indicator = (
                e.previous_edge(mesh).edge_indicator
                if e.previous_edge_id != UNSET_MESH_ID
                else "None"
            )
            face_id = e.face(mesh).face_id if e.face_id != UNSET_MESH_ID else "None"
            print(table_format.format(e.edge_indicator, e.origin_vertex(mesh).location.__repr__(), face_id, next_edge_indicator, previous_edge_indicator))  # type: ignore


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
    def print(self, mesh: MeshLike) -> None:
        """
        Prints the mesh to STDOUT as a GraphViz digraph.

        Note: This prints the x,y coordinate.
        If dealing with a 3d mesh you've got to decide which plane (XY or XZ) to visualize.

        ### Example
        To use in a Use in a unit test, set the mesh up and then force pytest to print
        to STDOUT by making the test fail.

        ### Print
        viz = MeshGraphVizPrinter()
        viz.print(mesh)
        assert False
        """
        to_vert_loc = (
            lambda v: f'v{v.vertex_indicator}[pos="{v.location[0]},{v.location[2]}!"]'
        )
        vertices: list[str] = [to_vert_loc(v) for v in mesh.vertices]

        to_inner_half_edge = (
            lambda e: f'v{e.origin_vertex.vertex_indicator} -> v{e.pair_edge.origin_vertex.vertex_indicator} [label="1" color="green"]'
        )
        inner_half_edges: list[str] = [
            to_inner_half_edge(e) for e in mesh.edges if e.face_id is not None
        ]

        to_outer_half_edge = (
            lambda e: f'v{e.origin_vertex.vertex_indicator} -> v{e.pair_edge.origin_vertex.vertex_indicator} [label="1" color="red" style="dashed"]'
        )
        outer_half_edges: list[str] = [
            to_outer_half_edge(e) for e in mesh.edges if e.face_id is None
        ]

        data: dict[str, str] = {
            "vertices": "\n ".join(vertices),
            "inner_half_edges": "\n ".join(inner_half_edges),
            "outer_half_edges": "\n ".join(outer_half_edges),
        }
        graph_viz: str = Template(DIAGRAPH_TEMPLATE).substitute(data)
        print(graph_viz)
