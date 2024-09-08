from abc import ABC, abstractmethod
from array import array as create_array
from array import ArrayType

import wgpu
import wgpu.backends.wgpu_native
from agents_playground.cameras.camera import Camera
from agents_playground.fp import Maybe
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration

from agents_playground.simulation.simulation_context_builder import SimulationContextBuilder
from agents_playground.spatial.matrix.matrix import Matrix, MatrixOrder


PROJ_MATRIX_MISSING_ERR = "The projection matrix on the camera was not set."

def assemble_camera_data(camera: Camera) -> ArrayType:
    view_matrix = camera.view_matrix
    maybe_proj_matrix: Maybe[Matrix[float]] = camera.projection_matrix
    proj_matrix: Matrix[float] = maybe_proj_matrix.unwrap_or_throw(
        PROJ_MATRIX_MISSING_ERR
    )
    proj_view: tuple = proj_matrix.transpose().flatten(
        MatrixOrder.Row
    ) + view_matrix.flatten(MatrixOrder.Row)
    return create_array("f", proj_view)


class RenderingPipelineBuilder(ABC):
    """
    Responsible for building a renderer pipeline.
    """

    def __init__(self) -> None:
        super().__init__()
        self._rendering_pipeline: wgpu.GPURenderPipeline

    def build(
        self,
        sim_context_builder: SimulationContextBuilder,
        pc: PipelineConfiguration
    ) -> wgpu.GPURenderPipeline:
        self._load_shaders(sim_context_builder, pc)
        self._build_pipeline_configuration(sim_context_builder, pc)
        self._load_mesh(sim_context_builder, pc)
        self._setup_camera(sim_context_builder, pc)
        self._setup_model_transforms(sim_context_builder, pc)
        self._setup_uniform_bind_groups(sim_context_builder, pc)
        self._rendering_pipeline = self._setup_renderer_pipeline(sim_context_builder, pc)
        self._create_bind_groups(sim_context_builder, pc)
        self._load_uniform_buffers(sim_context_builder, pc)
        return self._rendering_pipeline

    @abstractmethod
    def _load_shaders(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _build_pipeline_configuration(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _load_mesh(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _setup_camera(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _setup_model_transforms(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _setup_uniform_bind_groups(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _setup_renderer_pipeline(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> wgpu.GPURenderPipeline: ...

    @abstractmethod
    def _create_bind_groups(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...

    @abstractmethod
    def _load_uniform_buffers(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None: ...
