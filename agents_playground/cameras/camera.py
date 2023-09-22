
from __future__ import annotations
from enum import Enum
import itertools
import more_itertools
from typing import Generic, List, Protocol, Tuple, TypeVar

from agents_playground.spatial.vector3d import Vector3d

"""
**Requirements**
The camera protocol should:
- Support both 2D and 3D use cases. 
- Enable defining different projection models. 
- Enable "looking at" a point.
- Be separate from translation and rotation logic.
- Support rotation across the three primary camera vectors. 
  Y-axis (Up): Yaw
  X-axis (side): Pitch
  Negative Z-axis (front): Roll
- Enable zooming and panning
- Enable easy to understand configurable parameters.
  Field of View: fov
  Aspect Ratio: ar
  Depth of Field: dof
- Enable calculating the view frustum. 

Design Goals
- Enable passing in projection models.
- Make it straightforward to bind the internal matrices to uniform buffers.

Concepts
**World Transformation Matrix (M)**
The matrix that determines the position and orientation of an object in 3D space.
This transforms the model from object space (the coordinates used by the modeling tool)
to world space (the scene). The World Transformation Matrix is the Translation (T),
Rotate (R), and Scale (S) that needs to be applied to position, orientate, and scale
the model into the simulation.
M = TRS(v)

**View Matrix (V)** 
Transforms the model's vertices from world-space to view-space.

There is an inverse relationship between a camera's World Transformation Matrix (M) and
its View Matrix (V). 
V = M^-1 and M = V^-1

**The Model-View Matrix (VM)**
A combination of two effects.
1. The model transformations (M) applied to objects.
2. The transformation that orients and positions the camera (V). 
Model-View Matrix = VM

Consider that the view matrix V is changing the coordinates of the object from
world coordinates to the camera's coordinate system. The camera coordinate system
is sometimes referred to as eye coordinates.

The View volume extends:
- From Left to Right along the camera's x-axis.
- From Bottom to Top along the camera's y-axis.
- From -Near to -Far along the camera's z-axis.

Note: The distance from the camera to the vertices being rendered is either 
negative or positive depending on if the camera is using a right-handed (negative) 
or left-handed (positive) coordinate system.

The View matrix can be represented in column major form using the below convention.
- The first three columns are the camera's right(X), up (Y), facing (Z) vectors.
- The 4th column is the translation of the camera (position).
 | RIGHTx, UPx, FACINGx, POSITIONx |
 | RIGHTy, UPy, FACINGy, POSITIONy |
 | RIGHTz, UPz, FACINGz, POSITIONz |
 | 0,      0,   0,       1         |

**The Projection Matrix (P)**
Scales and shifts each mesh vertex in a particular way so that they lie inside
a standard cube that extends from -1 to 1 in each dimension.
This changes based on what projection strategy is being used.

The projection matrix reverses the direction of the z-axis.

**The Viewport Matrix (Vp)**
Maps the remaining vertices (that were not clipped) into a 3D "viewport".
This matrix maps the standard cube from the projection matrix into a block shape
whose X and Y values extend across the viewport in screen coordinates and 
whose Z values extend from 0 to 1 and retains a measure of the depth of 

**The Graphics Pipeline**
Vertices (v) -> VM-> P -> Clipping is applied -> Perspective Division is Done -> Vp -> Image

This pipeline translates the vertices coordinates from:
1. World Coordinates, to...
2. Camera Coordinates, to...
3. Normalized Device Coordinates (the standard cube), to...
4. Window/Screen Coordinates

To apply the graphics pipeline to a vertex (v), the matrices are applied right to left.
v' = P*V*M*v
--------------------------------------------------------------------------------
# Common 3D Cameras

**Look At Camera**
A look at camera is one in which the View Matrix (V) is built from the camera's 
position, up vector, and the position to look at.

**First Person Camera**
Cameras used in first person shooters tend to leverage camera's position and the
rotation around the camera's 3 vectors.
  X-axis (side): Pitch
  Y-axis (Up): Yaw
  Negative Z-axis (front): Roll

The View Matrix (V) for an FPS camera can be found by:
1. Apply the rotation around the X-axis (pitch, Rx).
2. Apply the rotation around the Y-axis (yaw, Ry).
3. Apply the rotation around the Z-axis (roll, Rz).
4. Translate (T) the camera to it's location in the world.
5. Find the inverse of the resulting matrix.

V = (T * Ry * Rx)^-1

**Arcball Camera**
An arcball camera locks the camera onto an object and moves the camera in relation
to the focus object.

Arcball cameras suffer from the Gimbal-lock problem. To work around this use 
quaternions.
"""
class Camera(Protocol):
  ...

class Camera2d(Camera):
  ...

class Camera3d(Camera):
  def __init__(
    self, 
    position: Vector3d = Vector3d(0,0,-10),
    right: Vector3d = Vector3d(1,0,0), 
    up: Vector3d = Vector3d(0,1,0), 
    facing: Vector3d = Vector3d(0,0,0), 
  ) -> None:  
    self.right    = right 
    self.up       = up 
    self.facing   = facing
    self.position = position

  def to_view_matrix(self) -> Matrix4x4: 
    """
    The View matrix can be represented in column major form using the below convention.
    The first three columns are the camera's right(X), up (Y), facing (Z) vectors.
    The 4th column is the translation of the camera (position).
    | RIGHTx, UPx, FACINGx, POSITIONx |
    | RIGHTy, UPy, FACINGy, POSITIONy |
    | RIGHTz, UPz, FACINGz, POSITIONz |
    | 0,      0,   0,       1         |
    """
    return m4(
      self.right.i, self.up.i, self.facing.i, self.position.i,
      self.right.j, self.up.j, self.facing.j, self.position.j,
      self.right.k, self.up.k, self.facing.k, self.position.k,
      0,            0,         0,             1
    )

T = TypeVar('T')
RowMajorNestedTuple = Tuple[Tuple[T, ...], ...]

class MatrixOrder(Enum):
  Row = 0
  Column = 1

def m4(m00: T, m01: T, m02: T, m03: T,
		m10: T, m11: T, m12: T, m13: T,
		m20: T, m21: T, m22: T, m23: T,
		m30: T, m31: T, m32: T, m33: T) -> Matrix4x4[T]:
  data = ( 
    (m00, m01, m02, m03),
    (m10, m11, m12, m13),
    (m20, m21, m22, m23),
    (m30, m31, m32, m33)
  )
  return Matrix4x4[T](data)

def flatten(data: RowMajorNestedTuple, major: MatrixOrder) -> Tuple[T, ...]:
  match major:
    case MatrixOrder.Row:
      return tuple(more_itertools.flatten(data))
    case MatrixOrder.Column:
      return ( 
        data[0][0], data[0][1], data[2][0], data[3][0], 
        data[0][1], data[1][1], data[2][1], data[3][1], 
        data[0][2], data[1][2], data[2][2], data[3][2], 
        data[0][3], data[1][3], data[2][3], data[3][3], 
      )

class Matrix4x4Error(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class Matrix4x4(Generic[T]):
  """
  An immutable 4 by 4 matrix. Internally the data is stored in a flattened 
  tuple in row-major form.
  """
  def __init__(self, data: RowMajorNestedTuple) -> None:
    self._data = flatten(data, MatrixOrder.Row)
    self.width = 4
    self.height = 4

  @staticmethod
  def identity() -> Matrix4x4:
    return m4(
      1, 0, 0, 0,
      0, 1, 0, 0,
      0, 0, 1, 0,
      0, 0, 0, 1
    )

  def i(self, row: int, col: int) -> T:
    """Finds the stored value in the matrix at matrix[i][j] using row-major convention."""
    # https://en.wikipedia.org/wiki/Row-_and_column-major_order
    if row >= 0 and row < 4 and col >= 0 and col < 4:
      index = row * self.width + col
      return self._data[index]
    else:
      general_msg = 'Attempted to access an element in a Matrix4x4 at an invalid index.'
      usage_msg = 'matrix.i(row, col) only accepts values in the range [0,3].'
      found_msg = f'found matrix.i(row={row}, col={col})'
      msg = f'{general_msg}\n{usage_msg}\n{found_msg}'
      raise Matrix4x4Error(msg)

  def flatten(self, major: MatrixOrder = MatrixOrder.Column) -> Tuple[T, ...]:
    """
    Flattens the matrix into a tuple.

    Args:
      - major (MatrixOrder): Determines if the returned tuple will be in row-major
        or column-major order. The default is MatrixOrder.Column.

    Returns 
    The flattened tuple is either of the form:
    For the matrix:
      | m00, m01, m02, m03 |
      | m10, m11, m12, m13 |
      | m20, m21, m22, m23 |
      | m30, m31, m32, m33 |
  
    Row-Major
    (m00, m01, m02, m03, m10, m11, m12, m13, m20, m21, m22, m23, m30, m31, m32, m33)

    Column-Major
    (m00, m10, m20, m30, m01, m11, 21, m31, m02, m12m, m22m, m03, m13, m23, m33)
    """
    match major:
      case MatrixOrder.Row:
        return self._data
      case MatrixOrder.Column:
        return (
          self.i(0,0), self.i(1,0), self.i(2,0), self.i(3,0),
          self.i(0,1), self.i(1,1), self.i(2,1), self.i(3,1),
          self.i(0,2), self.i(1,2), self.i(2,2), self.i(3,2),
          self.i(0,3), self.i(1,3), self.i(2,3), self.i(3,3),
        )
  
  def transpose(self) -> Matrix4x4:
    return m4(
      self.i(0,0), self.i(1,0), self.i(2,0), self.i(3,0),
      self.i(0,1), self.i(1,1), self.i(2,1), self.i(3,1),
      self.i(0,2), self.i(1,2), self.i(2,2), self.i(3,2),
      self.i(0,3), self.i(1,3), self.i(2,3), self.i(3,3),
    ) 
