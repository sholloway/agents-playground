from functools import partial
from math import radians
import os
from pathlib import Path

import wgpu
import wgpu.backends.wgpu_native
from wgpu.gui.wx import WgpuWidget

from agents_playground.cameras.camera import Camera, Camera3d
from agents_playground.gpu.per_frame_data import PerFrameData
from agents_playground.gpu.pipelines.web_gpu_pipeline import WebGpuPipeline
from agents_playground.gpu.renderer_builders.simple_renderer_builder import assemble_camera_data
from agents_playground.gpu.renderers.gpu_renderer import GPURenderer
from agents_playground.gpu.renderers.simple_renderer import SimpleRenderer
from agents_playground.loaders.obj_loader import Obj, ObjLoader

from agents_playground.spatial.matrix.matrix4x4 import Matrix4x4
from agents_playground.spatial.mesh import MeshBuffer
from agents_playground.spatial.mesh.triangle_mesh import TriangleMesh
from agents_playground.spatial.vector.vector3d import Vector3d

def update_uniforms(
  device: wgpu.GPUDevice, 
  camera_buffer: wgpu.GPUBuffer, 
  camera: Camera3d) -> None:
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(camera_buffer, 0, camera_data)
  
def draw_frame(
  camera: Camera,
  canvas: WgpuWidget, 
  device: wgpu.GPUDevice,
  renderer: GPURenderer,
  frame_data: PerFrameData
):
  canvas_width, canvas_height = canvas.GetSize()
  aspect_ratio: float = canvas_width/canvas_height

  canvas_context: wgpu.GPUCanvasContext = canvas.get_context()
  current_texture: wgpu.GPUTexture = canvas_context.get_current_texture()

  camera.projection_matrix = Matrix4x4.perspective(
      aspect_ratio= aspect_ratio, 
      v_fov = radians(72.0), 
      near = 0.1, 
      far = 100.0
    )
  camera_data = assemble_camera_data(camera)
  device.queue.write_buffer(frame_data.camera_buffer, 0, camera_data)
  
  # struct.RenderPassColorAttachment
  color_attachment = {
    "view": current_texture.create_view(),
    "resolve_target": None,
    # "clear_value": (0.5, 0.5, 0.5, 1),  # Clear to Gray.
    "clear_value": (0.9, 0.5, 0.5, 1),    # Clear to pink.
    "load_op": wgpu.LoadOp.clear,         # type: ignore
    "store_op": wgpu.StoreOp.store        # type: ignore
  }

  # Create a depth texture for the Z-Buffer.
  depth_texture: wgpu.GPUTexture = device.create_texture(
    label  = 'Z Buffer Texture',
    size   = [canvas_width, canvas_height, 1], 
    usage  = wgpu.TextureUsage.RENDER_ATTACHMENT, # type: ignore
    format = wgpu.enums.TextureFormat.depth24plus_stencil8 # type: ignore
  )
  depth_texture_view = depth_texture.create_view()

  depth_attachment = {
    "view": depth_texture_view,
    "depth_clear_value": 1.0,
    "depth_load_op": wgpu.LoadOp.clear,    # type: ignore
    "depth_store_op":  wgpu.StoreOp.store, # type: ignore
    "depth_read_only":  False,
    
    # I'm not sure about these values.
    "stencil_clear_value": 0,
    "stencil_load_op": wgpu.LoadOp.load,   # type: ignore
    "stencil_store_op": wgpu.StoreOp.store, # type: ignore
    "stencil_read_only": False,
  }

  command_encoder: wgpu.GPUCommandEncoder = device.create_command_encoder()

  # The first command to encode is the instruction to do a 
  # rendering pass.
  pass_encoder: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
    color_attachments         = [color_attachment],
    depth_stencil_attachment  = depth_attachment
  )

  pass_encoder.set_pipeline(frame_data.landscape_render_pipeline)
  renderer.render(pass_encoder, frame_data)

  pass_encoder.end()
  device.queue.submit([command_encoder.finish()])
  
class ObjPipeline(WebGpuPipeline):
  """
  Establishes a GPU rendering pipeline for visualizing an OBJ model.
  """
  def __init__(self) -> None:
    super().__init__()

  def initialize_pipeline(self, canvas: WgpuWidget) -> None:
    # Initialize WebGPU
    adapter: wgpu.GPUAdapter = self._provision_adapter(canvas)
    device: wgpu.GPUDevice = self._provision_gpu_device(adapter)
    canvas_context: wgpu.GPUCanvasContext = canvas.get_context()

    # Set the GPUCanvasConfiguration to control how drawing is done.
    render_texture_format = canvas_context.get_preferred_format(device.adapter)
    canvas_context.configure(
      device       = device, 
      usage        = wgpu.flags.TextureUsage.RENDER_ATTACHMENT, # type: ignore
      format       = render_texture_format,
      view_formats = [],
      color_space  = 'bgra8unorm-srgb', #'srgb',
      alpha_mode   = 'opaque'
    )

    # Load the 3D mesh into memory
    model_file_path = self._select_model()
    model_data: Obj = self._parse_model_file(model_file_path)
    mesh = TriangleMesh.from_obj(model_data)

    # Setup the Camera
    canvas_width, canvas_height = canvas.get_physical_size()
    aspect_ratio = canvas_width/canvas_height

    self._camera = Camera3d.look_at(
      position = Vector3d(3, 2, 4),
      target   = Vector3d(0, 0, 0),
      projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = radians(72.0), 
        near = 0.1, 
        far = 100.0
      ),
    )

    # Setup the Transformation Model.
    model_world_transform = Matrix4x4.identity()

    # Create a depth texture for the Z-Buffer.
    # depth_texture: wgpu.GPUTexture = device.create_texture(
    #   label  = 'Z Buffer Texture',
    #   size   = [canvas_width, canvas_height, 1], 
    #   usage  = wgpu.TextureUsage.RENDER_ATTACHMENT, # type: ignore
    #   format = wgpu.enums.TextureFormat.depth24plus_stencil8 # type: ignore
    # )

    # depth_texture_view = depth_texture.create_view()

    # Setup the Renderer
    renderer: GPURenderer = SimpleRenderer()

    # Prepare the per-frame data.
    frame_data: PerFrameData = renderer.prepare(
      device, 
      render_texture_format, 
      mesh,
      self._camera,
      model_world_transform
    )

    # Bind functions to key data structures.
    # self._bound_update_camera = partial(update_camera, cast(Camera3d,camera))
    self._bound_update_uniforms = partial(update_uniforms, device, frame_data.camera_buffer, self._camera) # type: ignore
    self._bound_draw_frame = partial(draw_frame, self._camera, canvas, device, renderer, frame_data)
    
    canvas.request_draw(self._bound_draw_frame)

  def refresh_aspect_ratio(self, aspect_ratio: float) -> None:
    self._camera.projection_matrix = Matrix4x4.perspective(
        aspect_ratio= aspect_ratio, 
        v_fov = radians(72.0), 
        near = 0.1, 
        far = 100.0
      )
    self._bound_update_uniforms()

  def _provision_adapter(self, canvas: wgpu.gui.WgpuCanvasInterface) -> wgpu.GPUAdapter:
    """
    Create a high performance GPUAdapter for a Canvas.
    """
    return wgpu.gpu.request_adapter( # type: ignore
      canvas=canvas, 
      power_preference='high-performance'
    ) 

  def _provision_gpu_device(self, adapter: wgpu.GPUAdapter) -> wgpu.GPUDevice:
    """
    Get an instance of the GPUDevice that is associated with a 
    provided GPUAdapter.
    """
    return adapter.request_device(
      label='only-gpu-device', 
      required_features=[],
      required_limits={}, 
      default_queue={}
    )
  
  def _select_model(self) -> str:
    """
    Find the path for the desired scene.
    """
    scene_dir = 'poc/pyside_webgpu/pyside_webgpu/demos/obj/models'
    scene_filename = 'skull.obj'
    return os.path.join(Path.cwd(), scene_dir, scene_filename)
  
  def _parse_model_file(self, scene_file_path: str) -> Obj:
    return ObjLoader().load(scene_file_path)
  
  @property
  def mesh(self) -> MeshBuffer:
    raise NotImplemented()
  
  @mesh.setter
  def mesh(self, other: MeshBuffer) -> None:
    raise NotImplemented()
