import os
from pathlib import Path

import pytest

from agents_playground.loaders.obj_loader import Obj, ObjLoader
from agents_playground.spatial.mesh import MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import obj_to_mesh

@pytest.fixture
def obj_skull_model() -> Obj:
  scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
  scene_filename = 'skull.obj'
  path = os.path.join(Path.cwd(), scene_dir, scene_filename)
  return ObjLoader().load(path)

class TestMeshPerformance:
  @pytest.mark.benchmark(group="Half-edge Mesh Performance", disable_gc=True)
  def test_load_skull(self, benchmark, obj_skull_model) -> None:
    benchmark(obj_to_mesh, obj_skull_model)
"""
The performance has gotten a bit worse. 

v0.2.0 with References
------------------------------- benchmark 'Half-edge Mesh Performance': 1 tests -------------------------------
Name (time in ms)         Min     Mean      Max   Median  StdDev     IQR  Outliers      OPS  Rounds  Iterations
---------------------------------------------------------------------------------------------------------------
test_load_skull       51.6856  53.8209  57.0199  53.6151  1.5036  2.0809       4;0  18.5802      19           1
---------------------------------------------------------------------------------------------------------------


This branch using lookups.
------------------------------- benchmark 'Half-edge Mesh Performance': 1 tests -------------------------------
Name (time in ms)         Min     Mean      Max   Median  StdDev     IQR  Outliers      OPS  Rounds  Iterations
---------------------------------------------------------------------------------------------------------------
test_load_skull       79.0780  79.3608  79.8499  79.2980  0.2239  0.1808       3;2  12.6007      13           1
---------------------------------------------------------------------------------------------------------------
"""