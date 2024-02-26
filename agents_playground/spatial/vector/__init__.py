from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.vector.vector import Vector
from agents_playground.spatial.vector.vector2d import Vector2d
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.spatial.vector.vector4d import Vector4d

def vector(*args) -> Vector:
  """Given a set of arguments, create a vector of the appropriate size."""
  match len(args):
    case 2:
      return Vector2d(*args)
    case 3:
      return Vector3d(*args)
    case 4:
      return Vector4d(*args)
    case _:
      raise NotImplementedError(f'Cannot create a vector with {len(args)} dimensions.')
    
def vector_from_points(start_point: Coordinate, end_point: Coordinate) -> Vector:
  """Create a new vector from two points
  The direction of the vector is defined by end_point - start_point.

  Note:
  In the case of Coordinates that have 4 dimensions a Vector3d is returned.
  """
  diff: Coordinate = end_point - start_point
  return vector(*diff.to_tuple()[0:3])