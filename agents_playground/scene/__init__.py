from dataclasses import dataclass

from agents_playground.cameras.camera import Camera
from agents_playground.spatial.landscape import Landscape

@dataclass
class Scene:
  camera: Camera
  landscape: Landscape 
  # Note: The scene needs some way to specify how to T/S/R the landscape.
  # Note: The scene needs some way to specify the UOM of world coordinates.

from . import *