from __future__ import annotations
from abc import abstractmethod

from typing import Protocol
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import m4
from agents_playground.spatial.vector import Vector

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

In order to get into the Clip Space coordinate system (see the WebGPU section below)
we need to apply a projection matrix.

A projection matrix is of the form:
N = Near Pane (Z axis)
F = Far Pane (Z axis)
right = the Right Pane (X axis)
left = the Left Pane (X axis)
top = the Top Pane (Y axis)
bott = the Bottom Pane (Y axis)
|2N/(right - left), 0,              (right + left)/(right - left),  0         |
|0,                2N/(top - bott), (top + bott)/(top - bott),      0         |
|0,                0,               -(F + N)/(F - N),               -2FN/(F-N)|
|0,                0,               -1,                             0         |

** Perspective Matrix (P) **
A perspective matrix is a concept from legacy OpenGL. 
It is a projection matrix calculated from view angle and aspect ratio rather than
the view box. The result is the same.
To build a projection matrix from the perspective components use:
  top = N * tan(view_angle/2)
  bott = -top
  right = top * aspect
  left = -right


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
WebGPU Coordinate Systems
https://www.w3.org/TR/webgpu/#coordinate-systems

**Normalized Device Coordinates (NDC)**
NDC has 3 dimensions (X,Y,Z)

Horizontal Axis (X): -1.0 ≤ x ≤ 1.0
Vertical Axis (Y): -1.0 ≤ y ≤ 1.0
Depth Axis (Z): 0.0 ≤ z ≤ 1.0

The bottom-left corner is at (-1.0, -1.0, z).

**Clip Space**
Clip space coordinates have four dimensions: (x, y, z, w).

WebGPU's coordinate system is called clip space. The position output of a vertex shader 
is in clip space. Clip space is in the range Y (vertical) [-1,-1] and X (horizontal) 
[-1,-1] with (0,0) at the center of the viewport.
           [1]
            |
            |
            |
 [-1] --------------[1]
            |
            |
            |       
          [-1]

The relationship between NDC and Clip Space is controlled by clip space's w component.
If point p = (p.x, p.y, p.z, p.w) is in the clip volume, then its normalized 
device coordinates are (p.x ÷ p.w, p.y ÷ p.w, p.z ÷ p.w).

**Framebuffer Coordinates**
A framebuffer is a collection of pixels. It is the output of the rasterization 
rendering process.
- They have two dimensions.
- Each pixel extends 1 unit in X and Y dimensions.
- The top-left corner is at (0.0, 0.0).
- X increases to the right.
- Y increases down.

**Viewport Coordinates**
Viewport coordinates combine framebuffer coordinates in x and y dimensions, with
depth in z.

Normally 0.0 ≤ z ≤ 1.0, but this can be modified by setting 
[[viewport]].minDepth and maxDepth via setViewport().
--------------------------------------------------------------------------------
# Common 3D Cameras

**Look At Camera**
https://carmencincotti.com/2022-04-25/cameras-theory-webgpu/
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

class CameraException(Exception):
  def __init__(self, *args: object) -> None:
    super().__init__(*args)

class Camera(Protocol):
  projection_matrix: Matrix
  position: Vector
  target: Vector
  right: Vector | None
  up: Vector | None
  facing: Vector | None
  
  @property
  @abstractmethod
  def view_matrix(self) -> Matrix[float]: 
    ...


# class Camera2d(Camera):
#   ...

class Camera3d(Camera):
  def __init__(
    self, 
    projection_matrix: Matrix,
    position: Vector,
    target: Vector,
    right: Vector | None = None,
    up: Vector | None = None,
    facing: Vector | None = None
  ) -> None:  
    self._projection_matrix = projection_matrix
    self.position = position
    self.target   = target
    self.right    = right 
    self.up       = up 
    self.facing   = facing


  @staticmethod
  def look_at(
    position: Vector, 
    target: Vector, 
    projection_matrix: Matrix) -> Camera:
    camera = Camera3d(projection_matrix, position, target)
    camera.update()
    return camera
  
  def update(self):
    """
    Recalculates the UP, RIGHT, and FACING vectors for use in the view matrix. 
    The calculations leverage the current values for position and target.
    """
    self.facing = (self.position - self.target).unit()
    self.right = Vector3d(0,1,0).cross(self.facing).unit()
    self.up = self.facing.cross(self.right).unit()

  @property
  def projection_matrix(self) -> Matrix[float]:
    return self._projection_matrix 
  
  @projection_matrix.setter
  def projection_matrix(self, new_projection: Matrix[float]) -> None:
    self._projection_matrix = new_projection
  
  @property
  def view_matrix(self) -> Matrix[float]: 
    """
    The View Matrix is the inverse of the look_at matrix and can be represented 
    using the below convention.
    | RIGHTx,        UPx,           FACINGx,       0 |
    | RIGHTy,        UPy,           FACINGy,       0 |
    | RIGHTz,        UPz,           FACINGz,       0 |
    | -TranslationX, -TranslationY, -TranslationZ, 1 |

    Source: https://carmencincotti.com/2022-04-25/cameras-theory-webgpu/
    """
    if (self.right is None or 
      self.up is None or 
      self.facing is None):
      warning = 'The FACING, RIGHT, and UP vectors must be calculated before calling view_matrix.'
      guidance = 'To calculate the 3 vectors, set the position and target vectors and then call the update() method.'
      err_msg = f"{warning}\n{guidance}"
      raise CameraException(err_msg)
    
    translation = Vector3d(
      self.position * self.right,
      self.position * self.up,
      self.position * self.facing
    )

    return m4(
      self.right.i,     self.up.i,        self.facing.i, 0,
      self.right.j,     self.up.j,        self.facing.j, 0,
      self.right.k,     self.up.k,        self.facing.k, 0,
      -translation.i,   -translation.j,   -translation.k, 1
    )  