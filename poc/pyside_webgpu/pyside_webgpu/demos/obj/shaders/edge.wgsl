struct Camera {
  projection : mat4x4<f32>,
  view : mat4x4<f32>
};

@group(0) @binding(0) 
var<uniform> camera: Camera;

@group(1) @binding(0) 
var<uniform> model: mat4x4<f32>;

struct VertexInput {
  @location(0) position : vec4<f32>, 
  @location(1) normal : vec3<f32>,
};

struct VertexOutput {
  @builtin(position) position : vec4<f32>,
  @location(0) normal : vec3<f32>,
};

@vertex
fn vs_main(input : VertexInput) -> VertexOutput {
  var output : VertexOutput;
  output.position = camera.view * model * input.position;
  output.normal = normalize((camera.view * model * vec4<f32>(input.normal[0], input.normal[1], input.normal[2], 0f)).xyz);
  return output;
}

let lightDir = vec3<f32>(0.25, 0.5, 1f);
let lightColor = vec3<f32>(1f, 1f, 1f);
let ambientColor = vec3<f32>(0.1, 0.1, 0.1);

@fragment
fn fs_main(input : VertexOutput) -> @location(0) vec4<f32> {
  //Return black for where a line should be...
  return vec4<f32>(0f, 0f, 0f, 1f);
}