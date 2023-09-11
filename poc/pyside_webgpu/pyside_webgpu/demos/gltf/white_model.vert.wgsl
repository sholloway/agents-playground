struct Camera {
  projection : mat4x4f,
  view : mat4x4f,
  position : vec3f,
  time : f32,
};
@group(0) @binding(0) var<uniform> camera : Camera;
@group(1) @binding(0) var<uniform> model : mat4x4f;

struct VertexInput {
  @location(0) position : vec3f,
  @location(1) normal : vec3f,
};

struct VertexOutput {
  @builtin(position) position : vec4f,
  @location(0) normal : vec3f,
};

@vertex
fn vertexMain(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  output.position = camera.projection * camera.view * model * vec4f(input.position, 1);
  output.normal = normalize((camera.view * model * vec4f(input.normal, 0)).xyz);
  return output;
}