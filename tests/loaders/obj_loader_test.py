import pytest


from agents_playground.loaders.obj_loader import Obj, ObjLineParser, ObjLoader, ObjParserMalformedTextureCoordinateError, ObjParserMalformedVertexError, ObjParserMalformedVertexNormalError, ObjTextureCoordinate
from agents_playground.spatial.vector3d import Vector3d

class TestObjLoader:
  def test_file_does_not_exist(self) -> None:
    loader = ObjLoader()
    with pytest.raises(FileNotFoundError):
      loader.load(filepath='not/a/real/file/junk.obj')

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
    parser.parse_line(model, 'v 0.49 -1.23 1.119', 1)
    parser.parse_line(model, 'v 1 0.14 22', 1)
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
      parser.parse_line(model, 'vt 14', 1)
    
    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt -1', 1)
    
    with pytest.raises(ObjParserMalformedTextureCoordinateError):
      parser.parse_line(model, 'vt 0.18 0.22 0.45 0.25', 1)

  def test_text_coordinates(self) -> None:
    parser = ObjLineParser()
    model = Obj()

    parser.parse_line(model, 'vt 0.18', 1)    
    parser.parse_line(model, 'vt 0.18 0.22', 1)    
    parser.parse_line(model, 'vt 0.18 0.22 0.45', 1)    

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

    assert model.vertex_normals[0] == Vector3d(0.02, 14.2, 0.17)