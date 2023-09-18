
from typing import Protocol

"""
Reqs
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

**View Matrix (V)** 
Transforms the model's vertices from world-space to view-space.

**The Model View Matrix (VM)**
A combination of two effects.
1. The model transformations applied to objects.
2. The transformation that orients and positions the camera. 
modelview = V*M

Consider that the view matrix V is changing the coordinates of the object from
world coordinates to the camera's coordinate system. The camera coordinate system
is sometimes referred to as eye coordinates.

The View volume extends:
- From Left to Right along the camera's x-axis.
- From Bottom to Top along the camera's y-axis.
- From -Near to -Far along the camera's z-axis.

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
"""
class Camera(Protocol):
  ...

class Camera2d(Camera):
  ...

class Camera3d(Camera):
  ...