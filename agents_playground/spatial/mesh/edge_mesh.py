from __future__ import annotations
from deprecated import deprecated

from agents_playground.loaders.obj_loader import Obj

@deprecated(reason="This class is replaced by the MeshLike and MeshBuffer implementations.")
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
  def from_obj_old(obj: Obj) -> EdgeMesh:
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
  
  @staticmethod
  def from_obj(obj: Obj) -> EdgeMesh:
    """
    Given an Obj instance, produce a list of edges defined by their vertices.
    
    A mesh is a collection of edges. Each triangle is composed of 2 vertices.
    Each vertex has a normal and texture coordinate. 

    An index is provided to specify the vertex order.
    An index buffer must be used to render the mesh.
    Each stride in the VBO is of the form:
    Vx, Vy, Vz, Vw, Tu, Tv, Ni, Nj, Nk
    """
    # Question: How does the stride impact the index buffer?
    mesh = EdgeMesh()
    vertex_count = 0

    # Step 3: Build an index buffer that provides the order in which the vertices 
    # and their normals should be accessed to construct the polygons.
    for polygon in obj.polygons:
      # Build either a single triangle (3 verts) or a fan (>3 verts) of triangles.
      # Note: The OBJ file format store vertices in CCW order. That is maintained here.

      v1_pos = obj.vertices[polygon.vertices[0].vertex - 1]
      v1_tex = obj.texture_coordinates[polygon.vertices[0].texture - 1] if polygon.vertices[0].texture is not None else (0,0)
      v1_norm = obj.vertex_normals[polygon.vertices[0].normal - 1] if polygon.vertices[0].normal is not None else (0,0,0)
      
      for vert_index in range(1, len(polygon.vertices) - 1):
        # Build triangles using the fan point and the other vertices.
        v2_index = polygon.vertices[vert_index]
        v3_index = polygon.vertices[vert_index + 1] 
        
        # Edge 1
        # Add the triangle point. This will be added multiple times for a fan.
        mesh.vertices.extend((*v1_pos, *v1_tex, *v1_norm))
        mesh.index.append(vertex_count)
        vertex_count += 1
      
        v2_pos = obj.vertices[v2_index.vertex - 1]
        v2_tex = obj.texture_coordinates[v2_index.texture - 1] if v2_index.texture is not None else (0,0)
        v2_norm = obj.vertex_normals[v2_index.normal - 1] if v2_index.normal is not None else (0,0,0)
        
        mesh.vertices.extend((*v2_pos, *v2_tex, *v2_norm))
        mesh.index.append(vertex_count)
        vertex_count += 1

        # Edge 2
        mesh.vertices.extend((*v2_pos, *v2_tex, *v2_norm))
        mesh.index.append(vertex_count)
        vertex_count += 1
        
        v3_pos = obj.vertices[v3_index.vertex - 1]
        v3_tex = obj.texture_coordinates[v3_index.texture - 1] if v3_index.texture is not None else (0,0,0)
        v3_norm = obj.vertex_normals[v3_index.normal - 1] if v3_index.normal is not None else (0,0,0)
        
        mesh.vertices.extend((*v3_pos, *v3_tex, *v3_norm))
        mesh.index.append(vertex_count)
        vertex_count += 1

        # Edge 3
        mesh.vertices.extend((*v3_pos, *v3_tex, *v3_norm))
        mesh.index.append(vertex_count)
        vertex_count += 1

        mesh.vertices.extend((*v1_pos, *v1_tex, *v1_norm))
        mesh.index.append(vertex_count)
        vertex_count += 1
      
    return mesh