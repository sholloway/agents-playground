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
    0 ---*----------> W

    For the horizontal axis, we map to [-1,1]
          x
    -1 ---*----------> 1

        x = (2t/W) - 1
    
    and to go the other way
        t = W*(x+1)/2

    For the vertical axis, we map to [1, -1]
         y
    1 ---*----------> -1

        y  = (2t/-H) + 1

    and to go the other way...
        t = -H * (y-1)/2

    So to place a quad where ever we want, we just map the 
    viewport coordinates to screen space.

    NOTE: At the moment (7/30/24) wgpu doesn't allow a const array to be indexed by a var.
    However the spec does allow this so I assume that will change in a future release.
    When that happens, move this to be declared at the module level as a constant.
    Tracking issue at: https://github.com/gfx-rs/wgpu/issues/4337

    // Quad that covers the entire viewport.
    var generic_quad = array<vec2<f32>, 6>(
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
*/

/*
Converts from viewport space (pixels) to the horizontal screen space (-1,1)
    x = (2t/W) - 1

Parameters:
    t: The horizontal location in the viewport (pixels).
    width: The width of the viewport (pixels).
*/
fn x_to_screen(t: i32, width: i32) -> f32{
    return f32(((2 * t)/width) - 1);
}

/*
Converts from viewport space (pixels) to the vertical screen space (1,-1)
    y  = (2t/-H) + 1

Parameters:
    t: The vertical location in the viewport (pixels).
    height: The width of the viewport (pixels).
*/
fn y_to_screen(t: i32, height: i32) -> f32{
    return f32((2*t/-height) + 1);
    // Is it possible do do an assertion? Like can I assert that the result is in the range [1,-1]
}

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
    //Upper left Corner
    x: f32,
    y: f32,

    //Lower Right Corner
    xx: f32,
    yy: f32,
}

@group(0) @binding(0) 
var<uniform> viewport: Viewport;

@vertex
fn vs_main(in: VertexInput) -> VertexOutput {
    // Assume that the desired position and size will be passed in as a uniforms.
    // Use the Upper Left Corner for the placement of the overlay.
    // In viewport coordinates (pixels)
    let overlay_config = OverlayPlacement(100, 100, 150, 100);
    let quad_config = ScreenSpaceRect(
        x_to_screen(overlay_config.loc_x, viewport.width), 
        y_to_screen(overlay_config.loc_y, viewport.height), 
        x_to_screen(overlay_config.loc_x + overlay_config.width, viewport.width), 
        y_to_screen(overlay_config.loc_y + overlay_config.height, viewport.height));

    var quad = array<vec2<f32>, 3>(
        // CW Winding
        // 1st triangle (x,y)
        vec2f( quad_config.x, quad_config.y),   // Left, Top
        vec2f( quad_config.xx, quad_config.yy), // Right, Bottom
        vec2f( quad_config.x, quad_config.yy),  // Left, Bottom

        // 2nd triangle
        // vec2f( -1.0, 1.0),  // Left, Top
        // vec2f( 1.0, 1.0),  // Right, Top
        // vec2f( 1.0, -1.0),  // Right, Bottom
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
        vec2<f32>( 0.0, 1.0),  // Left, Bottom

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