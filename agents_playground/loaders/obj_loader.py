"""
A simple OBJ parser. 

Reads an OBJ 3D file.
"""
from __future__ import annotations
import os
from typing import List, NamedTuple

from agents_playground.spatial.vector3d import Vector3d

SPACE: str = ' '
VERT_W_DEFAULT: float = 1.0
TEXT_COORD_V: float = 0
TEXT_COORD_W: float = 0

class ObjVertex3d(NamedTuple):
  x: float
  y: float
  z: float
  w: float 

class ObjTextureCoordinate(NamedTuple):
  u: float 
  v: float
  w: float 

class Obj:
  """Represents a 3d model."""
  def __init__(self) -> None:
    self.comments: int = 0
    self.vertices: List[ObjVertex3d] = []
    self.texture_coordinates: List[ObjTextureCoordinate] = []
    self.vertex_normals: List[Vector3d] = []
      
class ObjParserMalformedVertexError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ObjParserMalformedTextureCoordinateError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class ObjParserMalformedVertexNormalError(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

def is_in_unit_interval(value: float) -> bool:
  return 0 <= value and value <= 1.0

class ObjVertexLineParser:
  def parse(self, obj: Obj, tokens: List[str], line: str, line_num: int) -> None:
    if not (len(tokens) == 4 or len(tokens) == 5):
      self._raise_error(line_num, line)
        
    try:
      x = float(tokens[1])
      y = float(tokens[2])
      z = float(tokens[3])
      w = float(tokens[4]) if len(tokens) == 5 else VERT_W_DEFAULT
      obj.vertices.append(ObjVertex3d(x, y, z, w))
    except ValueError:
      self._raise_error(line_num, line)
    
  def _raise_error(self, line_num: int, line: str) -> None:
    raise ObjParserMalformedVertexError(f'Line: {line_num} - Vertex definition must be of the form\nv x y z [w]\nFound: {line}')

class ObjTextureCoordinateLineParser:
  def parse(self, obj: Obj, tokens: List[str], line: str, line_num: int) -> None:
    if len(tokens) not in [2,3,4]:
      self._raise_error(line_num, line)

    try:
      u = float(tokens[1])
      v = float(tokens[2]) if len(tokens) > 2 else TEXT_COORD_V
      w = float(tokens[3]) if len(tokens) > 3 else TEXT_COORD_W

      # u, v, and w must all be in the range [0,1] (inclusive).
      if not is_in_unit_interval(u) or \
        not is_in_unit_interval(v) or \
        not is_in_unit_interval(w):
        self._raise_error(line_num, line)

      obj.texture_coordinates.append(ObjTextureCoordinate(u, v, w))
    except:
      self._raise_error(line_num, line)

  def _raise_error(self, line_num: int, line: str) -> None:
    raise ObjParserMalformedTextureCoordinateError(f'Line: {line_num} - Texture Coordinate definition must be of the form\nvt u [v] [w] where u,v,w are in the unit interval.\nFound: {line}')

class ObjVertexNormalLineParser:
  def parse(self, obj: Obj, tokens: List[str], line: str, line_num: int) -> None:
    if len(tokens) != 4:
      self._raise_error(line_num, line)

    try:
      i = float(tokens[1])
      j = float(tokens[2]) 
      k = float(tokens[3]) 

      obj.vertex_normals.append(Vector3d(i, j, k))
    except:
      self._raise_error(line_num, line)

  def _raise_error(self, line_num: int, line: str) -> None:
    raise ObjParserMalformedVertexNormalError(f'Line: {line_num} - Vertex normal definition must be of the form\nvn x y z\nFound: {line}')

class ObjLineParser:
  def __init__(self) -> None:
    self.vertex_parser = ObjVertexLineParser()
    self.texture_coord_parser = ObjTextureCoordinateLineParser()
    self.vertex_normal_parser = ObjVertexNormalLineParser()
  
  def parse_line(self, obj: Obj, line: str, line_num: int) -> None:
    """Parses a single line of an Obj file."""

    tokens: list[str] = line.split(SPACE)
    match tokens[0]:
      case '#': # Comment. Do nothing.
        obj.comments += 1
      case 'v': # Vertex
        self.vertex_parser.parse(obj, tokens, line, line_num)
      case 'vt': # Texture Coordinate
        self.texture_coord_parser.parse(obj, tokens, line, line_num)
      case 'vn': # Vertex Normals
        self.vertex_normal_parser.parse(obj, tokens, line, line_num)


class ObjLoader:
  """
  The OBJ Format is a command per line with each line starting with an indicator
  char. Lines are space delimited.

  This parser does not support the full OBJ Spec at the moment.

  Supported Commands:
  Reference: https://en.wikipedia.org/wiki/Wavefront_.obj_file
  - #: A comment. Not parsed.
  - v: Vertex. Format: v x y z [w]. W is optional and defaults to 1. Example: v 0.123 0.234 0.345 1.0
  - vt: Texture Coordinates. Format: u, [v, w]. v,w are optional and default to 0. Example: vt 0.500 1 [0]
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