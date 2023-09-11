import pytest


from agents_playground.loaders.obj_loader import Obj, ObjLineParser, ObjLoader, ObjParserMalformedVertexError

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
      parser.parse_line(model, 'v1 0 1', 1)
    
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
