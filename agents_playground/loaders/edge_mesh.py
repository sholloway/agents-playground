from __future__ import annotations

from agents_playground.loaders.obj_loader import Obj

class EdgeMesh:
  """
  Groups the various lists that must be created to load a mesh of edges
  into GPUBuffer instances.
  """
  def __init__(self) -> None:
    self.vertices: list[float] = []  
    self.index: list[int] = []
    self.vertex_normals: list[float] = []  

  @staticmethod
  def from_obj(obj: Obj) -> EdgeMesh:
    edge_mesh = EdgeMesh()
    edge_count = 0

    # Each polygon is either a single triangle (3 verts) or a fan (>3 verts) of triangles.
    # For a triangle T, with vertices v1, v2, v3 edges are defined as
    # v1 -> v2
    # v2 -> v3
    # v3 -> v1
    for polygon in obj.polygons:
      # Use the first vertex as the point of the fan.
      v1_vertex_map = polygon.vertices[0]
      v1 = obj.vertices[v1_vertex_map.vertex - 1]

      v1_normal_index = v1_vertex_map.normal
      if v1_normal_index is None:
        # TODO: If there isn't a normal, calculate it.
        raise NotImplementedError('Obj files without vertex normals is currently not supported.')
      v1_normal = obj.vertex_normals[v1_normal_index - 1]

      for index in range(1, len(polygon.vertices) - 1):
        # Build triangles using the fan point and the other vertices.
        v2_index = polygon.vertices[index]
        v3_index = polygon.vertices[index + 1] 

        v2 = obj.vertices[v2_index.vertex - 1]
        v3 = obj.vertices[v3_index.vertex - 1]

        # Add the edges of the triangle to the mesh.
        # 3 edges defined by 3 pairs of vertices.
        edge_mesh.vertices.extend((*v1, *v2, *v2, *v3, *v3, *v1))

        # Add an index to each each to the edge_index.
        edge_mesh.index.append(edge_count)
        edge_count += 1
        edge_mesh.index.append(edge_count)
        edge_count += 1
        edge_mesh.index.append(edge_count)

        # Handle the normals.
        v2_normal_index = v2_index.normal
        if v2_normal_index is None:
          # TODO: If there isn't a normal, calculate it.
          raise NotImplementedError('Obj files without vertex normals is currently not supported.')
        
        v3_normal_index = v3_index.normal
        if v3_normal_index is None:
          # TODO: If there isn't a normal, calculate it.
          raise NotImplementedError('Obj files without vertex normals is currently not supported.')
      
        v2_normal = obj.vertex_normals[v2_normal_index - 1]
        v3_normal = obj.vertex_normals[v3_normal_index - 1]
        edge_mesh.vertex_normals.extend((*v1_normal, *v2_normal,  *v2_normal, *v3_normal, *v1_normal))

    return edge_mesh