/*
Draw a quad in screen space and color it a solid color.

Note that the Quad is mapped to screen space, which is: 
    -1,1-------------------1,1
        |                     |
        |                     |
        |                     |
        |         0,0         |
        |                     |
        |                     |
    -1,-1------------------1,-1    

    The viewport is:
    0,0 --------------------W,0
        |                     |
        |                     |
        |                     |
        |         0,0         |
        |                     |
        |                     |
    0,H --------------------W,H

    To map from a generic range of [0, L]
        t
    0---*---------->L

    To [-1,1]
         x
    -1---*---------->1

    x = 2t/L - 1
    and to go the other way
    t = L*(x+1)/2

    So to place a quad where ever we want, we just map the 
    viewport coordinates to screen space.

    NOTE: At the moment (7/30/24) wgpu doesn't allow a const array to be indexed by a var.
    However the spec does allow this so I assume that will change in a future release.
    When that happens, move this to be declared at the module level as a constant.
    Tracking issue at: https://github.com/gfx-rs/wgpu/issues/4337
*/

struct VertexInput {
    @builtin(vertex_index) vertex_index : u32,
};

struct VertexOutput {
    @builtin(position) pos: vec4<f32>,
    @location(0) uv : vec2<f32>,
};

struct Viewport{
    width: i32,
    height: i32 
}

struct OverlayPlacement{
    loc_x: i32,
    loc_y: i32,
    width: i32,
    height: i32
}

struct ScreenSpaceRect{
    loc_x: f32,
    loc_y: f32,
    width: f32,
    height: f32
}

@group(0) @binding(0) 
var<uniform> viewport: Viewport;

/*
Converts from viewport space (pixels) to screen space (-1,1)
x = 2t/L - 1
*/
fn to_screen(t: i32, scaling_factor: i32) -> f32{
    return ((2 * t)/scaling_factor) - 1;
}

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    // Assume that the desired position and size will be passed in as a uniforms.
    // Use the Upper Left Corner for the placement of the overlay.
    // In viewport coordinates (pixels)
    let overlay_config = OverlayPlacement(50, 20, 150, 100);
    let proj_overlay_config = ScreenSpaceRect(
        to_screen(overlay_config.loc_x, viewport.width), 
        to_screen(overlay_config.loc_y, viewport.height), 
        to_screen(overlay_config.width, viewport.width), 
        to_screen(overlay_config.height, viewport.height));

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
  return vec4<f32>(0, 1, 0, 0.75);
}