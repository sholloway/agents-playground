"""
A simple OBJ parser. 

Reads an OBJ 3D file.
"""

class Obj:
  """Represents a 3d model."""


class ObjParser:
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
    pass

  def parse(self, file_path) -> Obj:
    """
    1. Does the file exist?
    2. Parse Vertices
    3. Parse Texture Coordinates
    4. Parse Vertex Normals
    5. Parse Polygon Faces
    """
    ...
