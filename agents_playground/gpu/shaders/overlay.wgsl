/*
Draw a triangle in screen space and color it a solid color.
*/

struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};

struct VertexOutput {
    @builtin(position) pos: vec4<f32>,
    @location(0) uv : vec2<f32>,
};



@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    /*
    The Quad is mapped to screen space, which is: 
    -1,1-------------------1,1
        |                     |
        |                     |
        |                     |
        |         0,0         |
        |                     |
        |                     |
    -1,-1------------------1,-1    
    */
    // NOTE: At the moment (7/30/24) wgpu isn't allowsing a const array to be index by a var.
    // However the spec does allow this so I assume that will change in a future release.
    // When that happens, move this to be declared at the module level as a constant.
    // Tracking issue at: https://github.com/gfx-rs/wgpu/issues/4337
    var quad = array<vec2<f32>, 6>(
        // CW Winding
        // 1st triangle (x,y)
        vec2f( -1.0, 1.0),  // Left, Top
        vec2f( 1.0, -1.0),  // Right, Bottom
        vec2f( -1.0, -1.0), // Left, Bottom

        // 2nd triangle
        vec2f( -1.0, 1.0),  // Left, Top
        vec2f( 1.0, 1.0),  // Right, Top
        vec2f( 1.0, -1.0),  // Right, Bottom
    );

    /*
    The matching UV values for the quad map from 0 to 1 as so.
    0,0 ------------------- 1,0
        |                     |
        |                     |
        |                     |
        |                     |
        |                     |
        |                     |
    0,1 ------------------  1,1    
    */
    var uvs = array<vec2<f32>, 6>(
        vec2<f32>( 0.0, 0.0),  // Left, Top
        vec2<f32>( 1.0, 1.0),  // Right, Bottom
        vec2<f32>( 0.0, 1.0), // Left, Bottom

        // 2nd triangle
        vec2<f32>( 0.0, 0.0),  // Left, Top
        vec2<f32>( 1.0, 0.0),  // Right, Top
        vec2<f32>( 1.0, 1.0),  // Right, Bottom
    );

    var out: VertexOutput;
    out.pos = vec4<f32>(quad[in.vertex_index], 0.0, 1.0);
    out.uv = uvs[in.vertex_index];

    return out;
}

@fragment
fn fs_main(in: VertexOutput) -> @location(0) vec4<f32> {
  return vec4<f32>(1, 0.1, 0.1, 0.5);
}