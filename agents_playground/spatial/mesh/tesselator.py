
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.mesh import Mesh


class Tesselator:
  """Given a spatial object, tesselates the object into triangles."""
  @staticmethod
  def from_landscape(landscape: Landscape) -> Mesh:
    """
    Tesselates a landscape object.
    Args:
      - landscape: The landscape to convert into triangles.
    """
    
    