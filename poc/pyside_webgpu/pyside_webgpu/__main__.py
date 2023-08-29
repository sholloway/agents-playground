# Note QT needs to be imported before wgpu.
from typing import Optional
from PySide6 import QtWidgets
import PySide6.QtCore
import PySide6.QtWidgets

import wgpu
from wgpu.gui.qt import WgpuWidget

# Load the Rust WGPU backend.
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

class TopWindow(QtWidgets.QWidget):
  def __init__(self) -> None:
    super().__init__()
    self.resize(640, 480)
    self.setWindowTitle('Hello WebGPU!')

    splitter = QtWidgets.QSplitter()
    self.button = QtWidgets.QPushButton("Hello World", self)
    self.canvas1 = WgpuWidget(splitter)
    self.canvas2 = WgpuWidget(splitter)
    
    splitter.addWidget(self.canvas1)
    splitter.addWidget(self.canvas2)

    layout = QtWidgets.QHBoxLayout()
    layout.addWidget(self.button, 0)
    layout.addWidget(splitter, 1)
    self.setLayout(layout)

    self.show()

def initialize_canvas(canvas, power_preference="high-performance", limits=None):
  """Setup rendering on a given canvas."""
  adapter = wgpu.request_adapter(canvas=None, power_preference=power_preference)
  device = adapter.request_device(required_limits=limits)
  return _setup_rendering_pipeline(canvas, device)

def _setup_rendering_pipeline(canvas, device):
  shader = device.create_shader_module(code=triangle_shader)

  # No bind group and layout, we should not create empty ones.
  pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[])

  present_context = canvas.get_context()
  render_texture_format = present_context.get_preferred_format(device.adapter)
  present_context.configure(device=device, format=render_texture_format)

  render_pipeline = device.create_render_pipeline(
    layout=pipeline_layout,
    vertex={
      "module": shader,
      "entry_point": "vs_main",
      "buffers": [],
    },
    primitive={
      "topology": wgpu.PrimitiveTopology.triangle_list,
      "front_face": wgpu.FrontFace.ccw,
      "cull_mode": wgpu.CullMode.none,
    },
    depth_stencil=None,
    multisample=None,
    fragment={
      "module": shader,
      "entry_point": "fs_main",
      "targets": [
        {
          "format": render_texture_format,
          "blend": {
            "color": (
              wgpu.BlendFactor.one,
              wgpu.BlendFactor.zero,
              wgpu.BlendOperation.add,
            ),
            "alpha": (
              wgpu.BlendFactor.one,
              wgpu.BlendFactor.zero,
              wgpu.BlendOperation.add,
            ),
          },
        },
      ],
    },
  )

  def draw_frame():
    current_texture_view = present_context.get_current_texture()
    command_encoder = device.create_command_encoder()

    render_pass = command_encoder.begin_render_pass(
        color_attachments=[
            {
                "view": current_texture_view,
                "resolve_target": None,
                "clear_value": (0, 0, 0, 1),
                "load_op": wgpu.LoadOp.clear,
                "store_op": wgpu.StoreOp.store,
            }
        ],
    )

    render_pass.set_pipeline(render_pipeline)
    # render_pass.set_bind_group(0, no_bind_group, [], 0, 1)
    render_pass.draw(3, 1, 0, 0)
    render_pass.end()
    device.queue.submit([command_encoder.finish()])

  canvas.request_draw(draw_frame)
  return device
  

def build_app():
  app = QtWidgets.QApplication([])
  top_window = TopWindow()
  initialize_canvas(top_window.canvas1)
  initialize_canvas(top_window.canvas2)

  # Enter Qt event loop.
  app.exec()


if __name__ == '__main__':
  build_app()