from array import array as create_array
import os
from pathlib import Path

import wgpu
import wgpu.backends.wgpu_native

from agents_playground.fp import Something
from agents_playground.gpu.camera_configuration.camera_configuration_builder import (
    CameraConfigurationBuilder,
)
from agents_playground.gpu.mesh_configuration.builders.triangle_list_mesh_configuration_builder import (
    TriangleListMeshConfigurationBuilder,
)
from agents_playground.gpu.pipelines.pipeline_configuration import PipelineConfiguration
from agents_playground.gpu.renderer_builders.renderer_builder import (
    RenderingPipelineBuilder,
    assemble_camera_data,
)
from agents_playground.gpu.shader_configuration.default_shader_configuration_builder import (
    DefaultShaderConfigurationBuilder,
)
from agents_playground.gpu.shaders import load_shader
from agents_playground.simulation.simulation_context_builder import SimulationContextBuilder
from agents_playground.spatial.mesh import MeshBuffer



class LandscapeRendererBuilder(RenderingPipelineBuilder):
    def __init__(self) -> None:
        super().__init__()
        self._camera_config = CameraConfigurationBuilder()
        self._shader_config = DefaultShaderConfigurationBuilder()
        self._mesh_config = TriangleListMeshConfigurationBuilder("Landscape")

    def _load_shaders(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        shader_path = os.path.join(
            Path.cwd(), "agents_playground/gpu/shaders/landscape.wgsl"
        )
        pc.shader = load_shader(shader_path, "Triangle Shader", sim_context_builder.device)

    def _build_pipeline_configuration(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        pc.primitive_config = self._mesh_config.configure_pipeline_primitives()
        pc.vertex_config = self._shader_config.configure_vertex_shader(pc.shader)
        pc.fragment_config = self._shader_config.configure_fragment_shader(
            sim_context_builder.render_texture_format, pc.shader
        )

    def _load_mesh(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        # Load the 3D mesh into a GPUVertexBuffer.
        vertex_buffer: MeshBuffer = sim_context_builder.mesh_registry["landscape_tri_mesh"].vertex_buffer.unwrap()
        vertex_buffer.vbo = self._mesh_config.create_vertex_buffer(
            sim_context_builder.device, 
            vertex_buffer.data
        )
        vertex_buffer.ibo = self._mesh_config.create_index_buffer(
            sim_context_builder.device, 
            vertex_buffer.index
        )

    def _setup_camera(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        pc.camera_data = assemble_camera_data(sim_context_builder.scene.camera)
        if 'camera' not in sim_context_builder.uniforms:
            camera_buffer: wgpu.GPUBuffer = self._camera_config.create_camera_buffer(
                sim_context_builder.device, 
                sim_context_builder.scene.camera
            )
            sim_context_builder.uniforms.register('camera', buffer=camera_buffer)

    def _setup_model_transforms(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        sim_context_builder.scene.landscape_transformation.transformation_buffer = Something(
            sim_context_builder.device.create_buffer(
                label="Landscape Model Transform Buffer",
                size=4 * 16,
                usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
            )
        )

    def _setup_uniform_bind_groups(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        # Set up the bind group layout for the uniforms.
        pc.camera_uniform_bind_group_layout = (
            self._camera_config.create_camera_ubg_layout(sim_context_builder.device)
        )

        pc.model_uniform_bind_group_layout = (
            self._camera_config.create_model_ubg_layout(sim_context_builder.device)
        )

        pc.display_config_bind_group_layout = sim_context_builder.device.create_bind_group_layout(
            label="Display Configuration Uniform Bind Group Layout",
            entries=[
                {
                    "binding": 0,  # Bind group for the display configuration options.
                    "visibility": wgpu.flags.ShaderStage.VERTEX | wgpu.flags.ShaderStage.FRAGMENT,  # type: ignore
                    "buffer": {"type": wgpu.BufferBindingType.uniform},  # type: ignore
                }
            ],
        )

        display_config_buffer: wgpu.GPUBuffer = sim_context_builder.device.create_buffer(
            label="Display Configuration Buffer",
            size=4,
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,  # type: ignore
        )
        sim_context_builder.uniforms.register('display_configuration', buffer = display_config_buffer)

    def _setup_renderer_pipeline(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> wgpu.GPURenderPipeline:
        pipeline_layout: wgpu.GPUPipelineLayout = sim_context_builder.device.create_pipeline_layout(
            label="Landscape Render Pipeline Layout",
            bind_group_layouts=[
                pc.camera_uniform_bind_group_layout,
                pc.model_uniform_bind_group_layout,
                pc.display_config_bind_group_layout,
            ],
        )

        depth_stencil_config = {
            "format": wgpu.enums.TextureFormat.depth24plus_stencil8,  # type: ignore
            "depth_write_enabled": True,
            "depth_compare": wgpu.enums.CompareFunction.less,  # type: ignore
        }

        return sim_context_builder.device.create_render_pipeline(
            label="Landscape Rendering Pipeline",
            layout=pipeline_layout,
            primitive=pc.primitive_config,
            vertex=pc.vertex_config,
            fragment=pc.fragment_config,
            depth_stencil=depth_stencil_config,
            multisample=None,
        )

    def _create_bind_groups(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        vertex_buffer: MeshBuffer = sim_context_builder.mesh_registry["landscape_tri_mesh"].vertex_buffer.unwrap()

        # frame_data.landscape_camera_bind_group = self._camera_config.create_camera_bind_group(
        vertex_buffer.bind_groups[0] = self._camera_config.create_camera_bind_group(
            sim_context_builder.device, 
            pc.camera_uniform_bind_group_layout, 
            sim_context_builder.uniforms['camera'].buffer.unwrap_or_throw('Buffer not set on camera uniform.')
        )

        vertex_buffer.bind_groups[1] = (
            self._camera_config.create_model_transform_bind_group(
                sim_context_builder.device,
                pc.model_uniform_bind_group_layout,
                sim_context_builder.scene.landscape_transformation.transformation_buffer.unwrap(),
            )
        )

        display_config = sim_context_builder.uniforms['display_configuration']
        display_config_buffer = display_config.buffer.unwrap_or_throw('Buffer on display_configuration was not set.')
        vertex_buffer.bind_groups[2] = sim_context_builder.device.create_bind_group(
            label="Display Configuration Bind Group",
            layout=pc.display_config_bind_group_layout,
            entries=[
                {
                    "binding": 0,
                    "resource": {
                        "buffer": display_config_buffer,
                        "offset": 0,
                        "size": display_config_buffer.size,
                    },
                }
            ],
        )

    def _load_uniform_buffers(
        self, 
        sim_context_builder: SimulationContextBuilder, 
        pc: PipelineConfiguration
    ) -> None:
        queue: wgpu.GPUQueue = sim_context_builder.device.queue
        camera_uniform = sim_context_builder.uniforms['camera']
        camera_uniform_buffer = camera_uniform.buffer.unwrap_or_throw('Buffer on the camera uniform was not set.')
        queue.write_buffer(camera_uniform_buffer, 0, pc.camera_data)
        scene = sim_context_builder.scene

        if not scene.landscape_transformation.transformation_data.is_something():
            scene.landscape_transformation.transform()

        queue.write_buffer(
            scene.landscape_transformation.transformation_buffer.unwrap(),
            0,
            scene.landscape_transformation.transformation_data.unwrap(),
        )

        display_configuration = sim_context_builder.uniforms['display_configuration']
        display_config_buffer = display_configuration.buffer.unwrap_or_throw('Buffer on display_configuration uniform not set.')
        queue.write_buffer(display_config_buffer, 0, create_array("i", [0]))
