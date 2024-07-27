import wgpu
import wgpu.backends.wgpu_native


class NormalsShaderConfigurationBuilder:
    def configure_fragment_shader(
        self, render_texture_format: str, shader: wgpu.GPUShaderModule
    ) -> dict:
        """
        Returns a structs.FragmentState.
        """
        fragment_config = {
            "module": shader,
            "entry_point": "fs_main",
            "targets": [{"format": render_texture_format}],
        }
        return fragment_config

    def configure_vertex_shader(self, shader: wgpu.GPUShaderModule) -> dict:
        """
        Returns a structs.VertexState.
        """
        vertex_config = {
            "module": shader,
            "entry_point": "vs_main",
            "constants": {},
            "buffers": [  # structs.VertexBufferLayout
                {
                    "array_stride": 4 * 4,  # Position (x,y,z,w)
                    "step_mode": wgpu.VertexStepMode.vertex,  # type: ignore
                    "attributes": [  # structs.VertexAttribute
                        {
                            "shader_location": 0,
                            "format": wgpu.VertexFormat.float32x4,  # type: ignore
                            "offset": 0,
                        }
                    ],
                }
            ],
        }
        return vertex_config
