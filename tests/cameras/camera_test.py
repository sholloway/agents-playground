
from math import radians
from agents_playground.cameras.camera import Camera3d
from agents_playground.spatial.matrix import MatrixOrder
from agents_playground.spatial.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector3d import Vector3d
from agents_playground.spatial.vector4d import Vector4d

def in_range(value: float, lower: float, upper: float) -> bool:
  return lower <= value and value <= upper

class TestCamera3d:
  def test_look_at(self) -> None:
    up = Vector3d(0, 1, 0)
    position = Vector3d(1, 1, 1)
    target = Vector3d(0, 0, 0)
    camera = Camera3d.look_at(position,up,target, Matrix4x4.identity())

    view_matrix = camera.view_matrix.transpose().flatten(MatrixOrder.Row)
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

  def test_render_pipeline(self) -> None:
    # To render a primitive it must go through a series of transformations.
    # These are done on the GPU. This test is to verify that the matrices are 
    # actually constructed correctly.

    up = Vector3d(0, 1, 0)
    position = Vector3d(1, 1, 1)
    target = Vector3d(0, 0, 0)
    fov = radians(72.0)
    aspect_ratio = 1000.0/800.0 # width/height
    near = 1.0
    far = 1000.0

    camera = Camera3d.look_at(position,up,target, Matrix4x4.perspective(aspect_ratio, fov, near, far))

    # The vertex to be projected onto the clipping coordinate space.
    vertex = Vector4d(-0.500000, 0.500000, -0.500000, 1)

    world_matrix = Matrix4x4.identity()

    # The world matrix shouldn't change anything since it's the identity matrix.
    world_space: Vector4d = world_matrix * vertex # type: ignore
    assert world_space == vertex 

    # Camera space...
    camera_space = camera.view_matrix.transpose() * world_matrix * vertex # type: ignore
    # I need a good example here. I'm not sure what to assert...

    # clip_space: Vector4d = camera.projection_matrix.transpose() * camera.view_matrix.transpose() * world_matrix * vertex # type: ignore
    clip_space: Vector4d = camera.projection_matrix.transpose() * world_matrix * vertex # type: ignore
    assert in_range(clip_space.i, -1, 1), "Expected i to be in the range [-1, 1]"
    assert in_range(clip_space.j, -1, 1), "Expected j to be in the range [-1, 1]"
    assert in_range(clip_space.k, 0, 1),  "Expected k to be in the range [0, 1]" # Dot product of (m02, m12, m22, -1) and the vector

    """
    It seems that the projection matrix is projecting everything to less than 0 on the Z axis.

    """

    assert clip_space.w == 1

