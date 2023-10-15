from __future__ import annotations

from agents_playground.loaders.obj_loader import Obj

class TriangleMesh:
  """
  Groups the various lists that must be created to load a mesh of triangles
  into GPUBuffer instances.
  """
  def __init__(self) -> None:
    self.vertices: list[float] = []  
    self.vertex_normals: list[float] = []  
    self.index: list[int] = []

  @staticmethod
  def from_obj(obj: Obj) -> TriangleMesh:
    """
    Given an Obj instance, produce a list of triangles defined by their vertices.
    
    A mesh is a collection of triangles. Each triangle is composed of 3 vertices.
    Each vertex has a normal and texture coordinate. 

    NOTE: Currently skipping texture coordinates.
    """
    tri_mesh = TriangleMesh()
    triangle_count = 0
    
    for polygon in obj.polygons:
      # Build either a single triangle (3 verts) or a fan (>3 verts) of triangles.
      
      # Use the first vertex as the point of the fan.
      fan_point_vertex_map = polygon.vertices[0]
      fan_point_vertex = obj.vertices[fan_point_vertex_map.vertex - 1]

      fan_point_normal_index = fan_point_vertex_map.normal
      if fan_point_normal_index is None:
        # TODO: If there isn't a normal, calculate it.
        raise NotImplementedError('Obj files without vertex normals is currently not supported.')
      fan_point_normal = obj.vertex_normals[fan_point_normal_index - 1]

      for index in range(1, len(polygon.vertices) - 1):
        # Build triangles using the fan point and the other vertices.
        v2_index = polygon.vertices[index]
        v3_index = polygon.vertices[index + 1] 

        v2 = obj.vertices[v2_index.vertex - 1]
        v3 = obj.vertices[v3_index.vertex - 1]

        # Add the triangle to the mesh
        tri_mesh.vertices.extend((*fan_point_vertex, *v2, *v3))

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
        tri_mesh.vertex_normals.extend((*fan_point_normal, *v2_normal, *v3_normal))

        tri_mesh.index.append(triangle_count)
        triangle_count += 1
    return tri_mesh