
from array import array as create_array
from array import ArrayType
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from operator import mul
from functools import reduce
from math import cos, radians, sin
from typing import Generic, Self, assert_never, cast

import wgpu

from agents_playground.core.types import NumericType
from agents_playground.fp import Maybe, Nothing, Something
from agents_playground.spatial.coordinate import d, f
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder
from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4, m4
from agents_playground.spatial.transformation.pipeline import TransformationPipeline
from agents_playground.spatial.types import Degrees
from agents_playground.spatial.vector import vector
from agents_playground.spatial.vector.vector import Vector

"""
I need Matrix -> Buffer.

There are a few steps.
0. Create the array that will fill the buffer.
model_world_transform_data = create_array('f', matrix.flatten(MatrixOrder.Row))

1. Create an empty buffer.
device: wgpu.GPUDevice
model_to_world_buffer: wgpu.GPUDevice = device.create_buffer(
  label = 'Model Transform Buffer',
  size = 4 * 16,
  usage = wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST # type: ignore
)

2. Create the bind group for the buffer.
bind_group_layout: GPUBindGroupLayout
bind_group: wgpu.GPUBindGroup = device.create_bind_group(
  label   = 'Camera Bind Group',
  layout  = bind_group_layout,
  entries = [
    {
      'binding': 0,
      'resource': {
        'buffer': model_to_world_buffer,
        'offset': 0,
        'size': model_to_world_buffer.size
      }
    }
  ]
)

4. Write the data into the buffer and place it on the GPUQueue.
queue.write_buffer(model_to_world_buffer, 0, model_world_transform_data)
"""

@dataclass
class TransformationConfiguration:
    """
    A collection of vectors that are used to build a transformation pipeline.

    Attributes:
      translation: Three member list that specifies the distance along the three axes to move the item.
      rotation: Three member list of angles in degrees that specifies the amount to rotate around the axes.
      scale: Three member list of floats that specify the amount to scale along each axis.
      transformation_data: The transformation matrix resulting from multiplying T*R*S.
      transformation_buffer: The GPUBuffer to hold the transformation data.
    """

    # These attributes are intended to be loaded from Scene files.
    translation: list[float]
    rotation: list[float]
    scale: list[float]

    # These attributes are used by per frame processing.
    transformation_data: Maybe[ArrayType] = Nothing()
    transformation_buffer: Maybe[wgpu.GPUBuffer] = Nothing()

    def transform(self) -> None:
        """
        Creates a transformation pipeline to build a matrix from the various
        transformations and then stores it in the transformation_data.
        """
        tp = TransformationPipeline()
        if len(self.translation) == 3:
            tp.translate(vector(*self.translation))

        if len(self.rotation) == 3:
            self._create_rotation_transforms(tp)

        if len(self.scale) == 3:
            self._create_scale_transforms(tp)

        m = tp.transform()
        self.transformation_data = Something(
            create_array("f", m.flatten(MatrixOrder.Row))
        )

    def _create_rotation_transforms(self, tp: TransformationPipeline) -> None:
        if self.rotation[0] != 0:
            tp.rotate_around_x(self.rotation[0])

        if self.rotation[1] != 0:
            tp.rotate_around_y(self.rotation[1])

        if self.rotation[2] != 0:
            tp.rotate_around_z(self.rotation[2])

    def _create_scale_transforms(self, tp: TransformationPipeline) -> None:
        if self.scale[0] != 1 or self.scale[1] != 1 or self.scale[2] != 1:
            tp.scale(vector(*self.scale))