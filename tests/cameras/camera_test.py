
from agents_playground.cameras.camera import Camera3d
from agents_playground.spatial.matrix import MatrixOrder
from agents_playground.spatial.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector3d import Vector3d


class TestCamera3d:
  def test_look_at(self) -> None:
    up = Vector3d(0, 1, 0)
    position = Vector3d(1, 1, 1)
    target = Vector3d(0, 0, 0)
    camera = Camera3d.look_at(position,up,target, Matrix4x4.identity())
    
    view_matrix = camera.to_view_matrix().transpose().flatten(MatrixOrder.Row)
    round_it = lambda i: round(i, 6)
    view_matrix = list(map(round_it, view_matrix))
    assert view_matrix[0] == 0.707107
    assert view_matrix[1] == 0
    assert view_matrix[2] == -0.707107
    assert view_matrix[3] == 0
    assert view_matrix[4] == -0.408248
    assert view_matrix[5] == 0.816497
    assert view_matrix[6] == -0.408248
    assert view_matrix[7] == 0
    assert view_matrix[8] == 0.57735
    assert view_matrix[9] == 0.57735
    assert view_matrix[10] == 0.57735
    assert view_matrix[11] == 0
    assert view_matrix[12] == 1
    assert view_matrix[13] == 1
    assert view_matrix[14] == 1
    assert view_matrix[15] == 1