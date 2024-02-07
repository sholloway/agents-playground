from typing import Callable
import pytest
from agents_playground.counter.counter import Counter, CounterBuilder

from agents_playground.fp import Nothing
from agents_playground.spatial.coordinate import Coordinate
from agents_playground.spatial.landscape import Landscape
from agents_playground.spatial.landscape.constants import STANDARD_GRAVITY_IN_METRIC
from agents_playground.spatial.landscape.landscape_characteristics import LandscapeCharacteristics
from agents_playground.spatial.landscape.landscape_physicality import LandscapePhysicality
from agents_playground.spatial.landscape.tile import Tile, TileCubicPlacement, TileCubicVerticesPlacement
from agents_playground.spatial.landscape.types import LandscapeGravityUOM, LandscapeMeshType
from agents_playground.spatial.mesh.tesselator import Mesh, MeshException, MeshFace, MeshGraphVizPrinter, MeshHalfEdge, MeshVertex, MeshWindingDirection
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.uom import LengthUOM, SystemOfMeasurement

class TestTesselator:
  pass
