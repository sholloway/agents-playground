from dataclasses import dataclass

from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.matrix.matrix import Matrix
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.vector import vector
from agents_playground.spatial.vector.vector import Vector


@dataclass
class Transformation:
  """Convenance class for working with Affine Transformations.

  Attributes:
    translation: A vector to translate by.
    rotation: A vector to rotate by.
    scale: A vector to scale along.

  Supports being loaded from a JSON file as part of the Scene loading process.
  """
  translation: Maybe[Vector] = Nothing()
  rotation: Maybe[Vector] = Nothing()
  scale: Maybe[Vector] = Nothing()
  shear: Maybe[Vector] = Nothing()

  def __post_init__(self) -> None:
    if isinstance(self.translation, list):
      self.translation = Something(vector(*self.translation))

    if isinstance(self.rotation, list):
      self.rotation = Something(vector(*self.rotation))
  
    if isinstance(self.scale, list):
      self.scale = Something(vector(*self.scale))

  # def transform(self) -> Matrix:
  #   """ Returns the transformation matrix.
  #   """

  def translate(self) -> Matrix:
    """Returns the translation Matrix.
    """
    if not self.translation.is_something():
      return Matrix4x4.identity()
    
    translation = self.translation.unwrap()
    return m4(
      1, 0, 0, translation.i,
      0, 1, 0, translation.j,
      0, 0, 1, translation.k,
      0, 0, 0, 1
    )
 
    

  # def rotate(self) -> Matrix:
  #   """Returns the rotation matrix.
  #   """
  #   return m4()
    
  
  # def scale(self) -> Matrix:
  #   """Returns the scaling matrix.
  #   """
  #   return m4()