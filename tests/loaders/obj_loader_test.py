import pytest
import os 
from pathlib import Path

from agents_playground.loaders.obj_loader import (
  EdgeMesh,
  Obj, 
  ObjLineParser, 
  ObjLoader, 
  ObjParserMalformedPolygonError, 
  ObjParserMalformedTextureCoordinateError, 
  ObjParserMalformedVertexError, 
  ObjParserMalformedVertexNormalError, 
  ObjTextureCoordinate, 
  TriangleMesh
)

from agents_playground.spatial.vector3d import Vector3d

class TestObjLoader:
  def test_file_does_not_exist(self) -> None:
    loader = ObjLoader()
    with pytest.raises(FileNotFoundError):
      loader.load(filepath='not/a/real/file/junk.obj')

  def test_load_cube(self) -> None:
    loader = ObjLoader()
    path = os.path.join(Path.cwd(), 'tests/loaders/cube.obj')
    obj = loader.load(path)
    assert obj.comments == 1
    assert len(obj.vertices) == 8
    assert len(obj.texture_coordinates) == 14
    assert len(obj.vertex_normals) == 24
    assert len(obj.polygons) == 6

  def test_build_triangles(self) -> None:
    loader = ObjLoader()
    path = os.path.join(Path.cwd(), 'tests/loaders/skull.obj')
    obj = loader.load(path)

    triangle_mesh: TriangleMesh = TriangleMesh.from_obj(obj)

    num_polygons = len(obj.polygons)
    vertices_per_face = 3
    vert_dimensions = 4 # (x,y,z,w)

    assert len(triangle_mesh.vertices) == num_polygons * vertices_per_face * vert_dimensions
    assert len(triangle_mesh.index) == num_polygons

    # Verify the first triangle from the mesh.
    # f 1/1/1 2/2/2 4/4/3
    # 1/1/1
    assert triangle_mesh.vertices[0] == 0.137756  # v1.x
    assert triangle_mesh.vertices[1] == -0.214096 # v1.y
    assert triangle_mesh.vertices[2] == -0.214096 # v1.z
    assert triangle_mesh.vertices[3] == 1.0       # v1.w 

    assert triangle_mesh.vertex_normals[0] == 0.092330  # vn1.x
    assert triangle_mesh.vertex_normals[1] == -0.786161 # vn1.y
    assert triangle_mesh.vertex_normals[2] == 0.611086  # vn1.z

    # 2/2/2
    assert triangle_mesh.vertices[4] == 0.299240  # v2.x
    assert triangle_mesh.vertices[5] == -0.170795 # v2.y
    assert triangle_mesh.vertices[6] == 0.076241  # v2.z
    assert triangle_mesh.vertices[7] == 1.0      # v2.w 

    assert triangle_mesh.vertex_normals[3] == 0.026584  # vn2.x
    assert triangle_mesh.vertex_normals[4] == -0.864618 # vn2.y
    assert triangle_mesh.vertex_normals[5] == -0.864618  # vn2.z
    
    # 4/4/3   
    assert triangle_mesh.vertices[8] == 0.111707  # v3.x
    assert triangle_mesh.vertices[9] == -0.180897 # v3.y
    assert triangle_mesh.vertices[10] == 0.085708  # v3.z
    assert triangle_mesh.vertices[11] == 1.0      # v3.w 

    assert triangle_mesh.vertex_normals[6] == 0.094768  # vn3.x   
    assert triangle_mesh.vertex_normals[7] == -0.779686 # vn3.y
    assert triangle_mesh.vertex_normals[8] == 0.618958  # vn3.z

  

class TestObjLineParser:
  def test_skip_comments(self) -> None:
    parser = ObjLineParser()
    model = Obj()
    assert model.comments == 0
    parser.parse_line(model, '# This is a comment.', 1)
    assert model.comments == 1
    parser.parse_line(model, '# This is another comment.', 1)
    assert model.comments == 2

  def test_parse_bad_vertex(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    with pytest.raises(ObjParserMalformedVertexError):
      parser.parse_line(model, 'v 1 0', 1)
    
    with pytest.raises(ObjParserMalformedVertexError):
      parser.parse_line(model, 'v 1 0 1 a b c', 2)

    with pytest.raises(ObjParserMalformedVertexError):
      parser.parse_line(model, 'v 1 0 a', 3)

  def test_parse_simple_vertex(self) -> None:
    parser = ObjLineParser()
    model = Obj()
    parser.parse_line(model, 'v 1 0 1', 1)
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 2)
    parser.parse_line(model, 'v 1 0.14 22', 3)
    assert len(model.vertices) == 3
    for vert in model.vertices:
      assert vert.w == 1.0

  def test_parse_vertex_with_w(self) -> None:
    parser = ObjLineParser()
    model = Obj()
    parser.parse_line(model, 'v 1 0 1 0.4', 1)
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 1)
    parser.parse_line(model, 'v 1 0.14 22 0.2', 1)
    assert len(model.vertices) == 3
    assert model.vertices[0].w == 0.4
    assert model.vertices[1].w == 1
    assert model.vertices[2].w == 0.2

  def test_bad_texture_coordinates(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt', 1)
    
    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt a', 1)
    
    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt 14', 1, strict=True)
    
    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt -1', 1, strict=True)
    
    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt 0.18 0.22 0.45 0.25', 1)

  def test_does_not_raise_when_strict_is_off(self):
    parser = ObjLineParser()
    model = Obj()
    try:
      parser.parse_line(model, 'vt 14', 1, strict=False) 
      parser.parse_line(model, 'vt -1', 1, strict=False)
    except ObjParserMalformedTextureCoordinateError:
      assert False, 'ObjParserMalformedTextureCoordinateError should not have been thrown with strict=False. '

  def test_text_coordinates(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    parser.parse_line(model, 'vt 0.18', 1)    
    parser.parse_line(model, 'vt 0.18 0.22', 2)    
    parser.parse_line(model, 'vt 0.18 0.22 0.45', 3)    

    assert len(model.texture_coordinates) == 3
    assert model.texture_coordinates[0] == ObjTextureCoordinate(0.18, 0, 0)
    assert model.texture_coordinates[1] == ObjTextureCoordinate(0.18, 0.22, 0)
    assert model.texture_coordinates[2] == ObjTextureCoordinate(0.18, 0.22, 0.45)
    
  def test_bad_vertex_normal(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    with pytest.raises(ObjParserMalformedVertexNormalError):
      parser.parse_line(model, 'vn', 1)
    
    with pytest.raises(ObjParserMalformedVertexNormalError):
      parser.parse_line(model, 'vn 0.02 14.2 0.17 0.88', 1)

  def test_vertex_normal(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    parser.parse_line(model, 'vn 0.02 14.2 0.17', 1)  
    parser.parse_line(model, 'vn 14.7 9 -8.21', 2)  

    assert len(model.vertex_normals) == 2
    assert model.vertex_normals[0] == Vector3d(0.02, 14.2, 0.17)
    assert model.vertex_normals[1] == Vector3d(14.7, 9, -8.21)

  def test_bad_polygon(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    with pytest.raises(ObjParserMalformedPolygonError):
      parser.parse_line(model, 'f', 1)

  def test_polygon_with_just_vertices(self) -> None:
    # Test the use case f v1 v2 v3
    parser = ObjLineParser()
    model = Obj()

    # Set up the vertices for the polygon.
    parser.parse_line(model, 'v 1 0 1', 1)
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 2)
    parser.parse_line(model, 'v 1 0.14 22', 3)
    parser.parse_line(model, 'v 4.75 2.14 17.8', 4)

    assert len(model.vertices) == 4

    # Specifically selecting 1,2,3,4 to make asserting in a loop easier.
    parser.parse_line(model, 'f 1 2 3 4', 5) 
    assert len(model.polygons) == 1
    assert len(model.polygons[0].vertices) == 4

    for vert_index in range(len(model.polygons[0].vertices)):
      assert model.polygons[0].vertices[vert_index].vertex == vert_index + 1
      assert model.polygons[0].vertices[vert_index].texture is None
      assert model.polygons[0].vertices[vert_index].normal is None

  def test_polygon_with_texture_coordinates(self) -> None:
    # Test the use case f v1/vt1 v2/vt2 v3/vt3 v4/vt4
    parser = ObjLineParser()
    model = Obj()

    # Set up the vertices for the polygon.
    parser.parse_line(model, 'v 1 0 1', 1)
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 2)
    parser.parse_line(model, 'v 1 0.14 22', 3)
    parser.parse_line(model, 'v 4.75 2.14 17.8', 4)

    # Setup the texture coordinates for the polygon.
    parser.parse_line(model, 'vt 0.18', 5)
    parser.parse_line(model, 'vt 0.11', 6)
    parser.parse_line(model, 'vt 0.02', 7)
    parser.parse_line(model, 'vt 0.03', 8)

    assert len(model.vertices) == 4
    assert len(model.texture_coordinates) == 4

    parser.parse_line(model, 'f 1/1 2/2 3/3 4/4', 9)

    assert len(model.polygons) == 1
    assert len(model.polygons[0].vertices) == 4

    for vert_index in range(len(model.polygons[0].vertices)):
      assert model.polygons[0].vertices[vert_index].vertex == vert_index + 1
      assert model.polygons[0].vertices[vert_index].texture == vert_index + 1
      assert model.polygons[0].vertices[vert_index].normal is None

  def test_polygon_with_vertex_normals(self) -> None:
    # Test the use case f v1//vn1 v2//vn2
    parser = ObjLineParser()
    model = Obj()

    # Set up the vertices for the polygon.
    parser.parse_line(model, 'v 1 0 1', 1)
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 2)
    parser.parse_line(model, 'v 1 0.14 22', 3)
    parser.parse_line(model, 'v 4.75 2.14 17.8', 4)

    # Setup the vertex normals for the polygon.
    parser.parse_line(model, 'vn 1.18 -0.14 0.22', 5)
    parser.parse_line(model, 'vn 4.80 1.01 0.15', 6)
    parser.parse_line(model, 'vn 3.22 3.72 0.70', 7)
    parser.parse_line(model, 'vn -0.124 4.44 0.793', 8)
    
    assert len(model.vertices) == 4
    assert len(model.vertex_normals) == 4

    parser.parse_line(model, 'f 1//1 2//2 3//3 4//4', 9)

    assert len(model.polygons) == 1
    assert len(model.polygons[0].vertices) == 4

    for vert_index in range(len(model.polygons[0].vertices)):
      assert model.polygons[0].vertices[vert_index].vertex == vert_index + 1
      assert model.polygons[0].vertices[vert_index].texture is None
      assert model.polygons[0].vertices[vert_index].normal == vert_index + 1

  def test_polygons_with_vt_and_vn(self) -> None:
    # Test the use case f v/vt/vn
    parser = ObjLineParser()
    model = Obj()

    # Set up the vertices for the polygon.
    parser.parse_line(model, 'v 1 0 1', 1)
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 2)
    parser.parse_line(model, 'v 1 0.14 22', 3)
    parser.parse_line(model, 'v 4.75 2.14 17.8', 4)

    # Setup the texture coordinates for the polygon.
    parser.parse_line(model, 'vt 0.18', 5)
    parser.parse_line(model, 'vt 0.11', 6)
    parser.parse_line(model, 'vt 0.02', 7)
    parser.parse_line(model, 'vt 0.03', 8)

    # Setup the vertex normals for the polygon.
    parser.parse_line(model, 'vn 1.18 -0.14 0.22', 7)
    parser.parse_line(model, 'vn 4.80 1.01 0.15', 8)
    parser.parse_line(model, 'vn 3.22 3.72 0.70', 9)
    parser.parse_line(model, 'vn -0.124 4.44 0.793', 10)
    

    assert len(model.vertices) == 4
    assert len(model.texture_coordinates) == 4
    assert len(model.vertex_normals) == 4

    parser.parse_line(model, 'f 1/1/1 2/2/2 3/3/3 4/4/4', 11)

    assert len(model.polygons) == 1
    assert len(model.polygons[0].vertices) == 4

    for vert_index in range(len(model.polygons[0].vertices)):
      assert model.polygons[0].vertices[vert_index].vertex == vert_index + 1
      assert model.polygons[0].vertices[vert_index].texture == vert_index + 1
      assert model.polygons[0].vertices[vert_index].normal == vert_index + 1

  def test_polys_with_more_than_three_verts(self) -> None:
    # The TriangleMesh takes the strategy of building a triangle fan out of 
    # polygons that have more than three vertices. The fan's origin is located
    # at the first point.

    loader = ObjLoader()
    path = os.path.join(Path.cwd(), 'tests/loaders/cube.obj')
    obj = loader.load(path)

    triangle_mesh: TriangleMesh = TriangleMesh.from_obj(obj)

    # 6 faces on the cube. 2 triangles per face.
    assert len(triangle_mesh.index) ==  6 * 2

    # Each triangle has 3 vertices with 4 components apiece (i,j,k,w)
    assert len(triangle_mesh.vertices) == 6 * 2 * 3 * 4

  def test_load_edges(self) -> None:
    # Prepare the edges of a triangle mesh to be loaded into a line-list buffer.
    loader = ObjLoader()
    path = os.path.join(Path.cwd(), 'tests/loaders/cube.obj')
    obj = loader.load(path)

    edge_mesh = EdgeMesh.from_obj(obj)

    # There are 12 triangles on the cube. Each triangle has 3 edges.
    # A more efficient solution would only store an edge once.
    assert len(edge_mesh.index) == 12 * 3

    # To represent a list of edges, vertices are repeated. 
    # v1 -> v2, v2 -> v3, v3 -> v1
    # 6 faces -> 12 triangles -> 12 * 6 vertices -> 72 * 4 floats 
    assert len(edge_mesh.vertices) == 288