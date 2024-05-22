from math import radians
from agents_playground.cameras.camera import Camera3d
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.vector.vector3d import Vector3d
from agents_playground.spatial.vector.vector4d import Vector4d


def in_range(value: float, lower: float, upper: float) -> bool:
    return lower <= value and value <= upper

"""
TODO
- Go back to basics. Verify the matrix math and dot product for Vector4d and Matrix4d
  Thoughts:
    - Transition the spatial mathematics to use a rational data type (e.g. Python Fraction class.)
    - Use the TransformationPipeline class to enable chaining matrix together to optimize when 
      rounding is performed.

    t = TransformationPipeline()
    transformation = t.mul(projection_matrix).mul(view_matrix).mul(world_matrix)t.transform()
    vertex_in_clip_space = transformation * vertex_in_model_space

- Change the camera to use a Coordinate value for position and target. Right now it's
  using vectors and that doesn't make sense.
- May be an issue of right hand vs left hand coordinate systems.

"""
class TestCamera3d:
    def test_look_at(self) -> None:
        position = Vector3d(1, 1, 1)
        target = Vector3d(0, 0, 0)

        camera = Camera3d.look_at(
            position,
            target,
            near_plane=0.1,
            far_plane=100,
            vertical_fov=72,
            aspect_ratio="16:9",
        )

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
        assert view_matrix[11] == -1.732051
        assert view_matrix[12] == 0
        assert view_matrix[13] == 0
        assert view_matrix[14] == 0
        assert view_matrix[15] == 1

    def test_render_pipeline(self) -> None:
        # To render a primitive it must go through a series of transformations.
        # These are done on the GPU. This test is to verify that the matrices are
        # constructed correctly.

        camera = Camera3d.look_at(
            position=Vector3d(-5, 5, -5),
            target=Vector3d(0, 0, 0), 
            near_plane=0.1,
            far_plane=100,
            vertical_fov=72.0,
            aspect_ratio="4:3",
        )

        # The look_at will calculate a new up, facing, right vector.
        # assert camera.position == Vector3d(-5, 0, 0)
        # assert camera.facing == Vector3d(-1, 0, 0)
        # assert camera.up == Vector3d(0, 1, 0)
        # assert camera.right == Vector3d(0, 0, 1)

        # The vertex to be projected onto the clipping coordinate space.
        # In model coordinates.
        vertex = Vector4d(0, 0, 0, 1)

        # The world matrix shouldn't change anything since it's the identity matrix.
        # In this scenario, we're not moving the model.
        # Translates/Scales/Rotates the model to be how we want it in the scene.
        world_matrix: Matrix[float] = Matrix4x4.identity()
        world_space: Vector4d = world_matrix * vertex  # type: ignore
        assert world_space == vertex

        # Clip space is a 3D cube of the dimensions ([-1,1], [-1,1], [0,1])
        view_matrix = camera.view_matrix.transpose()
        projection_matrix = camera.projection_matrix.transpose()

        # TODO: The below is just for debugging. Remove when fixed.
        step1 = world_matrix * vertex  # type: ignore
        step2 = view_matrix * step1
        step3: Vector4d = projection_matrix * step2

        clip_space: Vector4d = projection_matrix * view_matrix * world_matrix * vertex  # type: ignore
        """
        BUG: The way I'm thinking about Clip space is wrong. 
        Per: https://carmencincotti.com/2022-05-02/homogeneous-coordinates-clip-space-ndc/
        Every vertex (x, y, z, w) has it's own clip space in which it exists. 
        Where:
            -w <= x <= w
            -w <= y <= w
            0 <=z <= w

        The value of w can be different for each vertex after going through the 
        transformation:
        out.position = projectionMatrix * viewMatrix * modelMatrix * inputModelSpacePosition

        The Normalized Device Coordinates is when the X,Y,Z coordinates are all divided 
        by the W coordinate. The GPU does this for us.
        """

        # assert step3.i == clip_space.i
        # assert step3.j == clip_space.j
        # assert step3.k == clip_space.k
        # assert step3.w == clip_space.w
        
        # Assert the transformed vertex is visible in the clip space cube.
        assert in_range(
            clip_space.i, -clip_space.w, clip_space.w
        ), f"Expected i to be in the range [{-clip_space.w}, {clip_space.w}]"

        assert in_range(
            clip_space.j, -clip_space.w, clip_space.w
        ), f"Expected j to be in the range [{-clip_space.w}, {clip_space.w}]"

        assert in_range(
            clip_space.k, 0, clip_space.w
        ), f"Expected k to be in the range [0, {clip_space.w}]"
