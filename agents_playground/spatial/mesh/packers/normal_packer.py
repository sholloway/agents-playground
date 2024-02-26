from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.mesh import MeshBuffer, MeshLike, MeshPacker, MeshVertexLike
from agents_playground.spatial.mesh.buffers.line_buffer import VertexBuffer
from agents_playground.spatial.mesh.half_edge_mesh import MeshException
from agents_playground.spatial.vector.vector import Vector

class NormalPacker(MeshPacker):
  """
  Given a half-edge mesh, backs a mesh buffer with a series of vertices to enable
  creating lines to visualize the normals. 
  """

  def pack(self, mesh: MeshLike) -> MeshBuffer:
    """
    For each vertex in a mesh, pack two vertices. 
    1. The original vertex (V).
    2. A new vertex (Q) that is along the vertex normal vector.

    The packed stride is:
    Vx, Vy, Vz
    """
    distance = 0.5 # The distance Q is from V.
    buffer = VertexBuffer()

    vertex: MeshVertexLike
    for vertex in mesh.vertices:
      if vertex.normal is None:
        msg = f"""
          Attempted to pack a vertex normal on a vertex that has no normal.
          The vertex in question is {vertex.location}.

          Be sure to call calculate_face_normals() and then calculate_vertex_normals()
          on a mesh before attempting to pack it into a MeshBuffer.
        """
        raise MeshException(msg)
      
      normal_offset: Vector = vertex.normal.unit().scale(distance)
      loc: Coordinate = vertex.location[0:3] 
      q: Coordinate = loc.add(Coordinate(*normal_offset.to_tuple()[0:3]))
      print('Packing')
      print(f'Vertex Normal: {vertex.normal.unit()}')
      print(f'normal_offset: {normal_offset}')
      print(f'loc: {loc}')
      print(f'q: {q}')
      buffer.pack(loc)
      buffer.pack(q)
    
    return buffer