from __future__ import annotations
import itertools
import more_itertools
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
  def from_obj_old(obj: Obj) -> TriangleMesh:
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
  
  @staticmethod
  def from_obj(obj: Obj) -> TriangleMesh:
    """
    Given an Obj instance, produce a list of triangles defined by their vertices.
    
    A mesh is a collection of triangles. Each triangle is composed of 3 vertices.
    Each vertex has a normal and texture coordinate. 

    Vertices are listed once. An index is provided to specify the vertex order.
    An index buffer must be used to render the mesh.
    Each stride in the VBO is of the form:
    Vx, Vy, Vz, Vw, Tu, Tv, Ni, Nj, Nk
    """
    # Question: How does the stride impact the index buffer?
    mesh = TriangleMesh()
    vertex_count = 0

    # Step 3: Build an index buffer that provides the order in which the vertices 
    # and their normals should be accessed to construct the polygons.
    for polygon in obj.polygons:
      # Build either a single triangle (3 verts) or a fan (>3 verts) of triangles.
      # Note: The OBJ file format store vertices in CCW order. That is maintained here.
      
      # Lets start simple and just get the basic example working. 
      # Assume we're just dealing with triangles.
      v1_pos = obj.vertices[polygon.vertices[0].vertex - 1]
      v1_tex = obj.texture_coordinates[polygon.vertices[0].texture - 1] if polygon.vertices[0].texture is not None else (0,0)
      v1_norm = obj.vertex_normals[polygon.vertices[0].normal - 1] if polygon.vertices[0].normal is not None else (0,0,0)
      
      mesh.vertices.extend((*v1_pos, *v1_tex, *v1_norm))
      mesh.index.append(vertex_count)
      vertex_count += 1
      
      v2_pos = obj.vertices[polygon.vertices[1].vertex - 1]
      v2_tex = obj.texture_coordinates[polygon.vertices[1].texture - 1] if polygon.vertices[1].texture is not None else (0,0)
      v2_norm = obj.vertex_normals[polygon.vertices[1].normal - 1] if polygon.vertices[1].normal is not None else (0,0,0)
      
      mesh.vertices.extend((*v2_pos, *v2_tex, *v2_norm))
      mesh.index.append(vertex_count)
      vertex_count += 1
      
      v3_pos = obj.vertices[polygon.vertices[2].vertex - 1]
      v3_tex = obj.texture_coordinates[polygon.vertices[2].texture - 1] if polygon.vertices[2].texture is not None else (0,0,0)
      v3_norm = obj.vertex_normals[polygon.vertices[2].normal - 1] if polygon.vertices[2].normal is not None else (0,0,0)
      
      mesh.vertices.extend((*v3_pos, *v3_tex, *v3_norm))
      mesh.index.append(vertex_count)
      vertex_count += 1
      
    return mesh