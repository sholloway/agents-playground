import wgpu

class ShaderConfigurationBuilder:
  def configure_fragment_shader(self, render_texture_format, shader):
    """
    Returns a structs.FragmentState.
    """
    fragment_config = {
      "module": shader,
      "entry_point": "fs_main",
      "targets": [
        {
          "format": render_texture_format
        }
      ]
    }
    return fragment_config

  def configure_vertex_shader(self, shader):
    """
    Returns a structs.VertexState.
    """
    vertex_config = {
      "module": shader,
      "entry_point": "vs_main",
      "constants": {},
      "buffers": [ # structs.VertexBufferLayout
        { # The buffer for the vertex.
          'array_stride': 4 * 4,                   # sizeof(float) * 4
          'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
          'attributes': [                          # structs.VertexAttribute
            {
              'shader_location': 0,
              'format': wgpu.VertexFormat.float32x4, # type: ignore This is of the form: x,y,z,w
              'offset': 0
            }
          ]
        },
        { # The buffer for the vertex normal.
          'array_stride': 4 * 3,                   # sizeof(float) * 3
          'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
          'attributes': [                          # structs.VertexAttribute
            {
              'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: i, j, k
              'offset': 0,
              'shader_location': 1
            }
          ]
        }
      ],
    }
    return vertex_config