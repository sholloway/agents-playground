
from typing import Protocol

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

The Model-View matrix can be represented in column major form using the below convention.
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
  ...