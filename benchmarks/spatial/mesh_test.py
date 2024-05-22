import os
from pathlib import Path

import pytest

from agents_playground.loaders.obj_loader import Obj, ObjLoader
from agents_playground.spatial.mesh import MeshLike
from agents_playground.spatial.mesh.half_edge_mesh import obj_to_mesh


@pytest.fixture
def obj_skull_model() -> Obj:
    scene_dir = "poc/pyside_webgpu/pyside_webgpu/demos/obj/models"
    scene_filename = "skull.obj"
    path = os.path.join(Path.cwd(), scene_dir, scene_filename)
    return ObjLoader().load(path)


class TestMeshPerformance:
    @pytest.mark.benchmark(group="Half-edge Mesh Performance", disable_gc=True)
    def test_load_skull(self, benchmark, obj_skull_model) -> None:
        benchmark(obj_to_mesh, obj_skull_model)
