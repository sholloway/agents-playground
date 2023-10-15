import wgpu

class ShaderConfigurationBuilder:
  def configure_fragment_shader(self, render_texture_format, white_model_shader):
    """
    Returns a structs.FragmentState.
    """
    fragment_config = {
      "module": white_model_shader,
      "entry_point": "fs_main",
      "targets": [
        {
          "format": render_texture_format
        }
      ]
    }
    return fragment_config

  def configure_vertex_shader(self, white_model_shader):
    """
    Returns a structs.VertexState.
    """
    vertex_config = {
      "module": white_model_shader,
      "entry_point": "vs_main",
      "constants": {},
      "buffers": [ # structs.VertexBufferLayout
        {
          'array_stride': 4 * 4 + 4*3 + 4*3,       # Position (x,y,z,w), Texture (u,v,w), Normal(i,j,k)
          'step_mode': wgpu.VertexStepMode.vertex, # type: ignore
          'attributes': [                          # structs.VertexAttribute
            {
              'shader_location': 0,
              'format': wgpu.VertexFormat.float32x4, # type: ignore This is of the form: x,y,z,w
              'offset': 0
            },
            {
              'shader_location': 1,
              'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: u, v, w
              'offset': 4 * 4 
            },
            {
              'shader_location': 2,
              'format': wgpu.VertexFormat.float32x3, # type: ignore This is of the form: i,j,k
              'offset': 4 * 4 + 4*3
            },
          ]
        }
      ],
    }
    return vertex_config