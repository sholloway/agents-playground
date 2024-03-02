struct Camera {
  projection: mat4x4<f32>,
  view: mat4x4<f32>
};

@group(0) @binding(0) 
var<uniform> camera: Camera;

@group(1) @binding(0) 
var<uniform> model: mat4x4<f32>;

struct VertexInput {
  @location(0) position: vec4<f32>, 
};

struct VertexOutput {
  @builtin(position) position : vec4<f32>,
};

@vertex
fn vs_main(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  // BUG: Something is wrong with this projection. Probably haven't bound the camera or model correctly.
  output.position = camera.projection * camera.view * model * input.position;
  return output;
}

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  var surface_color: vec4<f32>;
  surface_color = vec4<f32>(1.0, 1.0, 0.0, 1.0);
  return surface_color;
}