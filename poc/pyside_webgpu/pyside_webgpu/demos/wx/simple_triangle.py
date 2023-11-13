
import wx
from .wx_patch import WgpuWidget
import wgpu
import wgpu.backends.rs

triangle_shader = """
struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};

struct VertexOutput {
    @location(0) color : vec4<f32>,
    @builtin(position) pos: vec4<f32>,
};

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    var positions = array<vec2<f32>, 3>(
        vec2<f32>(0.0, -0.5),
        vec2<f32>(0.5, 0.5),
        vec2<f32>(-0.5, 0.75),
    );
    var colors = array<vec3<f32>, 3>(  // srgb colors
        vec3<f32>(1.0, 1.0, 0.0),
        vec3<f32>(1.0, 0.0, 1.0),
        vec3<f32>(0.0, 1.0, 1.0),
    );
    let index = i32(in.vertex_index);
    var out: VertexOutput;
    out.pos = vec4<f32>(positions[index], 0.0, 1.0);
    out.color = vec4<f32>(colors[index], 1.0);
    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
    let physical_color = pow(in.color.rgb, vec3<f32>(2.2));  // gamma correct
    return vec4<f32>(physical_color, in.color.a);
}
"""

class TopWindow(wx.Frame):
  def __init__(self) -> None:
    super().__init__(None, title="WX App")
    self.SetSize(640, 480)

    splitter = wx.SplitterWindow(self)

    self.button = wx.Button(self, -1, "Hello world")
    self.canvas1 = WgpuWidget(splitter)
    self.canvas2 = WgpuWidget(splitter)

    splitter.SplitVertically(self.canvas1, self.canvas2)
    splitter.SetSashGravity(0.5)

    sizer = wx.BoxSizer(wx.HORIZONTAL)
    sizer.Add(self.button, 0, wx.EXPAND)
    sizer.Add(splitter, 1, wx.EXPAND)
    self.SetSizer(sizer)

    self.Show()

def initialize_canvas(canvas, power_preference="high-performance", limits=None):
  """Setup rendering on a given canvas."""
  adapter: wgpu.GPUAdapter = wgpu.request_adapter(canvas=None, power_preference=power_preference) # type: ignore
  device: wgpu.GPUDevice   = adapter.request_device(required_limits=limits) # type: ignore
  return _setup_rendering_pipeline(canvas, device)

def _setup_rendering_pipeline(canvas, device):
  shader: wgpu.GPUShaderModule = device.create_shader_module(code=triangle_shader)

  # No bind group and layout, we should not create empty ones.
  pipeline_layout: wgpu.GPUPipelineLayout = device.create_pipeline_layout(bind_group_layouts=[])

  present_context: wgpu.GPUCanvasContext = canvas.get_context()
  render_texture_format = present_context.get_preferred_format(device.adapter)
  present_context.configure(device=device, format=render_texture_format)

  # structs.PrimitiveState
  # Specify what type of geometry should the GPU render.
  primitive_config={
    "topology": wgpu.PrimitiveTopology.triangle_list,
    "front_face": wgpu.FrontFace.ccw,
    "cull_mode": wgpu.CullMode.none,
  }

  # structs.VertexState
  # Configure the vertex shader.
  vertex_config = {
    "module": shader,
    "entry_point": "vs_main",
    "buffers": [],
  }

  # structs.FragmentState
  # Configure the fragment shader.
  fragment_config = {
    "module": shader,
    "entry_point": "fs_main",
    "targets": [
      {
        "format": render_texture_format,
        "blend": {
          "color": (
            wgpu.BlendFactor.one,
            wgpu.BlendFactor.zero,
            wgpu.BlendOperation.add
          ),
          "alpha": (
            wgpu.BlendFactor.one,
            wgpu.BlendFactor.zero,
            wgpu.BlendOperation.add
          )
        }
      }
    ]
  }

  render_pipeline = device.create_render_pipeline(
    label         = 'Rendering Pipeline', 
    layout        = pipeline_layout,
    primitive     = primitive_config,
    vertex        = vertex_config,
    fragment      = fragment_config,
    depth_stencil = None,
    multisample   = None
  )

  def draw_frame():
    current_texture_view: wgpu.GPUCanvasContext = present_context.get_current_texture()
    command_encoder = device.create_command_encoder()

    # The first command to encode is the instruction to do a 
    # rendering pass.
    render_pass: wgpu.GPURenderPassEncoder = command_encoder.begin_render_pass(
      color_attachments=[
        {
          "view": current_texture_view,
          "resolve_target": None,
          "clear_value": (0, 0, 0, 1),
          "load_op": wgpu.LoadOp.clear,
          "store_op": wgpu.StoreOp.store
        }
      ],
    )

    # Associate the render pipeline with the GPURenderPassEncoder.
    render_pass.set_pipeline(render_pipeline)
    
    # Draw primitives based on the vertex buffers. 
    render_pass.draw(
      vertex_count = 3, 
      instance_count = 1, 
      first_vertex = 0, 
      first_instance = 0)
    
    render_pass.end()
    device.queue.submit([command_encoder.finish()])

  canvas.request_draw(draw_frame)
  return device
  
def build_app():
  wgpu.GPUAdapter
  app = wx.App()
  top_window = TopWindow()
  initialize_canvas(top_window.canvas1)
  initialize_canvas(top_window.canvas2)
  app.MainLoop()