import os
from pathlib import Path
from pyside_webgpu.demos.obj.renderers.edge.mesh_configuration_builder import MeshConfigurationBuilder
from pyside_webgpu.demos.obj.renderers.edge.shader_configuration_builder import ShaderConfigurationBuilder
from pyside_webgpu.demos.obj.renderers.frame_data import PerFrameData

from pyside_webgpu.demos.obj.renderers.pipeline_configuration import PipelineConfiguration
from pyside_webgpu.demos.obj.renderers.renderer_builder import RendererBuilder
from pyside_webgpu.demos.obj.utilities import load_shader

import wgpu
import wgpu.backends.rs

from agents_playground.loaders.obj_loader import TriangleMesh

class EdgeRendererConfigurationBuilder(RendererBuilder):
  def __init__(self) -> None:
    super().__init__()
    self._mesh_config = MeshConfigurationBuilder()
    self._shader_config = ShaderConfigurationBuilder()

  def _load_shaders(
    self, 
    device: wgpu.GPUDevice, 
    pc: PipelineConfiguration
  ) -> None:
    shader_path = os.path.join(Path.cwd(), 'poc/pyside_webgpu/pyside_webgpu/demos/obj/shaders/triangle_edge.wgsl')
    pc.shader = load_shader(shader_path, 'Triangle Edge Shader', device)

  def _build_pipeline_configuration(
    self, 
    render_texture_format: str,
    pc: PipelineConfiguration,
  ) -> None:
    pc.primitive_config = self._mesh_config.configure_pipeline_primitives()
    pc.vertex_config = self._shader_config.configure_vertex_shader(pc.shader) 
    pc.fragment_config = self._shader_config.configure_fragment_shader(render_texture_format, pc.shader)

  def _load_mesh(
    self, 
    device: wgpu.GPUDevice, 
    mesh: TriangleMesh, 
    frame_data: PerFrameData
  ) -> None:
    # Load the 3D mesh into a GPUVertexBuffer.
    frame_data.vbo = self._mesh_config.create_vertex_buffer(device, mesh.vertices)

    # I don't kneed the vert normals to draw the edges, but including them to enable doing stuff with them later.
    frame_data.vertex_normals_buffer = self._mesh_config.create_vertex_normals_buffer(device, mesh.vertex_normals)

    # I think the IBO logic probably needs to change to support drawing the edges...
    frame_data.ibo = self._mesh_config.create_index_buffer(device, mesh.triangle_index)
    frame_data.num_triangles = len(mesh.triangle_index)