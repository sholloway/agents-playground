
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

"""
class Camera(Protocol):
  ...

class Camera2d(Camera):
  ...

class Camera3d(Camera):
  ...