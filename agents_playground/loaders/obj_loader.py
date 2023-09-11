"""
A simple OBJ parser. 

Reads an OBJ 3D file.
"""

import os
from typing import NamedTuple

SPACE = ' '

class ObjVertex3d(NamedTuple):
  x: float
  y: float
  z: float
  w: float 

class Obj:
  """Represents a 3d model."""
  def __init__(self) -> None:
    self.comments: int = 0
    self.vertices: list[ObjVertex3d] = []
      
class ObjParserMalformedVertexError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)


class ObjVertexLineParser:
  def __init__(self) -> None:
    pass

  def parse(self, obj: Obj, line: str, line_num: int) -> None:
    tokens: list[str] = line.split(SPACE)
    print(tokens)

    if not (len(tokens) == 4 or len(tokens) == 5):
      raise ObjParserMalformedVertexError(f'Line: {line_num} - Vertex definition must be of the form\nv x y z [w]\nFound: {line}')
        
    try:
      x = float(tokens[1])
      y = float(tokens[2])
      z = float(tokens[3])
      w = float(tokens[4]) if len(tokens) == 5 else 1.0

      obj.vertices.append(ObjVertex3d(x, y, z, w))
    except ValueError:
      raise ObjParserMalformedVertexError(f'Line: {line_num} - Vertex definition must be of the form\nv x y z [w]\nFound: {line}')

class ObjLineParser:
  def __init__(self) -> None:
    self.vertex_parser = ObjVertexLineParser()
  def parse_line(self, obj: Obj, line: str, line_num: int) -> None:
    """Parses a single line of an Obj file."""
    match line[0]:
      case '#': # Comment. Do nothing.
        obj.comments += 1
      case 'v': # Vertex
        self.vertex_parser.parse(obj, line, line_num)

class ObjLoader:
  """
  The OBJ Format is a command per line with each line starting with an indicator
  char. Lines are space delimited.

  This parser does not support the full OBJ Spec at the moment.

  Supported Commands:
  Reference: https://en.wikipedia.org/wiki/Wavefront_.obj_file
  - #: A comment. Not parsed.
  - v: Vertex. Format: v x y z [w]. W is optional and defaults to 1. Example: v 0.123 0.234 0.345 1.0
  - vt: Texture Coordinates. Format: u, [v, w]. v,w are option and default to 0. Example: vt 0.500 1 [0]
  - vn: Vertex Normals. Format: x y z. Normals may not be unit vectors. Example: vn 0.707 0.000 0.707
  - f: Polygon Face. 
    Format: Faces are defined using lists of vertex, texture and normal indices 
    in the format vertex_index/texture_index/normal_index for which each index 
    starts at 1 and increases corresponding to the order in which the referenced
    element was defined. Polygons such as quadrilaterals can be defined by using 
    more than three indices.

    Formats:
      - Just Vertices
        f v1 v2 v3 ....
      - Vertex texture coordinate indices.
        f v1/vt1 v2/vt2 v3/vt3 ...
      - Vertex normal indices
        f v1/vt1/vn1 v2/vt2/vn2 v3/vt3/vn3 ...
      - Vertex normal indices without texture coordinate indices
        f v1//vn1 v2//vn2 v3//vn3 ...
  """
  def __init__(self) -> None:
    self.parser = ObjLineParser()

  def load(self, filepath: str) -> Obj:
    """
    1. Does the file exist?
    2. Parse Vertices
    3. Parse Texture Coordinates
    4. Parse Vertex Normals
    5. Parse Polygon Faces
    """
    
    if not os.path.isfile(filepath) or os.path.exists(filepath):
      raise FileNotFoundError(f'The file {filepath} could not be found.')
    
    obj = Obj()
    line_num = 1
    with open(file = filepath, mode = 'r') as filereader:
      line = filereader.readline()
      self.parser.parse_line(obj, line, line_num)
      line_num += 1
    
    return obj